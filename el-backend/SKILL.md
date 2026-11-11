---
name: el-backend
description: Construcción de backend al estilo de Elias con PostgreSQL dueño de los invariantes, una transacción por request, permiso declarado en la ruta, contrato generado, errores tipados y pruebas contra base real. Úsala siempre que se escriba, cambie o revise código de servidor, SQL, esquema, migraciones, endpoints, handlers, workers, colas, integraciones externas, autenticación o permisos, en Rust (axum y sqlx), SvelteKit con Kysely o Laravel y PHP. Trae las reglas de concurrencia, idempotencia, dinero exacto, seguridad y rendimiento que no se negocian.
---

# EL · Backend

La base protege, el dominio decide, el handler orquesta, y no existe nada más. Aplica primero `el-architecture` (dueños, protocolo, cuándo detenerse); esta skill dice cómo se escribe el servidor.

## Núcleo

1. **Manda el proyecto.** Su `AGENTS.md` y su `docs/SPEC.md` ganan a esta skill, y esta skill gana a tus costumbres. Si chocan, obedece al proyecto y dilo.
2. **Prioridad, no invertir:** corrección → legibilidad → consistencia con el repositorio → rendimiento → simplicidad.
3. **Un dueño por regla.** Cada regla, dato y decisión vive en un solo lugar; lo demás lo consulta o lo deriva.
4. **Que lo compruebe la máquina.** Un tipo, un constraint, un lint o un tipo generado valen más que una convención que dependa de la revisión.
5. **No adivines.** Lee el código, sus tests y el fuente de la dependencia antes de usarlos. Ante dinero, identidad, permisos o migraciones, detente y pregunta.
6. **Nada especulativo.** Ni capas, ni opciones, ni rutas, tablas o permisos "para después".
7. Identificadores en inglés; documentos, copy y mensajes al usuario en español; los comentarios siguen el idioma del archivo vecino.

## 0. Antes de escribir

Identifica el stack y lee sólo su referencia. Las reglas `B` valen en todos.

| Si el repositorio tiene… | Lee |
| --- | --- |
| `Cargo.toml` con `axum` y `sqlx` | `references/rust-axum-sqlx.md` |
| `kysely` y `+page.server.ts` | `references/sveltekit-kysely.md` |
| `artisan` o `composer.json` | `references/laravel-php.md` |
| Un cambio de esquema o SQL no trivial, en cualquiera | `references/postgres.md` |

Toda escritura sigue este orden, sin saltos:

```text
requisito en la ruta → entrada ya validada → transacción con su contexto
→ bloquear y leer los hechos → preguntar a la política una vez
→ escribir con RETURNING → auditar en la misma transacción → commit → responder la fila
```

## 1. Datos: PostgreSQL es el dueño

- **B1. SQL-first.** El esquema se escribe a mano en SQL. Los tipos de la aplicación se generan de él o se verifican contra él; nunca al revés.
- **B2. Identidad.** PK `code uuid` (`uuidv7()` en PostgreSQL 18); FK `<entidad>_code`; `snake_case`; `timestamptz` siempre. Un identificador no codifica año, sede ni estado.
- **B3. Relaciones explícitas.** FK o tabla intermedia. Nunca arrays, JSON ni pares polimórficos `type`/`code` para relacionar.
- **B4. Invariantes con nombre.** Toda regla estructural es un constraint `<tabla>_<regla>_<fk|uq|check>` o un trigger que lanza con `CONSTRAINT = '<nombre>'`. El nombre es contrato: la aplicación lo traduce a un código de error y no vuelve a comprobar la regla.
- **B5. Multiempresa por construcción** (cuando el producto lo es). Toda tabla de empresa lleva `tenant_code`, una FK compuesta `(x_code, tenant_code)` y RLS `ENABLE` + `FORCE` con una sola política. La aplicación entra con un rol sin `BYPASSRLS` y con los permisos mínimos por tabla y columna: si el código olvida el contexto, la base devuelve cero filas.
- **B6. Las entidades cambian de estado; los hechos no cambian.** Entidades: columnas con significado (`status`, `is_active`, `archived_at`, `revoked_at`), no un `deleted_at` genérico. Hechos de dinero, stock y auditoría: sólo `INSERT`; corregir es otro hecho con su motivo (anulación, reverso, devolución).
- **B7. Lo derivable no se guarda.** Saldos, totales, diferencias y estados compuestos salen de vistas sobre los hechos. Un read model que usan listas, búsquedas o reportes es una vista con nombre; la aplicación sigue autorizando, filtrando y paginando.
- **B8. Dinero exacto.** `numeric` en la base, enteros exactos en el dominio, texto decimal en el cable. Nunca `float` ni `Number()`. Cada línea se redondea una vez y cada total es la suma exacta de sus líneas. El cálculo tiene un solo dueño, que también calcula lo que la pantalla muestra mientras se escribe.
- **B9. Migraciones sólo hacia adelante.** Nunca edites una ya aplicada. El servidor no migra al arrancar y se niega a servir con otro esquema. Tras cambiar el esquema, regenera lo que deriva de él y versiónalo en el mismo cambio.
- **B10. Un trigger protege un invariante o reserva algo atómico** (un correlativo, una serie). No esconde un flujo de negocio ni una autorización.

