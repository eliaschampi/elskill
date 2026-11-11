# Arquitectura de referencia (core-rs)

Para iniciar un proyecto o un módulo nuevo. Un proyecto existente conserva su stack y sus dueños: de aquí se copia el criterio, no el código.

**Contenido:** 1. Forma · 2. Stack · 3. Ciclo de una request · 4. Decisiones que no se revierten · 5. Mapa del servidor · 6. Puertas que comprueba la máquina · 7. Presupuestos · 8. Variantes · 9. Arranque de un proyecto

## 1. Forma

```text
web/  (SvelteKit SPA + Lumi) ──/api──► server (axum) ──► PostgreSQL 18
                                          │   SET ROLE <app>; RLS FORCE
                                          └──► motores externos sin estado (proceso aparte)

crates/domain   reglas puras: tipos validados, política de acceso, contrato (→ TypeScript),
                aritmética exacta, máquinas de estado. Sin tokio, sqlx ni axum.
crates/server   HTTP, sesiones, tenancy y SQL: un archivo por recurso.
migrations/     SQL-first: PostgreSQL es dueño de FK, UNIQUE, CHECK, triggers, vistas y RLS.
web/            la SPA; sus tipos se generan desde `domain`.
docs/           SPEC.md (ley) · API.md (contrato) · STATUS.md (hechos verificados).
```

Dos crates y nada más: sin capa de repositorios, sin servicios que reenvían, sin traits "por si acaso". `domain` se prueba sin base ni red; `server` se prueba por HTTP contra PostgreSQL real.

## 2. Stack

Versiones de core-rs en 2026-11. Al crear un proyecto, fija las vigentes en `rust-toolchain.toml`, `Cargo.toml` y `package.json`.

| Pieza | Elección | Por qué |
| --- | --- | --- |
| Lenguaje | Rust 1.98, edition 2024, `unsafe_code = "forbid"` | El compilador sostiene las garantías; binario pequeño y predecible |
| HTTP | axum 0.8 sobre hyper, con las features mínimas | Extractores tipados: el permiso viaja en el tipo del handler |
| SQL | sqlx 0.9 con `query!` / `query_as!` y caché `.sqlx/` | SQL escrito a mano y verificado al compilar; sin ORM |
| Base | PostgreSQL 18 (`uuidv7()`, RLS) | Dueña de los invariantes |
| Contrato | ts-rs → TypeScript | Los dos lados no pueden desalinearse |
| SPA | SvelteKit 2 con `adapter-static` y `ssr = false`, Svelte 5 runes, TypeScript estricto | Un solo backend; el panel y el POS no necesitan SEO |
| UI | Lumi (`@lumi-ui/svelte`) y Lucide por ícono, como únicas dependencias de runtime | Un sistema de diseño, poco peso |
| Herramientas | pnpm, Vite, oxlint, Prettier, svelte-check | Checks rápidos y sin warnings |

## 3. Ciclo de una request de empresa

```text
1  sesión      cookie → sha256(token) → cuenta                      1 sentencia
2  BEGIN       READ ONLY en GET y HEAD
3  contexto    set_config('app.tenant_code', …, true)               local a la transacción
4  bloqueo     FOR SHARE de la membresía y el rol                   sólo en escrituras
5  hechos      membresía, rol, permisos, módulos y sedes → Actor    1 sentencia
6  requisito   P::met_by(&actor), el de la tabla de rutas           403 si no se cumple
7  handler     sus n sentencias: leer, decidir una vez, escribir, auditar
8  COMMIT      lo hace el handler; soltar la transacción revierte
```

Presupuesto: 5 + n sentencias al leer y 6 + n al escribir. El cuerpo llega completo antes del paso 2 y ninguna llamada de red ocurre entre el 2 y el 8.

## 4. Decisiones que no se revierten

| Decisión | Por qué |
| --- | --- |
| La empresa va en la URL (`/api/t/{slug}/…`, `/{slug}/…`), nunca en la sesión | Un contador con veinte empresas en pestañas no puede operar la equivocada, y todo enlace se comparte |
| El SQL de empresa sólo corre sobre la transacción de empresa; el pool entra con un rol sin `BYPASSRLS`; RLS `FORCE` | Aislamiento doble: si el código olvida el contexto, PostgreSQL devuelve cero filas |
| Una transacción por request, abierta por el extractor; el permiso se declara en la ruta | Sin brecha entre autorizar y escribir; olvidar el permiso no compila |
| Toda regla de autorización vive en un tipo de dominio, un método por operación | Repartida, cada handler aplica un subconjunto: así nacen los bugs |
| La UI muestra sólo los `can_*` y los datos que calcula el servidor | UI y servidor no pueden discrepar |
| PostgreSQL es dueño de los invariantes; la app traduce por nombre de constraint y no los vuelve a comprobar | La base protege aunque el código falle, y la regla vive en un lugar |
| El contrato vive en un archivo de `domain` y se exporta a TypeScript, límites incluidos | Frontend y backend no pueden desalinearse |
| Sesión opaca: en la base sólo `sha256(token)` | Un volcado de la base no entrega sesiones |
| Las entidades se archivan; los hechos sólo se insertan | Historia y auditoría intactas |
| Un sobre de error, un enum de códigos, un estado HTTP por código | El mismo idioma en el servidor, la SPA y los motores externos |
| El servidor no migra al arrancar y no sirve con otro esquema | Ninguna versión corre sobre una base que no es la suya |

