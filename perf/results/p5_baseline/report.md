# Bench report: p5_baseline (profile=baseline)

- Runs: 18, SR: 18/18 = 100.0% (Wilson CI [0.82, 1.00])
- T_task p50: 10.3s, mean: 10.7s
- N_steps mean: 3.0
- CDP cmds/run: 131.3, sleep ms/run: 31486.8

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 36 | 3802.5 | 5490.9 | 140844.2 |
| browser.screenshot | 36 | 136.2 | 486.0 | 6111.6 |
| browser.state_request | 54 | 162.7 | 558.7 | 12867.5 |
| cdp.cmd | 2363 | 3.2 | 112.0 | 48817.8 |
| dom.cdp_ax_tree | 54 | 12.1 | 386.7 | 3892.2 |
| dom.cdp_get_all_trees | 54 | 28.3 | 399.7 | 5651.4 |
| dom.get_dom_tree | 54 | 33.7 | 535.0 | 6617.4 |
| dom.get_serialized_dom_tree | 54 | 35.4 | 549.5 | 6787.1 |
| idle.sleep | 1547 | 18.6 | 2166.1 | 566762.0 |
| phase.execute_actions | 36 | 876.5 | 1946.1 | 22646.1 |
| phase.get_next_action | 36 | 2959.3 | 3301.3 | 106877.2 |
| phase.llm_call | 36 | 2959.0 | 3301.1 | 106865.9 |
| phase.multi_act | 54 | 391.0 | 1656.2 | 31828.3 |
| phase.prepare_context | 36 | 260.8 | 544.0 | 11075.8 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | Y | 9.91 | 3 | 12632 | 101 |  |
| search_extract | 1 | Y | 9.76 | 3 | 12632 | 101 |  |
| search_extract | 2 | Y | 10.24 | 3 | 12632 | 101 |  |
| form_fill | 0 | Y | 12.11 | 3 | 12647 | 158 |  |
| form_fill | 1 | Y | 12.26 | 3 | 12647 | 158 |  |
| form_fill | 2 | Y | 12.05 | 3 | 12647 | 158 |  |
| table_paginate | 0 | Y | 13.94 | 4 | 19549 | 119 |  |
| table_paginate | 1 | Y | 14.4 | 4 | 19549 | 119 |  |
| table_paginate | 2 | Y | 13.63 | 4 | 19549 | 119 |  |
| login_flow | 0 | Y | 11.35 | 3 | 12560 | 117 |  |
| login_flow | 1 | Y | 10.43 | 3 | 12560 | 117 |  |
| login_flow | 2 | Y | 10.19 | 3 | 12560 | 117 |  |
| modal_dismiss | 0 | Y | 10.22 | 3 | 12503 | 92 |  |
| modal_dismiss | 1 | Y | 10.29 | 3 | 12503 | 92 |  |
| modal_dismiss | 2 | Y | 9.97 | 3 | 12503 | 92 |  |
| heavy_dom | 0 | Y | 7.15 | 2 | 6854 | 52 |  |
| heavy_dom | 1 | Y | 7.47 | 2 | 6854 | 52 |  |
| heavy_dom | 2 | Y | 7.86 | 2 | 6853 | 52 |  |