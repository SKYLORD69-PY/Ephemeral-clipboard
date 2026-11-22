# Contributing to Ephemeral Clipboard

Thank you for your interest. This file tells you how to report problems and send changes.

## Before you start

- Join the [PulseEngine Discord](https://discord.gg/VU8RUByEeG) to see open issues on the commission board and to ask questions. To claim an issue, comment on it here on GitHub.
- Read [`docs/project-plan.md`](docs/project-plan.md). It defines the scope.
- Read [`docs/PROTOCOL.md`](docs/PROTOCOL.md) before you change the client or the relay.
- Features that are out of scope (GUI, phone client, file transfer, macOS) go in a `v2-ideas` issue. Do not send a pull request for them.
- For security problems, do not open a public issue. Read [`SECURITY.md`](SECURITY.md).

## Report a bug

Open an issue and include:

1. Your OS and version (for example, Windows 11 or Arch Linux with Wayland).
2. The output of `eclip --version`.
3. The steps to reproduce the problem.
4. What you expected and what happened.

Do not paste real secrets or codes. Use test values.

## Set up the project

Requirements:

- Python 3.11 or later
- Git
- On Linux: `wl-clipboard` (Wayland) or `xclip` (X11)

```sh
git clone https://github.com/<owner>/ephemeral-clipboard.git
cd ephemeral-clipboard
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Send a change

1. Fork the repository and create a branch from `main`.
2. Keep each pull request to one change.
3. Run these commands before you push:

   ```sh
   ruff check .
   ruff format --check .
   mypy src
   pytest
   ```

4. Add tests for new behavior.
5. If you change the wire format, update `docs/PROTOCOL.md` and increase the protocol version.
6. Write a clear pull request title and describe what changed and why.

## Code rules

- Do not write your own cryptography. Use `spake2` and `cryptography`.
- Do not add a dependency without a strong reason. Explain it in the pull request.
- Keep functions small and names clear.
- Keep comments short.
- Never log, print or put in errors any payload, key or code.
- The relay must never store data on disk.
- Do not weaken a security check to make a test pass.

## Commit messages

Use a short summary line in the imperative mood, for example:

```text
relay: close room after 3 failed confirmations
```

## License

When you contribute, you agree that your contribution is licensed under the [MIT License](LICENSE).
