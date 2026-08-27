# Bench report: o1_fast (profile=fast)

- Runs: 9, SR: 9/9 = 100.0% (Wilson CI [0.70, 1.00])
- T_task p50: 10.2s, mean: 9.6s
- N_steps mean: 2.7
- CDP cmds/run: 124.3, sleep ms/run: 27975.7

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 15 | 3743.7 | 5303.0 | 60299.0 |
| browser.screenshot | 15 | 149.4 | 221.5 | 2344.0 |
| browser.state_request | 24 | 174.1 | 1018.3 | 7608.8 |
| cdp.cmd | 1119 | 2.9 | 112.4 | 19758.3 |
| dom.cdp_ax_tree | 24 | 13.4 | 818.8 | 3837.2 |
| dom.cdp_get_all_trees | 24 | 28.1 | 834.9 | 4183.3 |
| dom.get_dom_tree | 24 | 29.4 | 987.4 | 5019.1 |
| dom.get_serialized_dom_tree | 24 | 30.8 | 1008.7 | 5161.4 |
| idle.sleep | 753 | 9.0 | 1855.1 | 251781.2 |
| phase.execute_actions | 15 | 0.9 | 1687.5 | 8651.9 |
| phase.get_next_action | 15 | 3069.9 | 3301.6 | 46321.1 |
| phase.llm_call | 15 | 3069.4 | 3301.4 | 46317.0 |
| phase.multi_act | 24 | 240.8 | 1687.5 | 13953.4 |
| phase.prepare_context | 15 | 262.8 | 666.8 | 5073.8 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | Y | 10.84 | 3 | 12632 | 101 |  |
| search_extract | 1 | Y | 10.0 | 3 | 12632 | 101 |  |
| search_extract | 2 | Y | 10.18 | 3 | 12632 | 101 |  |
| form_fill | 0 | Y | 11.22 | 3 | 12647 | 158 |  |
| form_fill | 1 | Y | 11.03 | 3 | 12647 | 158 |  |
| form_fill | 2 | Y | 10.95 | 3 | 12647 | 158 |  |
| heavy_dom | 0 | Y | 7.8 | 2 | 6854 | 52 |  |
| heavy_dom | 1 | Y | 7.38 | 2 | 6854 | 52 |  |
| heavy_dom | 2 | Y | 7.07 | 2 | 6853 | 52 |  |