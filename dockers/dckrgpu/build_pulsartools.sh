#!/bin/bash
set -euo pipefail

TMPDIR_BASE="/datax2/tmp"
DEF_FILE="dckrgpu.def"
OUTPUT="pulsartools.sif"

mkdir -p "$TMPDIR_BASE"
chmod 777 "$TMPDIR_BASE"

echo ">>> Using temporary directory: $TMPDIR_BASE"
echo ">>> Building Singularity image from $DEF_FILE -> $OUTPUT"

sudo SINGULARITY_TMPDIR="$TMPDIR_BASE" singularity build "$OUTPUT" "$DEF_FILE"

echo ">>> Build finished: $OUTPUT"