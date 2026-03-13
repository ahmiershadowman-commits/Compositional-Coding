#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.csp_runtime.simulation import run_frontier_audit

if __name__ == '__main__':
    results = run_frontier_audit()
    print('# Frontier Audit')
    for r in results:
        print(f'- {r.scenario}: top={r.top_skill}, preflight={r.preflight_status}, next={r.next_action}, failures={r.failure_modes}')
