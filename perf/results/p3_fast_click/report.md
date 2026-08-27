# Bench report: p3_fast_click (profile=baseline)

- Runs: 18, SR: 18/18 = 100.0% (Wilson CI [0.82, 1.00])
- T_task p50: 10.6s, mean: 10.7s
- N_steps mean: 3.0
- CDP cmds/run: 131.3, sleep ms/run: 31312.6

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 36 | 3755.4 | 5327.0 | 139792.5 |
| browser.screenshot | 36 | 142.0 | 462.5 | 6907.7 |
| browser.state_request | 54 | 151.6 | 554.3 | 12903.2 |
| cdp.cmd | 2364 | 3.4 | 113.3 | 80617.4 |
| dom.cdp_ax_tree | 54 | 14.5 | 363.0 | 4255.5 |
| dom.cdp_get_all_trees | 54 | 31.6 | 371.5 | 5264.7 |
| dom.get_dom_tree | 54 | 35.1 | 490.5 | 6187.8 |
| dom.get_serialized_dom_tree | 54 | 35.7 | 507.7 | 6388.6 |
| idle.sleep | 1543 | 17.5 | 2161.0 | 563627.1 |
| phase.execute_actions | 36 | 717.7 | 1819.3 | 21048.6 |
| phase.get_next_action | 36 | 2959.7 | 3300.9 | 106874.0 |
| phase.llm_call | 36 | 2959.4 | 3300.7 | 106863.3 |
| phase.multi_act | 54 | 318.2 | 1554.8 | 30038.4 |
| phase.prepare_context | 36 | 250.9 | 600.8 | 11740.7 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | Y | 10.69 | 3 | 12632 | 101 |  |
| search_extract | 1 | Y | 10.44 | 3 | 12632 | 101 |  |
| search_extract | 2 | Y | 10.03 | 3 | 12632 | 101 |  |
| form_fill | 0 | Y | 12.03 | 3 | 12647 | 158 |  |
| form_fill | 1 | Y | 11.5 | 3 | 12647 | 158 |  |
| form_fill | 2 | Y | 12.08 | 3 | 12647 | 158 |  |
| table_paginate | 0 | Y | 14.1 | 4 | 19549 | 119 |  |
| table_paginate | 1 | Y | 13.96 | 4 | 19549 | 119 |  |
| table_paginate | 2 | Y | 13.94 | 4 | 19549 | 119 |  |
| login_flow | 0 | Y | 10.81 | 3 | 12560 | 117 |  |
| login_flow | 1 | Y | 10.52 | 3 | 12560 | 117 |  |
| login_flow | 2 | Y | 11.12 | 3 | 12560 | 117 |  |
| modal_dismiss | 0 | Y | 9.86 | 3 | 12503 | 92 |  |
| modal_dismiss | 1 | Y | 9.78 | 3 | 12503 | 92 |  |
| modal_dismiss | 2 | Y | 9.47 | 3 | 12503 | 92 |  |
| heavy_dom | 0 | Y | 7.34 | 2 | 6853 | 52 |  |
| heavy_dom | 1 | Y | 7.39 | 2 | 6854 | 52 |  |
| heavy_dom | 2 | Y | 7.74 | 2 | 6854 | 52 |  |