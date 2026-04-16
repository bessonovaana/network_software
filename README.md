# SAGA

- **Saga** is a long-running transaction broken down into a sequence of local transactions.
- **Orchestration** means there is a central “conductor” service (the **Orchestrator**) that tells other services what to do, like “Hey, Warehouse, reserve the item!”
- **Choreography** means services listen to events on their own, like “Oh, an `OrderCreated` event arrived, so I should try to charge the payment.”
- **Compensating transaction** is an action that “undoes” the result of a previous successful step, for example, “refund the card.”

## States
- **NEW** — a new order.
- **PAID** — paid.
- **DONE** — completed.
- **CANCELLED** — cancelled.

## Events
- **CREATE** — creation.
- **RESERVE_OK** — the item is available.
- **RESERVE_FAIL** — the item is not available.
- **PAY_OK** — payment succeeded.
- **PAY_FAIL** — payment failed.

## Transition rules
NEW → (CREATE) → NEW  
NEW → (RESERVE_OK) → NEW  
NEW → (RESERVE_FAIL) → CANCELLED  
NEW → (PAY_OK) → PAID  
NEW → (PAY_FAIL) → CANCELLED  
PAID → (PAY_OK) → DONE  
PAID → (PAY_FAIL) → CANCELLED