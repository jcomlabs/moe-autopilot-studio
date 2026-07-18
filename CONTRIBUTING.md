# Contributing

Contributions should preserve the distinction between deterministic analysis
and optional model-generated explanation.

## Development setup

1. Create a Python 3.11+ virtual environment.
2. Install `.[dev]`.
3. Run `npm ci` in `frontend`.
4. Run the Python and frontend checks before opening a pull request.

```powershell
python -m pytest
Push-Location frontend
npm test
npm run build
Pop-Location
```

## Pull requests

- Keep calculations, protocol checks, budgets, and commands deterministic.
- Add focused tests for changed behavior.
- Do not add benchmark prompts, model files, credentials, private paths, or
  generated build output.
- Label evidence as `measured`, `derived`, or `estimated`; do not silently
  extrapolate beyond a calibration interval.
- Keep event-specific submission copy off `main`.

Report security issues through the process in `SECURITY.md`, not a public issue.
