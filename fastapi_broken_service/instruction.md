In /app there is a FastAPI payments service with files main.py, models.py, and schemas.py.

Fix POST /payments so it satisfies this exact contract:

1. Missing Idempotency-Key header:
- return 400

2. First valid request for a new Idempotency-Key:
- create one payment row
- return 201

3. Repeating the same Idempotency-Key with the same amount:
- do not create a new payment row
- return the existing payment
- return 200

4. Repeating the same Idempotency-Key with a different amount:
- do not create a new payment row
- return 409

5. Transient failure flow:
- first request with simulate_transient_failure=true for a key returns 503
- retry with the same key and simulate_transient_failure=false succeeds
- this retry creates exactly one payment row for that key and returns 201
- any next repeat with same key and same amount returns 200 and does not create duplicates

Important:
- Do not break existing response schema fields.
- Keep behavior deterministic.
- Modify files only in /app.