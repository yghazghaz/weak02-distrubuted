#!/usr/bin/env python3
"""
SCx61 Week 2 — "Break It" (Lab Step 7). THIS VERSION IS DELIBERATELY
UNSAFE. Run it with break_deadlock.sh, watch what happens, and THEN read
this file carefully and find the lines responsible.

Same row-strip decomposition and halo-exchange idea as your
img_mpi_v2_halo.py, but the exchange is written with separate blocking
`Send` and `Recv` calls instead of `Sendrecv`.

Usage (same as v1/v2):
    mpirun --hostfile hostfile -n 6 python3 img_mpi_v3_naive_halo.py [in_prefix] [out_prefix]
"""
import socket
import sys
import numpy as np
from mpi4py import MPI

IN_PREFIX = "test_image"
OUT_PREFIX = "test_image_filtered_v3"

TAG_SCATTER_SHAPE = 10
TAG_SCATTER_DATA = 11
TAG_GATHER_SHAPE = 20
TAG_GATHER_DATA = 21
TAG_UP = 100    # a rank sending ITS OWN top row, to its top neighbor
TAG_DOWN = 101  # a rank sending ITS OWN bottom row, to its bottom neighbor


def box_blur_3x3(img: np.ndarray) -> np.ndarray:
    padded = np.pad(img.astype(np.float64), pad_width=1, mode="edge")
    acc = np.zeros_like(img, dtype=np.float64)
    h, w = img.shape
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            acc += padded[1 + dy: 1 + dy + h, 1 + dx: 1 + dx + w]
    acc /= 9.0
    return np.clip(acc, 0, 255).astype(np.uint8)


def split_rows(height: int, n: int):
    base = height // n
    extra = height % n
    bounds = []
    start = 0
    for i in range(n):
        rows = base + (1 if i < extra else 0)
        bounds.append((start, start + rows))
        start += rows
    return bounds


def filter_with_halo(strip: np.ndarray, top_halo: np.ndarray, bottom_halo: np.ndarray) -> np.ndarray:
    extended = np.vstack([top_halo[None, :], strip, bottom_halo[None, :]])
    filtered_extended = box_blur_3x3(extended)
    core_rows = strip.shape[0]
    return filtered_extended[1:1 + core_rows, :]


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    hostname = socket.gethostname()

    in_prefix = sys.argv[1] if len(sys.argv) > 1 else IN_PREFIX
    out_prefix = sys.argv[2] if len(sys.argv) > 2 else OUT_PREFIX

    if rank == 0:
        img = np.load(f"{in_prefix}.npy")
        height, width = img.shape
        bounds = split_rows(height, size)
        my_start, my_end = bounds[0]
        my_strip = img[my_start:my_end, :].copy()
        for worker in range(1, size):
            w_start, w_end = bounds[worker]
            strip = img[w_start:w_end, :].copy()
            comm.send(strip.shape, dest=worker, tag=TAG_SCATTER_SHAPE)
            comm.Send(strip, dest=worker, tag=TAG_SCATTER_DATA)
        width_for_halo = width
    else:
        shape = comm.recv(source=0, tag=TAG_SCATTER_SHAPE)
        my_strip = np.empty(shape, dtype=np.uint8)
        comm.Recv(my_strip, source=0, tag=TAG_SCATTER_DATA)
        width_for_halo = shape[1]

    # ------------------------------------------------------------
    # Halo exchange, version 3. The print markers show how far each
    # rank gets - use them as evidence when you debug.
    # ------------------------------------------------------------
    print(f"[rank {rank} on {hostname}] before Send", flush=True)

    if rank > 0:
        comm.Send(my_strip[0, :].copy(), dest=rank - 1, tag=TAG_UP)
    if rank < size - 1:
        comm.Send(my_strip[-1, :].copy(), dest=rank + 1, tag=TAG_DOWN)

    print(f"[rank {rank} on {hostname}] after Send", flush=True)

    top_halo = np.empty(width_for_halo, dtype=np.uint8)
    bottom_halo = np.empty(width_for_halo, dtype=np.uint8)

    if rank > 0:
        comm.Recv(top_halo, source=rank - 1, tag=TAG_DOWN)
    else:
        top_halo = my_strip[0, :].copy()

    if rank < size - 1:
        comm.Recv(bottom_halo, source=rank + 1, tag=TAG_UP)
    else:
        bottom_halo = my_strip[-1, :].copy()

    print(f"[rank {rank} on {hostname}] after Recv", flush=True)

    my_filtered = filter_with_halo(my_strip, top_halo, bottom_halo)

    if rank == 0:
        result = np.zeros_like(img)
        result[my_start:my_end, :] = my_filtered
        for worker in range(1, size):
            w_start, w_end = bounds[worker]
            shape = comm.recv(source=worker, tag=TAG_GATHER_SHAPE)
            buf = np.empty(shape, dtype=np.uint8)
            comm.Recv(buf, source=worker, tag=TAG_GATHER_DATA)
            result[w_start:w_end, :] = buf
        np.save(f"{out_prefix}.npy", result)
        print(f"[rank 0 on {hostname}] wrote {out_prefix}.npy", flush=True)
    else:
        comm.send(my_filtered.shape, dest=0, tag=TAG_GATHER_SHAPE)
        comm.Send(my_filtered, dest=0, tag=TAG_GATHER_DATA)


if __name__ == "__main__":
    main()
