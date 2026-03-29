In `/app` there is a FastAPI payments service implemented only with `main.py`, `models.py`, and `schemas.py`.

Fix `POST /payments` to satisfy:

- First valid request with `Idempotency-Key` returns `201` and creates one payment.
- Repeating the same key with the same payload returns the existing payment with `200` and does not create duplicates.
- Repeating the same key with a different amount returns `409`.
- If `simulate_transient_failure=true`, the first request for that key returns `503`; retrying with the same key and `simulate_transient_failure=false` succeeds and still results in exactly one payment row for that key.

Modify files only in `/app`.