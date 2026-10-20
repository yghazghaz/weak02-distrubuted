from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# تحديد الجيران
top_neighbor = rank - 1 if rank > 0 else MPI.PROC_NULL
bottom_neighbor = rank + 1 if rank < size - 1 else MPI.PROC_NULL

# نفترض عندك بيانات للإرسال لأعلى وأسفل (أو يمين ويسار)
send_top = np.ascontiguousarray(top_halo_data)
recv_bottom = np.empty_like(send_top)

print(f"[rank {rank}] before Send", flush=True)

# الاستخدام الصحيح لـ Sendrecv بحيث الإرسال والاستقبال متبادلين بين الجيران
comm.Sendrecv(
    sendbuf=send_top, dest=top_neighbor, sendtag=101,
    recvbuf=recv_bottom, source=bottom_neighbor, recvtag=101
)