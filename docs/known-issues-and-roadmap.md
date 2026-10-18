# Known issues and roadmap

A plain list of what is incomplete or inconsistent at the moment, checked against the code and by running the tests.

## Known issues

| # | Where | What | Effect |
|---|---|---|---|
| 1 | `tests/test_wallet.py`, `tests/test_order.py`, `tests/test_task5_unit.py` | They connect to a real PostgreSQL and write test rows. | They fail with *connection refused* unless the Docker stack from `docker-compose.yml` is running. All other tests (20) run without a database. |
| 2 | Phase 3 flows | Connected to the real services and covered by mock-based unit tests, but **not yet run against a live bot, database and RapidSeen account**. | Do one end-to-end run with a test bot before relying on them. |
| 3 | `app/database/models/order.py` | An order does not store the target link (the link is only sent to the provider). | The order list and tracking screens cannot show the link. Needs a new column and an Alembic migration. |
| 4 | `view_handler.py`, `view_multiple_handler.py` | Service id `1` and a price of 1 coin per 100 views are fallback constants (see [`phase3-decisions.md`](phase3-decisions.md)). | Needs confirmation from the real service list; move to configuration. |
| 5 | `app/main.py` | The bot session uses a hard-coded local SOCKS5 proxy, `socks5://127.0.0.1:10808`. The forced-channel-join middleware is implemented but its registration is commented out. The file also starts with the previous version of itself inside a block comment. | Not portable; make the proxy and the middleware configurable. |
| 6 | `app/web.py` and `app/server.py` | Two FastAPI entry points; only `app/web.py` is used by `app/run.py`. | Remove or merge the unused one. |
| 7 | `docker-compose.yml` | Development database password in plain text. | Change before any shared deployment; ideally read it from `.env`. |
| 8 | `OrderLifecycleService.process_open_orders` | Nothing calls it periodically. | Orders stay `SUBMITTED` until a status check is triggered; add a background job. |
| 9 | root `test_phase2_suite.py`, `test_task6_unit.py` | Tests live next to the code in the project root; `pytest` is configured to look in `tests/` only. | Run the Phase 2 suite with `python test_phase2_suite.py`. |

## Fixed in the latest changes

* `RapidSeenAPIError` was imported by the order placement service and by tests but not defined. It is now defined in `app/integrations/rapidseen/client.py`, so the order placement service can be imported again.
* The Phase 3 handlers use the real services: orders go through `OrderPlacementService` (debit, internal order, provider call, automatic refund on failure), the wallet is addressed by the database user id instead of the Telegram id, the matching `InsufficientBalanceError` is caught, and the order list reads from `OrderRepository`.
* Order tracking is restricted to the owner of the order and uses the real status names.
* The Phase 3 routers are registered in `get_handlers_router()`; the *Services* button of the main menu opens the ordering keyboard.
* A stale test (`tests/test_rapidseen_final.py`) was rewritten for the current client; tests were added for the link validator and the Phase 3 handlers.

## Roadmap

1. Run the whole flow once end to end with a test bot, a test database and a RapidSeen test account.
2. Store the target link on the order (new column + migration) and show it in the tracking screens.
3. Confirm service ids and prices with the RapidSeen service list; move them to configuration.
4. Make the proxy and the forced-join middleware configurable.
5. Add a background job that calls `OrderLifecycleService.process_open_orders` periodically.
6. Admin features: manual wallet adjustments (`ADJUSTMENT` transactions exist), order search.
7. CI: run the tests and a linter on every push.
