# SCx61 Week 2 - Submission

Name: ______________________    Date: ____________

A claim without evidence does not count. For EVERY failure or fix you claim below, attach:
- the exact command you ran,
- the real output (pasted as text, or a screenshot), and
- one line saying who produced any error/warning you quote (your program? mpirun? Docker? the healthcheck?).

## 1. The build
- [ ] Output of `mpirun --hostfile hostfile -n 6 hostname` (6 lines, 3 hostnames).
- [ ] Output of `python3 compare.py --candidate test_image_filtered_v1` (the seam rows).
- [ ] Output of `python3 compare.py --candidate test_image_filtered_v2` (0 differing pixels).

## 2. The failure (screenshot required)
- [ ] Screenshot of `bash break_deadlock.sh 20` hanging and ending with `CONFIRMED HANG`.
- [ ] Screenshot (or pasted output) of `docker compose ps` taken WHILE it hangs.
- [ ] Your 3 hypotheses, each with the command that would confirm/reject it and the output you got.
- [ ] Which lines of `img_mpi_v3_naive_halo.py` are responsible, in your own words.

## 3. AI Round 1 (paste verbatim, do not edit)
- [ ] The exact prompt you sent (with YOUR real output filled in).
- [ ] The AI's full response, copied as-is. Name of the assistant: ____________
- [ ] Which of its commands you actually ran, with the real output.
- [ ] Where its hypotheses differed from yours.

## 4. AI Round 2
| Claim | Verdict | Command | Real output (paste) |
|---|---|---|---|
| A | | | |
| B | | | |
| C (run at 8192 AND at a bigger width or with Ssend) | | | |

## 5. Fix and verify
- [ ] `bash verify_fix.sh` output, three runs, each ending with 0 differing pixels.
- [ ] `ssh node1 hostname` from node0 (Week 1 still works).

## 6. Knowledge check
Answer the six questions at the end of student_checklist.md in full sentences.