## 2. Transacciones y concurrencia

- **B11. Una transacción por request,** abierta en la entrada ya con su contexto, `READ ONLY` en lecturas. El handler confirma de forma explícita y soltarla revierte. Dos escrituras que deben ir juntas van siempre en la misma.
- **B12. Bloquear y después leer.** En una escritura, bloquea primero las filas de las que depende la decisión (`FOR SHARE`, `FOR UPDATE`, `FOR NO KEY UPDATE`) y lee sus hechos en la sentencia siguiente. Leídos en la sentencia del bloqueo, PostgreSQL puede entregar la fila nueva con los permisos viejos.
- **B13. La transacción no espera a la red.** El cuerpo llega completo antes de abrirla. Una llamada externa va con la transacción cerrada: autoriza, cierra, llama, vuelve a entrar y **vuelve a comprobar**.
- **B14. Orden y límites.** Bloquea siempre en el mismo orden. La conexión fija `lock_timeout`, `statement_timeout` e `idle_in_transaction_session_timeout`. Deadlock, fallo de serialización y espera vencida (`40P01`, `40001`, `55P03`) son 409 `conflict`: "Otra operación cambió estos datos; reintenta."
- **B15. Correlativos:** `UPDATE … SET n = n + 1 … RETURNING` dentro de la transacción que usa el número. Dos no toman el mismo y el que se revierte lo devuelve.
- **B16. Idempotencia.** Toda escritura que crea dinero, documentos o envíos recibe del cliente una `request_key`, única por empresa. Repetirla devuelve el mismo resultado, nunca otro.
- **B17. Comprueba lo que tocaste.** Un `UPDATE` o `DELETE` que no afecta filas es un 404. Responde con la fila que devuelve `RETURNING`, sin releerla.

## 3. Autorización

- **B18.** Siempre en el servidor y **declarada en la ruta**: ningún handler existe sin su requisito.
- **B19.** Una política con un método por operación, que aplica todas sus reglas juntas. El handler carga los hechos y pregunta **una vez**; nunca aplica un subconjunto.
- **B20.** Permisos `dominio.view` y `dominio.manage`, con `manage ⇒ view` (donde ya hay otro catálogo aceptado, se respeta). No hay permiso por botón, campo o pestaña, y sólo se añade uno más específico con evidencia operativa. Jamás autorices por nombre o código de rol. Nadie otorga lo que no tiene.
- **B21.** El método que protege la mutación es el mismo que calcula el `can_*` que viaja a la UI.
- **B22.** Lo ajeno no existe: a quien no pertenece se le responde 404, igual que si el recurso no existiera. Al suspendido, 403.

## 4. Contrato y errores

- **B23. Parse, don't validate.** La entrada se deserializa a tipos que sólo existen válidos, con sus límites dentro del tipo y los campos desconocidos rechazados. El error señala el campo con un JSON Pointer.
- **B24. Un sobre, un enum.** `{ "error": { "code", "message", "pointer" } }`. `code` pertenece a un enum cerrado; cada código tiene un solo estado HTTP; `message` va en español y es seguro de mostrar. La causa interna va sólo al log, en la línea de la request y con su id.
- **B25. Constraints por nombre.** Nunca interpretes el texto de un error de la base. Un constraint que no reconoces es un 500, no un mensaje filtrado.
- **B26. Un contrato.** Los tipos del cable se definen una vez y el cliente los recibe generados. Cambiar el contrato actualiza su documento, su definición y lo generado en el mismo commit.
- **B27.** Fechas en RFC 3339, montos como texto decimal y códigos externos como texto: nunca se convierten a entero.

## 5. Exterior y segundo plano

- **B28. Cola con lease.** El trabajo se encola en la misma transacción que el hecho. El worker lo toma con `FOR UPDATE SKIP LOCKED` y un lease que vence, trabaja sin transacción abierta y cada escritura vuelve a entrar con su lease: uno vencido y tomado por otro ya no escribe.
- **B29. Marca antes de enviar.** Un envío sin respuesta registrada queda `unknown`: se consulta, no se reenvía a ciegas. Nada se concluye que el sistema externo no haya dicho de ese mismo documento. Lo que no se resuelve solo pasa a una persona.
- **B30. Firmar o generar una vez.** Se guarda exactamente lo firmado, y ningún reintento lo regenera.
- **B31.** Toda llamada externa tiene tiempo límite. Sin servicio: 503 con `Retry-After`. Los reintentos retroceden duplicando la espera, con tope.
- **B32.** Lo pesado (PDF, OMR, imágenes) corre fuera de la request o en un proceso local acotado y sin credenciales.

