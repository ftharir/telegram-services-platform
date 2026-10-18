# Phase 3 Decisions Log

## RapidSeen Service ID Fallback
- **Decision**: Service ID = 1 selected as default for Telegram View orders in RapidSeen API.
- **Reason**: RapidSeen API documentation requires service_id integer parameter.
- **Fallback Note**: FALLBACK service_id=1 set in view_handler and view_multiple_handler.
