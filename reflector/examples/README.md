<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# reflector Examples

Annotated worked examples for the primary Reflector runtime workflows.

Each example is self-contained, executable, and demonstrates the intended
usage of the public Python interfaces without requiring network access or
external credentials.

## Examples

| Example | File | Description |
|---------|------|-------------|
| Audit pipeline | [`audit_example.py`](audit_example.py) | Run the four-stage reflective audit pipeline and interpret the result |
| Synchronization checkpoint | [`synchronization_example.py`](synchronization_example.py) | Evaluate synchronization boundaries and inspect active boundary state |
| Milestone orchestration | [`milestone_example.py`](milestone_example.py) | Create and advance a milestone through its lifecycle, including the enforced human-review boundary |

## Running the examples

With a development checkout:

```bash
# Install the package
uv sync --all-extras

# Run the audit example
uv run python -m reflector.examples.audit_example

# Run the synchronization example
uv run python -m reflector.examples.synchronization_example

# Run the milestone example
uv run python -m reflector.examples.milestone_example
```

All examples are also verified as part of the test suite:

```bash
uv run pytest tests/ -q
```

## Example structure

Each example file follows the same structure:

1. **Purpose** — what the example demonstrates
2. **Prerequisites** — what must be installed
3. **Public interfaces used** — the classes and methods exercised
4. **Expected output** — what to expect when running the example
5. **Cleanup** — how to clean up any state (most examples write no files)
6. **Reference** — links to specifications and implementation files
7. **Annotated code** — step-by-step implementation with inline comments

## Reference specifications

- [`specs/reflector.spec.md`](../../specs/reflector.spec.md) — Master Reflector specification
- [`specs/synchronization/synchronization-checkpoint.spec.md`](../../specs/synchronization/synchronization-checkpoint.spec.md) — Synchronization checkpoint contract

## Related documentation

- [`docs/getting-started.md`](../../docs/getting-started.md) — Zero-to-working-environment setup
- [`docs/architecture-overview.md`](../../docs/architecture-overview.md) — System architecture reference
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — Contributor guide
