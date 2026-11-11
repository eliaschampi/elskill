# Rust + axum + sqlx (el estilo de core-rs)

Fragmentos reales de core-rs, recortados. Antes de usar la API de un crate, lee su fuente en `~/.cargo/registry/src`: no adivines firmas.

**Contenido:** 1. Workspace y puertas · 2. `domain`: tipos que sólo existen válidos · 3. Tabla de rutas · 4. Handler · 5. Política · 6. Errores · 7. SQL · 8. Async y recursos · 9. Pruebas · 10. Checks

## 1. Workspace y puertas

```toml
# Cargo.toml
[workspace]
resolver = "3"
members = ["crates/domain", "crates/server"]

[workspace.package]
edition = "2024"
rust-version = "1.98"

[workspace.lints.rust]
unsafe_code = "forbid"

[workspace.lints.clippy]
pedantic = { level = "warn", priority = -1 }
unwrap_used = "warn"
expect_used = "warn"

[profile.release]
lto = "thin"
codegen-units = 1
strip = true
```

```toml
# clippy.toml — una transacción sólo se abre en db.rs. En cualquier otro sitio es un error de lint.
disallowed-methods = [
    { path = "sqlx_core::pool::Pool::begin", reason = "open company transactions through db::TenantTx" },
]
```

```toml
# .cargo/config.toml
[env]
TS_RS_EXPORT_DIR = { value = "web/src/lib/api/contract", relative = true }
SQLX_OFFLINE = "true"
```

- Las dependencias se declaran en `[workspace.dependencies]` con las features mínimas (`default-features = false` donde el crate lo permite).
- `domain` depende de serde, ts-rs, uuid, thiserror y poco más. No conoce tokio, sqlx ni axum.
- Un `#[allow(...)]` siempre lleva `reason = "…"`.

## 2. `domain`: tipos que sólo existen válidos

```rust
//! Validated values. A type here can only be built through `parse`, so
//! anything that reaches the server's logic is already correct: parse, don't
//! validate. Messages are user-facing Spanish.

macro_rules! text_type {
    ($(#[$doc:meta])* $name:ident, $max:literal) => {
        $(#[$doc])*
        #[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize, TS)]
        #[serde(try_from = "String", into = "String")]
        pub struct $name(String);

        impl $name {
            pub const MAX_CHARS: usize = $max;

            pub fn parse(value: &str) -> Result<Self, Invalid> {
                clean_text(value, $max).map(Self)
            }

            #[must_use]
            pub fn as_str(&self) -> &str {
                &self.0
            }
        }
        // + TryFrom<String>, From<$name> for String, Display
    };
}

text_type!(BranchName, 80);
text_type!(
    /// Why a comprobante is annulled (SUNAT RA: up to 100 characters).
    AnnulReason, 100
);
```

- Los cuerpos de request llevan estos tipos: un valor malo falla al deserializar y el servidor responde 400 con el JSON Pointer del campo.
- `Password` y `Secret` no implementan `Serialize`.
- Un enum de dominio expone `ALL`, `key()`, `from_key()` y su `label()` en español: la base guarda la clave y el catálogo vive en el código.
- El contrato vive en `contract.rs`, cada tipo con `#[derive(TS)]` y `#[ts(export)]`. `cargo test -p domain` regenera el TypeScript, que nunca se edita a mano.

## 3. Tabla de rutas: el permiso viaja en el tipo

```rust
/// Company routes, under `/api/t/{slug}`: each names its requirement, the
/// "Permiso" column of docs/API.md.
fn tenant_routes() -> Router<AppState> {
    Router::new()
        .route(
            "/branches",
            get(branches::list::<need::BranchesView>)
                .post(branches::create::<need::BranchesManage>),
        )
        .route("/branches/{code}", put(branches::update::<need::BranchesManage>))
}
```

```rust
/// What a route demands of the member, beyond being an active one.
pub trait Requirement {
    fn met_by(actor: &Actor) -> bool;
}

/// An authorized member of one company, holding the request's transaction.
/// Handlers commit it (`tenant.tx.commit()`); dropping it rolls back.
pub struct Tenant<P> {
    pub tx: TenantTx,
    pub ctx: Context,
    need: PhantomData<fn() -> P>,
}
```

