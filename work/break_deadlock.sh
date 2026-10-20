#!/usr/bin/env bash
# SCx61 Week 2 - Lab Step 7 ("Break It").
# Generates a wide test image (8192 x 300) and runs img_mpi_v3_naive_halo.py
# on it with a hard timeout. A hang followed by the timeout is the EXPECTED
# result - that is the point of the exercise.
#
# Run it INSIDE node0 as student, from the work folder:
#     bash break_deadlock.sh 20        (20 = timeout in seconds)
set -euo pipefail

FAILING_WIDTH=8192
HEIGHT=300
PREFIX="break_${FAILING_WIDTH}"
TIMEOUT_SECONDS="${1:-20}"

cd "$(dirname "$0")"

echo "=== Generating ${FAILING_WIDTH}-wide test image ==="
python3 make_test_image.py --width "${FAILING_WIDTH}" --height "${HEIGHT}" --out-prefix "${PREFIX}"

echo "=== Running img_mpi_v3_naive_halo.py with a ${TIMEOUT_SECONDS}s hard timeout ==="
if timeout "${TIMEOUT_SECONDS}" mpirun --hostfile hostfile -n 6 python3 img_mpi_v3_naive_halo.py "${PREFIX}" "${PREFIX}_out_v3"; then
    echo "!!! UNEXPECTED: it completed within ${TIMEOUT_SECONDS}s. Tell your TA and show the output above."
    exit 1
else
    rc=$?
    if [ "${rc}" -eq 124 ]; then
        echo "=== CONFIRMED HANG: mpirun was killed by timeout after ${TIMEOUT_SECONDS}s. ==="
        echo "=== This is the failure you will now debug. Write down your hypotheses BEFORE touching any code. ==="
        exit 0
    else
        echo "!!! mpirun exited with error code ${rc} (an error, not a hang). Tell your TA and show the output above."
        exit "${rc}"
    fi
fi