## 6. Seguridad

B34 a B37 describen el diseño para trabajo nuevo. En un proyecto existente no sustituyas a su dueño de autenticación: extiéndelo.

- **B33. Secretos.** Una contraseña, un token, una cookie, una clave o un certificado jamás aparecen en un log, un error, una respuesta ni en datos de página. Sus tipos no se serializan; en reposo van sellados y atados a su fila y a su uso; en memoria se borran al soltarlos.
- **B34. Contraseñas.** argon2id con parámetros OWASP, fuera del runtime async y tras un semáforo que acota la memoria. Si la cuenta no existe se verifica igual un hash señuelo: el error es único.
- **B35. Sesiones opacas.** Un token aleatorio de 32 bytes; en la base sólo su `sha256`. Cookie `__Host-` con `Secure`, `HttpOnly` y `SameSite=Lax`. Vencen por inactividad y por vida absoluta; cambiar la clave borra las demás.
- **B36. CSRF.** Toda request que no sea GET ni HEAD exige `Sec-Fetch-Site` propio u `Origin` igual al origen público. Los cuerpos son JSON.
- **B37. Freno.** Cada intento se reserva **antes** de verificar. Pasado el límite: 429 con `Retry-After`.
- **B38. Superficies públicas.** Un DTO explícito por endpoint público; nunca una vista ni un modelo de administración. Un enlace público es un token firmado o guardado como hash, de un solo uso cuando concede algo.
- **B39. Código.** Sin `unsafe`. Sin `unwrap` ni `expect` fuera de los tests y del arranque. Nada bloqueante dentro de async. Si falta configuración, falla el arranque, no la primera request.

## 7. Rendimiento

- **B40.** Cada request tiene un presupuesto de sentencias escrito. Cero N+1: lote con `= ANY($1)`, join o agregado lateral sólo sobre la página.
- **B41.** Toda lista que puede crecer se pagina por cursor (clave de orden más `code`), con tamaño fijo y `LIMIT n + 1`. Se filtra y pagina la cabecera antes de armar su detalle.
- **B42.** Índices para las rutas reales de búsqueda y filtro. Lo pendiente tiene un índice parcial y nunca se busca recorriendo la historia.
- **B43.** Sin caché, memoización ni concurrencia añadida sin una medida que lo pida. Una medición declara método, datos y lo que no demuestra.
- **B44.** Recursos acotados: tamaño del pool, cuerpo máximo, tiempo por request y un semáforo para lo caro.

## 8. Pruebas

- **B45.** Pocas y de alto valor. Unitarias puras en el dominio: la matriz de la política y la aritmética. Integración HTTP contra PostgreSQL real: una por familia de rutas, para el cableado, y una por invariante de seguridad o de dominio, **incluidas sus carreras** (dos requests a la vez).
- **B46.** No se prueban getters, serialización ni el framework. No se borra ni se debilita un test para que pase: la causa está en el código, o el test documenta una regla.
- **B47.** Los tests usan una base desechable propia, nunca la de desarrollo. CI nunca llama a un servicio externo real: usa un cliente falso.

## 9. Cierre

Corre los checks que define el proyecto (su `AGENTS.md`, sus scripts, su CI), no una lista genérica, y no instales herramientas para cumplir. Antes de entregar, repasa:

- [ ] El permiso está en la ruta y la política se pregunta una vez.
- [ ] Cada invariante nuevo es un constraint con nombre, traducido a un código de error.
- [ ] Una sola transacción, ninguna llamada de red dentro, y lo que decide se bloqueó antes de leerse.
- [ ] Un `UPDATE` o `DELETE` sin filas responde 404.
- [ ] La escritura que crea dinero o documentos es idempotente por `request_key`.
- [ ] Ninguna consulta dentro de un bucle; toda lista que crece está paginada.
- [ ] Ningún secreto ni campo interno en respuestas, logs o datos de página.
- [ ] Contrato, documento y tipos generados cambiaron en el mismo commit.
- [ ] Hay una prueba HTTP por invariante nuevo, con su carrera si existe.
- [ ] Todos los checks del proyecto están en verde.

## Referencias

- `references/postgres.md` — plantillas SQL: tabla, nombres, RLS, guardias, invariantes al COMMIT, vistas, correlativos, cola, cursor, migraciones.
- `references/rust-axum-sqlx.md` — el estilo de core-rs: lints, tipos validados, tabla de rutas, handler, errores, sqlx, pruebas y checks.
- `references/sveltekit-kysely.md` — faztore y coedula: flujo de capas, acciones, repositorios y cierre.
- `references/laravel-php.md` — aeduca, fact y see-php: dueños existentes, Actions, datos y cierre.