Un handler no puede obtener un `Tenant` sin un requisito: olvidar el permiso no compila. La tabla de rutas es el espejo de la columna "Permiso" de `docs/API.md`.

## 4. Handler

```rust
/// `PUT /api/t/{slug}/branches/{code}`. The establishment code is fixed.
pub async fn update<P: Requirement>(
    mut tenant: Tenant<P>,
    Code(code): Code,
    Json(body): Json<UpdateBranch>,
) -> AppResult<Json<BranchView>> {
    let branch = sqlx::query_as!(
        BranchView,
        "UPDATE branches
            SET name = $3, address_line = $4, ubigeo = $5, is_active = $6
          WHERE code = $1 AND tenant_code = $2
          RETURNING code, name, establishment_code, address_line, ubigeo, is_active",
        code,
        tenant.tx.tenant_code(),
        body.name.as_str(),
        body.address_line.as_ref().map(AddressLine::as_str),
        body.ubigeo.as_ref().map(Ubigeo::as_str),
        body.is_active,
    )
    .fetch_optional(tenant.tx.conn())
    .await?
    .ok_or(ErrorCode::NotFound)?;

    audit::record(
        &mut tenant.tx,
        Action::BranchUpdated,
        Some(code),
        json!({ "name": branch.name, "is_active": branch.is_active }),
    )
    .await?;

    tenant.tx.commit().await?;

    Ok(Json(branch))
}
```

Lo que enseña:

- El archivo abre con `//!`: qué regla guarda y quién la protege ("Rule 8 belongs to the database (`branches_structure`, checked at COMMIT)").
- El SQL vive en el handler y mapea directo al tipo del contrato (`BranchView`): no hay DTO intermedio ni repositorio.
- `WHERE code = $1 AND tenant_code = $2`, aunque RLS ya aísle.
- `fetch_optional … ok_or(ErrorCode::NotFound)?`: sin fila, 404.
- La auditoría va en la misma transacción y el `commit` es explícito.
- El handler no comprueba "al menos una sede activa": lo hace PostgreSQL al COMMIT y `error.rs` lo traduce.
- Una request que llama a la red autoriza en una transacción de lectura, la cierra, llama, y vuelve a entrar con `Tenant::enter(…)` para escribir.

## 5. Política: una pregunta por decisión

```rust
// handler: cargar hechos, preguntar una vez, escribir
let target = fetch_for_update(&mut tenant.tx, &tenant.ctx.actor, viewer, code).await?;
let role = roles::assignable(&mut tenant.tx, body.role_code).await?;
let reach = branches::requested_reach(&mut tenant.tx, body.all_branches, &body.branch_codes).await?;

tenant.ctx.actor.may_edit_member(&target.facts, Some((&role.facts, &reach)))?;

// lista: el mismo método calcula lo que la UI muestra
can_edit: actor.may_edit_member(&facts, None).is_ok(),
```

Cada `may_*` de `domain::access::Actor` devuelve `Result<(), Denial>` y aplica juntas todas sus reglas (cobertura de permisos, regla del propietario, alcance de sedes). `impl From<Denial> for AppError` convierte la negación en su código. La matriz se prueba unitaria en `domain`.

## 6. Errores

```rust
pub enum AppError {
    /// A client-facing error: code, Spanish message, optional pointer.
    Api { code: ErrorCode, message: Cow<'static, str>, pointer: Option<String>, retry_after: Option<u64> },
    /// 503 `unavailable`; the reason goes to the log.
    Unavailable(&'static str),
    /// 500 `internal_error`; the cause goes to the log.
    Internal(BoxError),
}

AppError::invalid("/branch_codes/2", "La sede no existe o está inactiva.") // 400 con pointer
ErrorCode::NotFound.into()                                                 // mensaje por defecto
```

