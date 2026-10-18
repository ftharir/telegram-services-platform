# Known issues and roadmap

A plain list of what is incomplete or inconsistent at the moment, checked against the code and by running the tests.

## Known issues

| # | Where | What | Effect |
|---|---|---|---|
| 1 | `app/integrations/rapidseen/client.py` | `RapidSeenAPIError` is imported by `order_placement_service.py` and by two test modules, but it is not defined in the client. | `OrderPlacementService` cannot be imported; `tests/test_rapidseen.py`, `tests/test_rapidseen_final.py` and `tests/test_task5_unit.py` fail at collection. The fix is to define the exception class in `client.py`. |
| 2 | `tests/test_wallet.py`, `tests/test_order.py` | They connect to a real PostgreSQL. | They fail with *connection refused* unless the Docker stack from `docker-compose.yml` is running. |
| 3 | `app/bot/handlers/` (Phase 3) | The Phase 3 routers (`view_handler`, `view_multiple_handler`, `order_tracking_handler`) are **not registered** in the running bot. `get_handlers_router()` includes only the start and account routers; `app/bot/main.py` is a placeholder that registers the Phase 3 routers but is not used by `app/run.py`. | The Phase 3 menu and flows are not reachable yet. |
| 4 | Phase 3 handlers | They call methods that do not exist yet on the Phase 2 services (`OrderLifecycleService(session)` without a client, `create_order`, `get_user_orders` on the lifecycle service). | The Phase 3 flows need to be connected to `OrderPlacementService` and the order repository before they can run. |
| 5 | `app/services/rapidseen_client.py` | A placeholder client that only logs and returns a fixed success value. The real client is `app/integrations/rapidseen/client.py`. | Phase 3 orders are not sent to RapidSeen. |
| 6 | `view_handler.py`, `view_multiple_handler.py` | Service id `1` and a price of 1 coin per 100 views are fallback constants (see [`phase3-decisions.md`](phase3-decisions.md)). | Needs confirmation from the real service list. |
| 7 | `app/main.py` | The bot session uses a hard-coded local SOCKS5 proxy, `socks5://127.0.0.1:10808`. The forced-channel-join middleware is implemented but its registration is commented out. The file also starts with the previous version of itself inside a block comment. | Not portable; make the proxy and the middleware configurable. |
| 8 | `app/web.py` and `app/server.py` | Two FastAPI entry points; only `app/web.py` is used by `app/run.py`. | Remove or merge the unused one. |
| 9 | `docker-compose.yml` | Development database password in plain text. | Change before any shared deployment; ideally read it from `.env`. |
| 10 | root `test_phase2_suite.py`, `test_task6_unit.py` | Tests live next to the code in the project root; `pytest` is configured to look in `tests/` only. | Run the Phase 2 suite with `python test_phase2_suite.py` (it passes: 5 of 5 checks). |

## Roadmap

1. Fix item 1, get `pytest` green (with the database container running).
2. Connect the Phase 3 handlers to the Phase 2 services, register their routers in `get_handlers_router()`, and replace the placeholder RapidSeen client by the real one.
3. Confirm service ids and prices with the RapidSeen service list; move them to configuration.
4. Make the proxy and the forced-join middleware configurable.
5. Add a background job that calls `OrderLifecycleService.process_open_orders` periodically.
6. Admin features: manual wallet adjustments (`ADJUSTMENT` transactions exist), order search.
7. CI: run the tests and a linter on every push.
