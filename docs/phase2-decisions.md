# Phase 2 Decisions and Assumptions Log

This document tracks all decisions, inferred business rules, and fallback assumptions made during Phase 2 development.

---

## Decision: Partial and Canceled Refund Calculation

Status: CONFIRMED

Source checked:
- Client instructions & Phase 2 Policy
- RapidSeen API documentation

Finding:
When an order status reaches Canceled or Partial, refund is calculated proportionally as:
`refund_coins = cost_coins * remains / original_quantity`

Implemented rule:
If `remains` is present, the proportional formula is applied. If `remains` is missing or invalid, no automatic refund is processed to prevent financial errors, and a warning is logged.

Code location:
`app/services/order_lifecycle_service.py`

Needs client confirmation:
No

---

## Decision: Partial Refund Rounding

Status: FALLBACK

Source checked:
- RapidSeen API documentation
- RapidSeen example
- Client requirements

Finding:
No explicit coin rounding rule was found in the project sources.

Implemented rule:
`ROUND_HALF_UP` using `decimal.Decimal` is used when converting a fractional coin refund to an integer number of coins.

Reason:
Coins are integers in the system. `ROUND_HALF_UP` provides a predictable and neutral rounding policy.

Code location:
`app/services/order_lifecycle_service.py`

Needs client confirmation:
Yes

---

## Decision: Cancel Request Status Handling

Status: CONFIRMED

Source checked:
- RapidSeen API documentation
- Phase 2 Policy

Finding:
Responses to cancel action (`Sent`, `Already sent`, `Not possible`) indicate only the result of the cancel request, not a final order status.

Implemented rule:
Requesting a cancel sends the action to RapidSeen without directly marking the order as `CANCELED`. The final order status is resolved in subsequent status polling.

Code location:
`app/services/order_lifecycle_service.py`

Needs client confirmation:
No
