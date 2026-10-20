# SCx61 Week 2 — Debugging Guide (Break It → Debug It → Fix It)

**Read this only after you have watched the hang with your own eyes (`bash break_deadlock.sh 20`).**

All commands below run **inside node0, as `student`, from the work folder**:

```bash
docker compose exec -u student -w /home/student/work node0 bash
```

## What you should have just seen

- Six lines `[rank N on nodeX] before Send`, and then silence.
- No error. No crash. After 20 seconds `timeout` killed the job.
- In a second terminal: `docker compose ps` still says `Up (healthy)` for all three nodes.


> **Who sent that log line?** If you run `docker compose logs`, you may see lines repeating every ~20 s such as
> `Unable to negotiate with 127.0.0.1 ... no matching host key type found. Their offer: sk-...`.
> Look at the source: `127.0.0.1` inside the container is the **healthcheck probing sshd itself**. It is not your MPI job and not the cause of the hang. Before you decide what a message means, decide who emitted it.

A healthy cluster that runs a program which never finishes. The bug is not in Docker, and not in the launch. Your job is to prove where it is, with evidence.

## The rule for this step: evidence before guessing

1. **Write down 3 hypotheses** for why it hangs (10 minutes, on paper, no AI, no code changes).
2. For each hypothesis, write **one command** that would confirm or reject it, and **what output would confirm / reject it**.
3. Run the commands. Keep the real output.

Checks you should be able to run:

| Check | Command | What it tells you |
|---|---|---|
| Is the cluster healthy? | `docker compose ps` (from your host, in `lab/config`) | Containers are fine, so this is not a Docker problem |
| Does launching work at all? | `mpirun --hostfile hostfile -n 6 hostname` | 3 distinct hostnames, 2 each means SSH, DNS and mpirun are fine |
| How far did each rank get? | read the `before Send` / `after Send` markers | Where exactly are they stuck? Is it one rank or all of them? |
| Does a small image work? | `python3 make_test_image.py --width 256 --height 300 --out-prefix small256` then run v3 on `small256` | Does the same code succeed on small data? What does that tell you? |
| Is the small case really safe? | replace every `comm.Send(` with `comm.Ssend(` in a COPY of v3 and run it on `small256` (with `timeout 20`) | What changes? Why? |

Then read `img_mpi_v3_naive_halo.py` and point at the exact lines responsible.

## AI-assisted debugging, Round 1

Only after you have your own evidence. Fill this template with **your real output** (not mine, not a classmate's):

```
I'm running a 3-container Docker Compose cluster (node0, node1, node2) and
launch: mpirun --hostfile hostfile -n 6 python3 img_mpi_v3_naive_halo.py
from node0, with mpi4py on Open MPI 4.1.4. All containers are Up (healthy).

Expected: the job finishes and writes an output file.
Actual: <what you saw>. No error message.
Small image (width 256): <what happened>. Large image (width 8192): <what happened>.

Evidence:
<paste: docker compose ps, the hostname test, the before/after Send output>

Relevant code:
<paste the Send / Recv section of v3>

Give me: 1) your top 2-3 hypotheses, ranked; 2) one command per hypothesis to
confirm or reject it; 3) the exact output that would confirm vs reject each;
4) the smallest fix (not a rewrite); 5) one command that proves the fix worked.
Do not say "check your MPI setup".
```

Compare the AI's hypotheses with yours. Where did they differ? Which of its commands did you actually run?

## AI-assisted debugging, Round 2: catch the AI being wrong

An AI assistant answered with the text below. Test **each** of the three claims on your cluster and decide, using real command output, whether it is VERIFIED, REFUTED, or HIDES THE SYMPTOM.

> *"I see the problem. This is one of three things:*
>
> ***Claim A:** Docker's internal DNS/networking is flaky between containers — the ranks can't reliably reach each other. Restart Docker (`systemctl restart docker` or `docker compose down && docker compose up -d`) and it should clear up.*
>
> ***Claim B:** `sshd` isn't actually reachable on the worker nodes, so `mpirun` can't launch the remote ranks in the first place — that's why nothing completes.*
>
> ***Claim C:** The underlying issue is that your messages are too big for MPI's default internal buffering. Raise the eager-send limit — `--mca btl_vader_eager_limit 16384` (or the TCP equivalent, `btl_tcp_eager_limit`, for cross-node traffic) — so the messages fit in the buffer and `Send` can return immediately instead of blocking. That will fix it."*

Fill in your own table. A verdict without a command and its real output does not count.

| Claim | Verdict (VERIFIED / REFUTED / HIDES THE SYMPTOM) | The command whose output proves it |
|---|---|---|
| A | | |
| B | | |
| C | | |

Hint for C: a fix is only a fix if it survives a bigger input, or a stricter test. Try both.

### Toolbox for Round 2 (commands, not answers)

```bash
# A. does launching work, independent of the image job?
mpirun --hostfile hostfile -n 6 hostname

# C-1. same program, raised eager limit, at the width that hung
#      (reuses break_8192.npy created by break_deadlock.sh)
timeout 30 mpirun --mca btl_vader_eager_limit 16384 --hostfile hostfile -n 6 \
    python3 img_mpi_v3_naive_halo.py break_8192 claimc_8192_out
echo "exit code: $?"          # 0 = finished, 124 = killed by timeout (hung)

# C-2. same flag, bigger image
python3 make_test_image.py --width 20000 --height 300 --out-prefix claimc_20000
timeout 30 mpirun --mca btl_vader_eager_limit 16384 --hostfile hostfile -n 6 \
    python3 img_mpi_v3_naive_halo.py claimc_20000 claimc_20000_out
echo "exit code: $?"

# C-3. stricter test: Send -> Ssend (synchronous send) on a COPY, at the SMALL width
sed 's/comm\.Send(/comm.Ssend(/g' img_mpi_v3_naive_halo.py > v3_ssend_test.py
python3 make_test_image.py --width 256 --height 300 --out-prefix small256
timeout 20 mpirun --hostfile hostfile -n 6 python3 v3_ssend_test.py small256 small256_ssend_out
echo "exit code: $?"
```

From the host (not inside node0), for Claim A and B evidence: `docker network inspect scx61-week1_clusternet`, and from node0: `ssh node1 hostname`.

### Who is allowed to say what

A section number in the MPI Standard differs between versions (MPI-3.1 and MPI 4.1 number the same chapter differently). When you cite the Standard, cite the **section title and the version**, for example: MPI 4.1, "Communication Modes".

## Fix it and prove it

Your `img_mpi_v2_halo.py` already does the exchange with `Sendrecv`. Prove it handles the image that hung:

```bash
bash verify_fix.sh
```

You want: it finishes, and `compare.py` prints **0 differing pixels**. Run it three times in a row. Then run one unrelated check that Week 1 is not broken: `ssh node1 hostname` from node0.
