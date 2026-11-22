# Security Policy

Ephemeral Clipboard sends secrets. Security reports have high priority.

## Supported versions

| Version | Supported |
| --- | --- |
| Latest release | Yes |
| Older releases | No |

## Report a vulnerability

Do not open a public issue.

Use GitHub private vulnerability reporting:

1. Go to the **Security** tab of this repository.
2. Click **Report a vulnerability**.
3. Include:
   - The affected version and OS
   - The steps to reproduce the problem
   - The effect (for example, plaintext exposure or a bypass of the attempt limit)

Do not include real secrets in your report. Use test values.

## What happens next

1. We confirm that we received your report.
2. We check the problem and tell you if we accept it.
3. We fix it, release a new version and credit you in the release notes, unless you ask us not to.

Please do not disclose the problem in public until a fix is released.

## Scope

**In scope:**

- A relay that can recover the plaintext, the key or the code
- Any way to test code guesses offline
- A bypass of key confirmation or of the 3-attempt limit
- A payload that is delivered more than once, or that stays after its TTL
- Relay data written to disk
- Payloads, keys or codes in logs or error messages
- Ciphertext changes that are not detected
- Clipboard auto-clear that deletes a value the user copied later
- Key material that stays in memory after use, where `SecureBuffer` claims to protect it

**Out of scope:**

- Plaintext copies in Python memory (`str`, `bytes`). This is a known limit, documented in [`docs/threat-model.md`](docs/threat-model.md).
- Copies kept by the OS clipboard or by the app the user pastes into
- Metadata seen by the relay (IP addresses, times, payload size)
- Malware that runs as the user's account
- Attacks that need physical access to an unlocked machine
- Clipboard managers that ignore the history exclusion flags
