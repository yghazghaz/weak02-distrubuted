SCx61 Week 2 - Break Kit v3  (given to you by your TA at the "Break It" step)

HOW TO UNZIP (important):
This zip has NO top-level folder. Extract it INTO your existing lab/ folder
(the one that contains config/, source_code/ and work/), so the files land at:

  lab/debugging.md
  lab/SUBMISSION.md
  lab/work/img_mpi_v3_naive_halo.py
  lab/work/break_deadlock.sh
  lab/work/verify_fix.sh

Check before you continue (from the lab/ folder):   ls work/break_deadlock.sh
(Windows PowerShell:  dir work\break_deadlock.sh)
If that file is not found, you extracted one level too deep or too high. Move it.

Then, from lab/config, enter node0 as student:

  docker compose exec -u student -w /home/student/work node0 bash
  bash break_deadlock.sh 20

Always start the scripts with 'bash' (the executable flag is lost on Windows).
Expected: six 'before Send' lines, silence, then '=== CONFIRMED HANG ... ==='.

Then follow debugging.md. When you finish, fill SUBMISSION.md.
