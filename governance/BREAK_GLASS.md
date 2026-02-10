# Break-Glass Procedure (Template)

This is a compact template you can adapt for your own repositories.

## When it is allowed

- Sev-1 / Sev-2 incidents only.
- Time-critical security patches only.

## Required approvals

- At least two approvers from a named list (role-based), for example:
  - Lead Architect
  - Head of Engineering
  - Security Lead

## Required actions

1. Create an incident ticket id (required): `INC-####`.
2. Apply the minimal fix on a short-lived emergency branch.
3. Merge using the break-glass path (documented for your platform).
4. Record the incident id in the merge/commit message.

## Audit and follow-up

- Alert on break-glass merges.
- Store an immutable audit log entry (who/what/when).
- Require a post-mortem within 24 hours.
