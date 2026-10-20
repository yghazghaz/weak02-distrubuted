# SCx61 Week 2 — Student Checklist

Tick a box only after you have run the command and seen the real output — not when the code merely "looks right".

All MPI commands run **inside node0**: `docker compose exec -u student -w /home/student/work node0 bash` (run from `lab/config`).

## Setup (before the session)
- [ ] From `lab/config`: `docker compose up -d --build`
- [ ] `docker compose ps` shows `node0`, `node1`, `node2` all `Up (healthy)`
- [ ] Shared-folder check from the README (section 2) printed `OK` and the file name
- [ ] Inside node0: `mpirun --version` prints an Open MPI version

## Steps 1–3: Predict, build, run `hello_mpi.py`
- [ ] Wrote down a prediction for what a 6-rank launch prints (how many lines? same or different? which nodes?)
- [ ] Completed the 3 TODOs in `hello_mpi.py`
- [ ] `mpirun --hostfile hostfile -n 6 python3 hello_mpi.py` prints 6 lines
- [ ] Marked which hostname each rank printed — did it match my prediction?

## Step 4: Send / Recv concepts
- [ ] Can explain `send`/`recv` (lowercase) vs `Send`/`Recv` (uppercase) in my own words
- [ ] Predicted what happens when the sender's tag does not match the receiver's tag

## Step 5: Strips, no halo
- [ ] Completed the TODOs in `img_mpi_v1_nohalo.py`
- [ ] Predicted whether the result will equal the serial oracle exactly
- [ ] Generated the test image: `python3 make_test_image.py --width 512 --height 300 --out-prefix test_image`
- [ ] Created `test_image_filtered_serial.npy` (the serial oracle command in the README)
- [ ] Ran v1 on 6 ranks
- [ ] `compare.py --candidate test_image_filtered_v1` — found the differing row ranges myself, **before** looking at the slide

## Step 6: Halo exchange
- [ ] Completed the `halo_exchange()` TODOs in `img_mpi_v2_halo.py` with `comm.Sendrecv`
- [ ] Ran v2 on 6 ranks
- [ ] `compare.py --candidate test_image_filtered_v2` reports **0 differing pixels**

## Step 7: Break it (new files arrive from your TA)
- [ ] Unzipped the Break Kit INTO `lab/`; `ls work/break_deadlock.sh` finds the file
- [ ] Read `img_mpi_v3_naive_halo.py`; can point to the lines where every rank sends before it receives
- [ ] Predicted what happens with a much wider image
- [ ] Ran `bash break_deadlock.sh 20` and watched it hang
- [ ] In a second terminal, `docker compose ps` still shows everything healthy WHILE it hangs

## Step 8: Debug it — evidence first, before any AI
- [ ] Wrote 3 hypotheses, each with a command and the output that would confirm or reject it
- [ ] `mpirun --hostfile hostfile -n 6 hostname` still works (launching is fine)
- [ ] Every rank printed `before Send`; none printed `after Send`
- [ ] Re-ran at a small width and it completed
- [ ] (Recommended) `Send` → `Ssend` in a copy of v3, ran at the small width — what happened, and what does that prove?

## Step 8b: AI Debugging, Round 1
- [ ] Filled the prompt template in `debugging.md` with MY OWN real output
- [ ] Compared the AI's hypotheses with mine; ran at least one of its commands myself

## Step 8c: AI Debugging, Round 2: catch the AI being wrong
- [ ] Refuted Claim A with a command's real output
- [ ] Refuted Claim B with a command's real output
- [ ] Claim C: ran it at the original failing width — did it complete?
- [ ] Claim C: ran it again at a bigger width (or tried `Ssend`) — what happened?
- [ ] Filled the verdict table, each verdict citing the command that proves it

## Step 9: Fix, verify
- [ ] `bash verify_fix.sh` finishes on the SAME 8192-wide image that hung
- [ ] It reports **0 differing pixels**
- [ ] Ran it 3 times in a row — all 3 succeeded
- [ ] `ssh node1 hostname` from node0 still works (Week 1 not broken)
- [ ] (Challenge) thought through what halo width a "blur then edge detection" pipeline needs, and why

## Knowledge check (write real answers, not one-word guesses)
- [ ] Q1: two different causes of "containers healthy but mpirun hangs", and the output that tells them apart
- [ ] Q2: why did the naive code pass on a small image and hang on a big one — did the small run "prove" it correct?
- [ ] Q3: when does "just raise the eager limit" stop working, and why is it not a fix?
- [ ] Q4: why can't `mpirun` just use `docker compose exec` instead of SSH?
- [ ] Q5: why does a 3×3 filter need exactly one halo row on each side? What changes for 5×5?
- [ ] Q6: why do we run MPI as `student` and not `root`?
