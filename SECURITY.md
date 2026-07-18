# Security Policy

## Supported versions

Security fixes are applied to the latest published release and the `main`
branch. Earlier experimental releases are not maintained.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting for this repository. Do not open a
public issue for a suspected vulnerability or include credentials, model data,
local paths, or private benchmark inputs in a report.

Include the affected version, operating system, reproduction steps, impact, and
whether the issue requires the optional local runner or Codex integration. You
should receive an acknowledgement within seven days. No bounty is offered.

## Security boundary

The API binds to `127.0.0.1`. Local experiments use structured executable,
argument, environment, and working-directory fields and never invoke a shell.
The optional advisor delegates authentication to Codex CLI; Studio does not
store ChatGPT tokens. See `docs/ARCHITECTURE.md` for the complete trust boundary.
