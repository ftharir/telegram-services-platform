# Phase 3 Decisions Log

## RapidSeen Service ID Fallback
- **Decision**: Service ID = 1 selected as default for Telegram View orders in RapidSeen API.
- **Reason**: RapidSeen API documentation requires service_id integer parameter.
- **Fallback Note**: the default is `VIEW_SERVICE_ID=1` and `VIEW_PRICE_COINS_PER_100=1` in `app/core/config.py`; both can be overridden in `.env` and must be replaced by the real service id and price before going live.

## Orders go through the placement service
- **Decision**: Phase 3 handlers place orders with `OrderPlacementService.place_order` instead of debiting the wallet and creating the order themselves.
- **Reason**: the service already debits, creates the internal order with its idempotency key, calls the provider and refunds automatically on failure; one code path for money is safer than two.

## Idempotency per confirmation
- **Decision**: an idempotency key is generated when the order summary is shown (one key for a single order, `<key>-<index>` for each link of a multi-post order). A second press of the confirm button reuses the key and is rejected as a duplicate.

## Wallet is addressed by database user id
- **Decision**: handlers use `db_user.id` (injected by the DB middleware), not the Telegram id, for the wallet and for orders.

## Tracking is limited to the owner
- **Decision**: a tracking code is shown only to the user who owns the order. The tracking screens show the stored target link (`orders.target_link`, added by the migration `a3c7e1d5b9f2`; older orders have none).

## Services button
- **Decision**: the *Services* button of the main menu opens the ordering keyboard (view, multi-view, order list, wallet).


## Order status check runs in the background
- **Decision**: `app/run.py` starts a polling task next to the bot and the web server when `RAPIDSEEN_API_KEY` is set and `ORDER_POLL_INTERVAL_SECONDS` is above 0. A failed round is logged and retried; it never stops the bot.
