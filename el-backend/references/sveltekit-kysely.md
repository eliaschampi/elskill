# SvelteKit + Kysely (faztore, coedula)

Monolitos SvelteKit con PostgreSQL y Kysely. Su arquitectura ya está aceptada: el objetivo es **terminarla, no sustituirla** por la de core-rs. Manda el documento del proyecto (`docs/ARCHITECTURE.md` en coedula, `docs/Architecture.md` en faztore); esto es el resumen de lo que comparten.

## Flujo de capas

```text
ruta (+page.server.ts | +server.ts)
  → locals.can(...)                      el permiso, al entrar en cada rama sensible
  → parser del form o loader del querystring
  → service      sólo si orquesta, transacciona o comparte una regla
  → repository   SQL + mapeo a DTO, un agregado por repositorio
  → $lib/types/<dominio>
```

- **Un service no es ceremonia.** Un insert validado es parser + repository. Un `XService.create` que sólo llama a `XRepository.create` está prohibido.
- La ruta hace permiso, cableado y `fail` / `redirect`. Cero SQL en la ruta si el repositorio ya existe.
- Las carpetas nombran responsabilidades. No crees `services/forms/`, `modules/` ni estructuras Clean o Hexagonal.
- **Corte atómico:** mover o borrar el original en el mismo cambio y actualizar a todos los callers. Sin barrels de compatibilidad, sin `deprecated`, sin facade temporal. Si no cabe entero, se omite.
- Antes de editar una superficie, busca sus callers con grep.

## Cada escritura

1. `locals.can(...)` en el `load` y en cada action o endpoint. El `can()` del cliente sólo decide qué se muestra.
2. Normaliza la entrada con los helpers del proyecto (campos de formulario, trim, DNI, fechas de Lima).
3. Valida requeridos, UUID y FK **antes** de escribir.
4. Ejecuta el repositorio o el service y comprueba las filas afectadas: 404 si no tocó ninguna.
5. Más de una escritura que debe ir junta: `locals.db.transaction().execute(...)`.
6. Lo esperado responde `fail(400 | 403 | 404, { error })`, sin filtrar detalles internos.
7. Los errores de PostgreSQL se reconocen por código (`pgErrorCode`, `PG_UNIQUE_VIOLATION`, `PG_FOREIGN_KEY_VIOLATION`), nunca por su texto.
8. Jamás `password_hash` ni otro secreto en `PageData`.

## Datos

- Línea base en `database/init/*.sql`; para bases ya creadas, además `database/migrations/NNNN-descripcion.sql`.
- Después de cambiar el esquema: aplica el SQL y corre `pnpm run db:generate`. `src/lib/database/types.ts` se genera y nadie lo edita a mano.
- Al reemplazar una vista, las columnas nuevas van al final.
- Las lecturas operativas se acotan a la sede de trabajo del usuario cuando el flujo es de una sede.
- Inventario y caja: los movimientos son el libro; el estado actual se deriva o se mantiene sólo dentro de la operación del repositorio que escribe el movimiento.
- Varias líneas se procesan por lote dentro de la transacción; los bloqueos siguen siempre el mismo orden (por variante).
- Los endpoints públicos usan su propio repositorio y DTO explícitos; nunca una vista de administración.

## Permisos

Respeta el catálogo del proyecto: coedula usa `<entidad>:read|create|update|delete`, más un permiso especial sólo cuando existe la operación (`approve`, `export`). El bypass de superadministrador está centralizado: no lo reimplementes.

## Cliente

- Formularios Lumi con `use:enhance`; toast al éxito; `invalidate` con la misma clave que declaró `depends`.
- El estado de página son runes, no `writable()`.

## Cierre

```bash
pnpm run check        # faztore: svelte-check + oxlint + prettier
npm run lint:fix && npm run check    # coedula
pnpm run db:generate  # tras cambiar el esquema
pnpm test             # faztore: las suites de base usan bases desechables propias
```

Las suites de base de datos nunca usan el `DATABASE_URL` de la aplicación. En coedula la base local es `psql -d coedula`, no Docker.