```rust
impl From<sqlx::Error> for AppError {
    fn from(error: sqlx::Error) -> Self {
        // SQLSTATE: una carrera que perdió, o la base que va atrasada.
        //   "40P01" | "40001" | "55P03" → Conflict        "57014" → Unavailable
        let mapped = match constraint(&error) {
            Some("memberships_keep_owner") => Some(E::LastOwner.into()),
            Some("invitations_pending_email_uq") => {
                Some(Self::pointed(E::InvitationPending, "/email", message(E::InvitationPending)))
            }
            // The same draft sent twice at once: one wins.
            Some("documents_request_key_uq" | "payments_request_key_uq") => Some(E::Conflict.into()),
            _ => None,
        };
        mapped.unwrap_or_else(|| Self::Internal(error.into()))
    }
}
```

- `ErrorCode` vive en el contrato (se exporta a TypeScript) y `ErrorCode::status()` da su único estado HTTP.
- Un código nuevo llega completo en el mismo cambio: la variante, su estado, su mensaje en español, su título en la SPA (el mapa exhaustivo rompe el build si falta) y su fila en la tabla de errores de la spec.
- Un 5xx nunca lleva la causa en el cuerpo: viaja al log en la línea de la request.

## 7. SQL con sqlx

- Sólo `sqlx::query!`, `query_as!` y `query_scalar!`: se verifican al compilar contra `.sqlx/`.
- Lotes con arrays: `code = ANY($2)` para leer, `SELECT $1, $2, unnest($3::uuid[])` para insertar. Nunca una consulta dentro de un bucle.
- `r#"SELECT … AS "name!""#` cuando sabes que una columna no es nula y sqlx no puede inferirlo.
- Tras cambiar SQL o esquema: `cargo sqlx prepare --workspace -- --all-targets`, y `.sqlx/` se versiona. No se edita a mano.
- Las listas usan los helpers de cursor de `db.rs` (`PAGE_SIZE`, `next_cursor`); no inventes otra paginación.

## 8. Async y recursos

- Lo que consume CPU (argon2) va en `spawn_blocking`, tras un semáforo que acota cuántos corren a la vez.
- Nada de `unwrap` ni `expect` fuera de los tests y del arranque: `?` con `AppError`, u `ok_or`.
- El cuerpo tiene tope (64 KiB) y plazo (5 s), la request un presupuesto (15 s) y el pool un `acquire_timeout`.
- `#[must_use]` en constructores y consultas puras.
- La configuración se lee una vez al arrancar a un `Config`; si falta algo, el proceso no arranca.

## 9. Pruebas

```rust
#[sqlx::test(migrator = "server::MIGRATOR")]
async fn a_cashier_has_one_shift_open(options: PgPoolOptions, connect: PgConnectOptions) {
    let app = app(options, connect).await;
    let (owner, slug) = cash_company(&app).await;
    // …
    // Two tabs at once: one shift, whatever the timing.
    let (one, two) = tokio::join!(
        open(&app, &owner, &slug, &principal, "100.5"),
        open(&app, &owner, &slug, &principal, "100.5"),
    );
    let (opened, refused) = if one.status == StatusCode::CREATED { (one, two) } else { (two, one) };
    assert_eq!(opened.status, StatusCode::CREATED, "{}", opened.body);
    assert_eq!(refused.code(), "conflict");
}
```

- Cada test recibe una base nueva, un pool que corre con el rol de la aplicación como en producción, y maneja el router real con cookies reales.
- El nombre del test es la regla, como frase. Se afirma sobre el estado HTTP, `error.code` y `error.pointer`.
- Una prueba por invariante de la spec, con su carrera (`tokio::join!`), y una por familia de rutas para el cableado.
- Lo externo se prueba con un cliente falso; ningún test sale a la red.

## 10. Checks (todos en verde)

```bash
cargo fmt --all
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace            # regenera también el contrato TypeScript
cargo sqlx prepare --workspace --check -- --all-targets
pnpm --dir web run check && pnpm --dir web run build
```

Con `rtk` instalado, antepónlo a los comandos de salida larga (`rtk cargo test`, `rtk cargo clippy`).