## 5. Mapa del servidor

| Archivo | Responsabilidad |
| --- | --- |
| `main.rs` | Subcomandos: `serve`, `migrate` y tareas de consola |
| `lib.rs` | `router(state)`: la tabla de rutas, cada una con su requisito |
| `config.rs` | Entorno → `Config`; el arranque falla si falta algo |
| `db.rs` | Pool, compuerta de esquema, la transacción de empresa y sus constructores |
| `tenancy.rs` | El extractor: sesión → slug → membresía → actor |
| `http.rs` | JSON estricto, guardia CSRF, request id, presupuesto de tiempo, cookie, IP del cliente |
| `error.rs` | `AppError` → sobre de error; constraints → códigos |
| `auth.rs`, `password.rs`, `throttle.rs` | Sesiones, argon2id tras un semáforo, freno |
| `<recurso>.rs` | Handlers y SQL de un recurso; `<recurso>/<parte>.rs` cuando gana una segunda responsabilidad |
| `audit.rs` | `record(&mut tx, acción, sujeto, datos)`, en la misma transacción |
| `outbox/` | El worker: cola con lease, envío y veredicto |
| `vault.rs` | Sella y abre secretos en reposo |

## 6. Puertas que comprueba la máquina

| Garantía | Quién la cierra |
| --- | --- |
| Ningún handler sin permiso | `Tenant<P>`: sin requisito en la ruta, no compila |
| Ninguna transacción fuera de su módulo | `clippy.toml` con `disallowed-methods` |
| Ningún secreto serializado | `Password` y `Secret` no implementan `Serialize` |
| SQL válido contra el esquema | `sqlx::query!` y `cargo sqlx prepare --check` |
| Cliente y servidor alineados | TypeScript generado; CI falla si `git diff` toca el contrato |
| Aislamiento aunque el código falle | RLS `FORCE` y un rol sin `BYPASSRLS` |
| Esquema correcto en producción | El servidor se niega a servir si la versión aplicada no es la suya |
| Cada código de error tiene su frase | `Record<ErrorCode, string>` exhaustivo en la SPA |
| Sin `unwrap` ni warnings | clippy pedantic con `-D warnings`; `svelte-check --fail-on-warnings`; `oxlint --deny-warnings` |

Cada garantía nueva busca su puerta antes de escribirse como regla en un documento.

## 7. Presupuestos

Los de core-rs, como ejemplo. Cada proyecto escribe los suyos en `SPEC.md` antes del primer vertical y los mide en un celular barato con red lenta.

- Request de empresa: 5 + n sentencias al leer, 6 + n al escribir; cero N+1.
- Binario release con menos de 50 MB de RSS en reposo; la memoria de argon2 acotada por su semáforo.
- SPA inicial con menos de 150 KB de JavaScript gzip, en pocos chunks cacheables.
- Tiempos: cuerpo 5 s, request 15 s, espera de bloqueo 2 s.
- Listas: páginas de 50 con cursor.

## 8. Variantes

- **Superficie pública con SEO** (el catálogo de faztore): un segundo runtime de sólo lectura, con SSR y DTO explícitos. Jamás expone vistas de administración, costos, caja ni usuarios.
- **Motor sin estado** (see-php): proceso aparte, sin base ni disco de negocio, con contrato estricto. El core es su único cliente y el dueño de toda memoria.
- **Binario especializado** (pdf-rs, omr-rs): proceso local acotado por tiempo, sin credenciales y fuera de la transacción. Si falta, lo que depende de él responde 503 y lo demás sigue.
- **Monolito SvelteKit o Laravel existente**: se termina su arquitectura con sus dueños actuales; ver las referencias de `el-backend`.

## 9. Arranque de un proyecto

1. `AGENTS.md`, `CLAUDE.md` (sólo `@AGENTS.md`), `docs/SPEC.md`, `docs/STATUS.md` y `TASK.md`: ver `doc-system.md`.
2. Workspace con `domain` y `server`, lints del workspace, `rust-toolchain.toml` y `clippy.toml`.
3. Migración `0001` con los roles, la función de contexto, RLS y el plano de identidad.
4. `db.rs`, `tenancy.rs`, `http.rs` y `error.rs` antes del primer recurso: las garantías van primero.
5. El contrato con el sobre de error y su enum, generado hacia `web/src/lib/api/contract/`.
6. La SPA con un cliente, un layout que carga el contexto una vez, Lumi y un tema de dos semillas.
7. CI con los mismos checks que `AGENTS.md`, contra la misma versión mayor de PostgreSQL que producción.
8. Los presupuestos escritos en `SPEC.md`.
