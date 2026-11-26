# Authentication, sessions, secret storage

For creating or changing these boundaries. Prefer maintained capabilities of the existing framework, identity provider, or project owner. These defaults guide new work; they do not authorize replacing established authentication during unrelated work. Verify current authoritative guidance and the installed implementation before choosing parameters.

## Passwords

Prefer a maintained Argon2id implementation unless deployment constraints require another supported algorithm. Pick work factors from current guidance and measure verification cost under the expected memory and concurrency budget; do not freeze parameters in code you copy from a skill. Use the library's unique salt and self-describing hash format, and support rehash as parameters evolve.

Keep responses identical for unknown accounts and wrong passwords. Verify a maintained dummy hash for unknown accounts instead of skipping the expensive work, and apply abuse controls before either path. Keep the blocking-task concurrency guarantees from rust.md. [OWASP passwords](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

## Opaque browser sessions

- Generate tokens with a cryptographically secure RNG and enough entropy; store only token digests plus metadata. Never derive tokens from account IDs, timestamps, or a general-purpose RNG.
- HTTPS only, `Secure` + `HttpOnly` cookies. Set `SameSite` explicitly to fit real navigation and identity-provider flows (`None` requires `Secure`). Prefer host-only scope and the `__Host-` prefix when the required path and domain allow.
- Enforce idle and absolute expiry on the server. Rotate the session at authentication and privilege change and invalidate the replaced token. Define revocation for logout, credential reset, compromise, and suspension; test that replayed tokens fail.
- Bearer session tokens never go in URLs, logs, page data, or ordinary browser storage. Cookie flags reduce exposure; they do not replace XSS prevention or CSRF protection.

Use framework session primitives where available; a custom token format adds no security by itself. [OWASP sessions](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

## CSRF

For cookie-authenticated state changes use and test the framework's maintained defense. If absent, use a maintained synchronizer token or session-bound signed double-submit; never a naive cookie-equality check.

Origin or Fetch Metadata defenses need an explicit policy for missing headers, trusted origins, subdomains, and non-browser clients. `SameSite` and CORS are not substitutes for that policy. State changes never use safe methods. Test rejected cross-origin mutations and valid flows, including authentication callbacks. [OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

## Retrievable credentials

Minimize retained secrets. Prefer an established vault or managed secret service; when application-level encryption is needed use a maintained authenticated-encryption API, never custom cryptography. Follow its nonce rules, keep keys apart from ciphertext, restrict key access, and define versioning, rotation, and recovery. Encryption without integrity cannot detect substitution. [OWASP crypto storage](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)

When cross-tenant, cross-record, or cross-purpose substitution is a threat, bind those values as authenticated context and rebuild the expected context from the authorized record at decryption; never trust context carried beside attacker-controlled ciphertext. Test wrong-context and tampered-ciphertext rejection without exposing plaintext or cryptographic detail.

## Focused proof

Verify the boundary that changed: invalid-password behavior and resource bounds; session expiry, rotation, revocation; cross-origin rejection; ciphertext integrity and context binding. Keep secrets out of fixtures and diagnostics; use isolated credentials. A successful login alone does not verify authentication security.
