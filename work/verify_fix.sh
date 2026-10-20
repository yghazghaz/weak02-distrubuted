#!/usr/bin/env bash
# SCx61 Week 2 - Lab Step 9 ("Fix It" / "Verify It").
# Runs YOUR img_mpi_v2_halo.py (the Sendrecv version) on the SAME 8192-wide
# image that hung in break_deadlock.sh, then compares the result with the
# serial oracle.
#
# Run it INSIDE node0 as student, from the work folder:
#     bash verify_fix.sh
# Expected: it finishes, and compare.py prints 0 differing pixels.
set -uo pipefail
cd "$(dirname "$0")"

WIDTH=8192
HEIGHT=300
PREFIX="break_${WIDTH}"
OUT="${PREFIX}_out_v2"

if [ ! -f "${PREFIX}.npy" ]; then
    echo "=== ${PREFIX}.npy not found - generating it ==="
    python3 make_test_image.py --width "$WIDTH" --height "$HEIGHT" --out-prefix "$PREFIX" || exit 1
fi

echo "=== Running img_mpi_v2_halo.py on the ${WIDTH}-wide image (60s limit) ==="
timeout 60 mpirun --hostfile hostfile -n 6 python3 img_mpi_v2_halo.py "$PREFIX" "$OUT"
rc=$?
if [ "$rc" -eq 124 ]; then
    echo "=== Still hangs (timeout). Your fix is not complete yet. ==="
    exit 1
elif [ "$rc" -ne 0 ]; then
    echo "=== mpirun failed with exit code ${rc} - read the error above. ==="
    exit "$rc"
fi

echo "=== Building the serial oracle for this image ==="
python3 -c "
import numpy as np
from filter_ref import box_blur_3x3
np.save('${PREFIX}_serial.npy', box_blur_3x3(np.load('${PREFIX}.npy')))
"

echo "=== Comparing with the serial oracle (target: 0 differing pixels) ==="
python3 compare.py --serial-prefix "${PREFIX}_serial" --candidate "$OUT"
