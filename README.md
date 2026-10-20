# SCx61 Week 2 Lab — Rank, Send, Recv (and the deadlock hiding in both)

You turn the Week 1 cluster into a working MPI cluster and use it to filter one image across 6 processes on 3 nodes.

```
PREDICT → BUILD → RUN → OBSERVE → BREAK → DEBUG → FIX → VERIFY
```

Write your prediction **before** every run. The lab is comparing your prediction with the real output.

## What's in this folder

```
lab/
├── README.md              ← you are here
├── student_checklist.md   ← tick items as you go
├── config/
│   └── compose.yaml       ← the cluster (complete — nothing to fill in)
├── source_code/
│   ├── Dockerfile         ← node image (Week 1 + Open MPI, NumPy, Pillow, mpi4py)
│   └── entrypoint.sh      ← runs by itself on container start
└── work/                  ← YOUR folder: shared by all 3 nodes
    ├── hostfile
    ├── make_test_image.py, filter_ref.py, compare.py
    └── hello_mpi.py, img_mpi_v1_nohalo.py, img_mpi_v2_halo.py   ← you complete these (TODOs)
```

More files (for the "Break It" step) arrive from your TA during the session as a small zip called `SCx61_Week02_BreakKit_v3.zip`. Instructions for it are in section 6.

## 1. Start the cluster (do this before the session)

Docker Desktop must be running. In a terminal:

```bash
cd lab/config
docker compose up -d --build
docker compose ps
```

The first build downloads Open MPI and takes a few minutes. Wait until `docker compose ps` shows **node0, node1, node2 all `Up (healthy)`**.

> Still have the Week 1 cluster running? That is fine — this uses the same project name, so Compose simply replaces it. Always run `docker compose` from **this** `lab/config` folder (it has the Week 2 `compose.yaml`).

Apple Silicon (M1/M2/M3) Mac: this has not been tested on that hardware. If the build fails, send your TA a screenshot of the error.

## 2. Check the shared folder (10 seconds)

```bash
docker compose exec -u student node0 bash -c "touch /home/student/work/perm_test && echo OK"
docker compose exec node1 ls /home/student/work/perm_test
docker compose exec node0 rm /home/student/work/perm_test
```

You should see `OK`, then the file name. If any command errors, go to **Troubleshooting** below.

## 3. Enter the cluster

**Every MPI command in this lab runs inside node0, as `student`, in the work folder.** One command gets you there:

```bash
docker compose exec -u student -w /home/student/work node0 bash
```

Your prompt now looks like `student@node0:~/work$`. Everything below is typed there. (`exit` leaves node0.)

Edit the `.py` files on your own machine (VS Code, in `lab/work/`). Saved changes show up inside all three nodes instantly.

## 4. The commands you will use

```bash
mpirun --version
mpirun --hostfile hostfile -n 6 hostname                  # 6 lines, 3 hostnames, 2 each

mpirun --hostfile hostfile -n 6 python3 hello_mpi.py      # after you complete the 3 TODOs

python3 make_test_image.py --width 512 --height 300 --out-prefix test_image
python3 -c "import numpy as np; from filter_ref import box_blur_3x3; np.save('test_image_filtered_serial.npy', box_blur_3x3(np.load('test_image.npy')))"

mpirun --hostfile hostfile -n 6 python3 img_mpi_v1_nohalo.py
python3 compare.py --candidate test_image_filtered_v1

mpirun --hostfile hostfile -n 6 python3 img_mpi_v2_halo.py
python3 compare.py --candidate test_image_filtered_v2
```

These run **your** files. The files with `TODO` need your code before they work.

## 5. Running scripts: always `bash name.sh`

When a `.sh` file is unzipped on Windows it loses its "executable" flag, so `./name.sh` can fail with `Permission denied`. Always start scripts with `bash`:

```bash
bash break_deadlock.sh 20      # right
./break_deadlock.sh 20         # may fail - do not use
```

## 6. The Break Kit (you receive it during the session)

The kit zip has **no top-level folder**. Extract it **into your existing `lab/` folder** (the one containing `config/`, `source_code/` and `work/`). Afterwards these files must exist:

```
lab/debugging.md
lab/SUBMISSION.md
lab/work/img_mpi_v3_naive_halo.py
lab/work/break_deadlock.sh
lab/work/verify_fix.sh
```

Check from the `lab/` folder: `ls work/break_deadlock.sh` (Windows PowerShell: `dir work\break_deadlock.sh`). If it says "not found", you extracted one level too deep or too high - move the files.

## 7. If the build cannot download packages (no internet / proxy)

`docker compose up -d --build` needs to download Open MPI. If it fails with network or apt errors, do not keep retrying: tell your TA. The TA can give you a pre-built image file (`scx61_week2_image.tar.gz`). The steps then are:

```bash
docker load -i scx61_week2_image.tar.gz
cd lab/config
docker compose up -d          # NOTE: no --build
docker compose ps             # wait for 3 x Up (healthy)
```

## Troubleshooting (the things that actually happen)

| What you see | What it means | Fix |
|---|---|---|
| `docker compose up` says no configuration file / `compose.yaml` not found | Wrong folder | `cd lab/config` first |
| `docker compose ps` shows fewer than 3 nodes or `starting` for a long time | Still building / starting | Wait 30–60 s and run `docker compose ps` again |
| `mpirun` says it cannot run as root | You entered without `-u student` | `exit`, then use the command from section 3 |
| `mpirun`: "unable to open the hostfile" or "No such file" | You are not in the work folder, or the shared folder is not mounted | Use the section 3 command (it starts in the right folder). Check `ls` shows `hostfile`. |
| `touch: Permission denied` on the shared folder, or files owned by `root` | Windows/Mac file-sharing quirk | Tell your TA — it has a fallback |
| `bash: ...: $'\r': command not found` or `/usr/bin/env: 'bash\r'` | A file was saved with Windows line endings | In node0: `sed -i 's/\r$//' <file>` (or in VS Code click `CRLF` at the bottom bar and pick `LF`) |
| Build fails with network/apt errors | No internet at build time | Section 7: ask your TA for the offline image |
| `docker compose logs` shows repeating sshd lines about `127.0.0.1` (for example "Unable to negotiate ... no matching host key type") | That is the Docker **healthcheck** probing sshd from inside the container. It is not your MPI job and not the cause of any hang | Ignore it. Before you decide what a log line means, decide **who emitted it** |
| `Permission denied` when running `./something.sh` | `.sh` files lose the executable flag on Windows | Use `bash something.sh` |

If something else breaks: copy the **exact** error, write what you expected vs. what happened, and show your TA. That is also the first step of the debugging method this course teaches.

## Tear down

```bash
docker compose down          # from lab/config
```

Your files in `lab/work/` stay on your machine.
# weak02-distrubuted
