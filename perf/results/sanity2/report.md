# Bench report: sanity2 (profile=baseline)

- Runs: 6, SR: 6/6 = 100.0% (Wilson CI [0.61, 1.00])
- T_task p50: 10.3s, mean: 10.6s
- N_steps mean: 3.0
- CDP cmds/run: 131.5, sleep ms/run: 31291.3

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 12 | 3894.8 | 4887.3 | 46576.1 |
| browser.screenshot | 12 | 142.5 | 381.5 | 2182.8 |
| browser.state_request | 18 | 146.2 | 499.6 | 3680.2 |
| cdp.cmd | 789 | 3.1 | 94.0 | 13517.0 |
| dom.cdp_ax_tree | 18 | 10.7 | 323.2 | 1429.7 |
| dom.cdp_get_all_trees | 18 | 29.1 | 335.4 | 1686.7 |
| dom.get_dom_tree | 18 | 30.5 | 468.6 | 1984.3 |
| dom.get_serialized_dom_tree | 18 | 31.0 | 482.5 | 2037.6 |
| idle.sleep | 519 | 19.9 | 2043.9 | 187747.5 |
| phase.execute_actions | 12 | 882.5 | 1655.7 | 7673.9 |
| phase.get_next_action | 12 | 2960.1 | 3242.2 | 35616.8 |
| phase.llm_call | 12 | 2959.8 | 3242.0 | 35613.7 |
| phase.multi_act | 18 | 261.3 | 1655.6 | 10520.3 |
| phase.prepare_context | 12 | 232.4 | 418.5 | 3238.0 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | Y | 9.86 | 3 | 12632 | 101 |  |
| form_fill | 0 | Y | 11.54 | 3 | 12647 | 158 |  |
| table_paginate | 0 | Y | 14.25 | 4 | 19549 | 119 |  |
| login_flow | 0 | Y | 10.62 | 3 | 12560 | 117 |  |
| modal_dismiss | 0 | Y | 9.95 | 3 | 12503 | 92 |  |
| heavy_dom | 0 | Y | 7.61 | 2 | 6853 | 52 |  |