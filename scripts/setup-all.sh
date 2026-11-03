#!/usr/bin/env bash
# One-time setup of this repository's environment (runs as the codespace postCreateCommand).
#   1. ETRI 0.5 um open-source design kit + official PDK 260820 files (models, rule decks)
#   2. official SPICE models copied to designs/etri050/sim/models (git-ignored, PDK files are not committed)
#   3. qflow / graywolf / qrouter / tcsh for the digital control block (no root needed)
# A failed qflow build does not stop the rest; rerun: bash scripts/install-qflow-etri050.sh
set -uo pipefail

WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ETRI050_WITH_DOCS="${ETRI050_WITH_DOCS:-1}"

bash "$WS/scripts/setup-etri050.sh" || { echo "[setup] design kit setup failed"; exit 1; }
bash "$WS/scripts/get-models.sh" || echo "[setup] official models not extracted (see above)"
bash "$WS/scripts/install-qflow-etri050.sh" || echo "[setup] qflow install failed - rerun: bash scripts/install-qflow-etri050.sh"
echo "[setup] done. Check the environment: bash scripts/smoke-test.sh"
