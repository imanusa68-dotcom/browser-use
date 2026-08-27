# Bench report: smoke_debug (profile=baseline)

- Runs: 1, SR: 0/1 = 0.0% (Wilson CI [0.00, 0.79])
- T_task p50: 11.9s, mean: 11.9s
- N_steps mean: 7.0
- CDP cmds/run: 168, sleep ms/run: 30138.9

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 6 | 445.0 | 932.1 | 3170.8 |
| browser.screenshot | 6 | 144.2 | 159.3 | 837.8 |
| browser.state_request | 7 | 153.3 | 167.2 | 924.6 |
| cdp.cmd | 168 | 2.7 | 87.5 | 2221.0 |
| dom.cdp_ax_tree | 7 | 9.6 | 21.4 | 84.4 |
| dom.cdp_get_all_trees | 7 | 23.9 | 33.8 | 175.7 |
| dom.get_dom_tree | 7 | 25.9 | 36.0 | 190.8 |
| dom.get_serialized_dom_tree | 7 | 26.7 | 37.4 | 197.4 |
| idle.sleep | 130 | 57.5 | 195.7 | 30138.8 |
| phase.get_next_action | 6 | 198.2 | 740.0 | 1764.2 |
| phase.llm_call | 6 | 198.1 | 739.5 | 1763.1 |
| phase.multi_act | 1 | 667.0 | 667.0 | 667.0 |
| phase.prepare_context | 6 | 239.6 | 259.3 | 1389.2 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | N | 11.93 | 7 | 0 | 0 |  |