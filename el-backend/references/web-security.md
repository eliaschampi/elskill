# Authentication, sessions, and secret storage

Read when creating or changing these boundaries. Prefer the maintained capabilities of the existing framework, identity provider, or project owner. These defaults guide new work; they do not authorize replacing established authentication during an unrelated task. Verify current authoritative guidance and the installed implementation before selecting parameters.

## Password authentication

For new password storage, prefer a maintained Argon2id implementation unless deployment constraints require another supported algorithm. Select work factors from current guidance and measure verification cost under the expected memory and concurrency budget; do not freeze security parameters in a reusable skill. Use the library's unique salt generation and self-describing hash format, and support rehashing as parameters evolve.

Keep responses consistent for unknown accounts and invalid passwords. Where appropriate, verify a maintained dummy hash for unknown accounts rather than skipping expensive work; apply abuse controls before either path. Retain the blocking-task concurrency guarantees in the [Rust reference](rust-axum-sqlx.md). [OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

## Opaque browser sessions

- Generate unpredictable tokens with a cryptographically secure random generator and sufficient entropy; store only token digests and session metadata. Never derive tokens from account IDs, timestamps, or general-purpose random generators.
- Transport browser sessions over HTTPS in `Secure`, `HttpOnly` cookies. Set `SameSite` explicitly to match real navigation and identity-provider flows; `None` requires `Secure`. Prefer host-only scope and the `__Host-` prefix when compatible with the required cookie path and domain behavior.
- Enforce idle and absolute expiration on the server. Rotate session identity at authentication and privilege changes; invalidate replaced tokens. Define revocation for logout, credential reset, compromise, and account suspension, and test that replayed tokens fail.
- Do not place bearer session tokens in URLs, logs, page data, or ordinary browser storage. Cookie flags reduce exposure; they do not replace XSS prevention or CSRF protection.

Use framework session primitives where available; a custom token format does not improve security by itself. [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

## CSRF protection

For cookie-authenticated state changes, use and test the framework's maintained CSRF defense. If unavailable, use a maintained synchronizer-token or session-bound signed double-submit implementation appropriate to the architecture. Do not implement a naive cookie-equality check.

Origin or Fetch Metadata defenses require an explicit policy for missing headers, trusted origins, subdomains, and non-browser clients. `SameSite` and CORS are not automatic substitutes for that policy. State-changing actions must not use safe HTTP methods. Test rejected cross-origin mutations and valid application flows, including authentication callbacks where applicable. [OWASP CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

## Retrievable credentials

Minimize retained secrets. Prefer an established vault or managed secret service; when application encryption is needed, use a maintained authenticated-encryption API rather than custom cryptography. Follow its nonce requirements, separate keys from ciphertext, restrict key access, and define key versioning, rotation, and recovery. Encryption without integrity does not detect substitution or modification. [OWASP cryptographic storage](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)

When ciphertext substitution across tenants, records, or purposes is a threat, bind those values as authenticated context and reconstruct the expected context from the authorized record during decryption. Do not trust context carried alongside attacker-controlled ciphertext. Test wrong-context and tampered-ciphertext rejection without exposing plaintext or cryptographic details.

## Focused proof

Verify the boundary that changed: invalid-password behavior and resource bounds; session expiry, rotation, and revocation; cross-origin rejection; or ciphertext integrity and contextual binding. Keep secrets out of fixtures and diagnostics, and use isolated credentials. A successful login alone does not verify authentication security.
