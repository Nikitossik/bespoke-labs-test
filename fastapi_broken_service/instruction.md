In /app there is a FastAPI payments service with files main.py, models.py, and schemas.py.

Fix POST /payments so it satisfies this exact contract:

1. Missing Idempotency-Key header:
- return 400

2. Idempotency-Key normalization:
- trim leading/trailing spaces from Idempotency-Key
- if key is empty after trim, return 400
- use the normalized key for all lookups and inserts

3. First valid request for a new Idempotency-Key:
- create one payment row
- return 201

4. Repeating the same Idempotency-Key with the same amount:
- do not create a new payment row
- return the existing payment
- return 200

5. Repeating the same Idempotency-Key with a different amount:
- do not create a new payment row
- return 409

Important:
- Do not break existing response schema fields.
- Keep behavior deterministic.
- Modify files only in /app.