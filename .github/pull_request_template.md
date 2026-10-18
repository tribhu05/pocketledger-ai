## Description
Briefly describe the changes introduced in this pull request and why they are needed.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Test addition or improvement

## Verification Checklist
- [ ] Backend tests pass: `pytest backend/tests/test_backend.py -v`
- [ ] Frontend tests & lint pass: `cd frontend && npm run lint && npx vitest run`
- [ ] Production build succeeds: `cd frontend && npm run build`
- [ ] Financial arithmetic verified with Python `Decimal` (no floating-point drift)
- [ ] No telemetry, analytics, or third-party cloud data egress introduced
- [ ] Schema changes in `backend/schemas.py` synchronized with `frontend/src/types.ts`
