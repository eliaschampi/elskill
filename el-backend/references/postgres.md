# PostgreSQL: el esquema que protege

Plantillas tomadas o adaptadas de las migraciones y consultas de core-rs. Copia la forma; los nombres son de ese proyecto.

**Contenido:** 1. Tabla tipo · 2. Nombres · 3. Aislamiento por empresa · 4. Guardia que bloquea antes de mirar · 5. Invariante al COMMIT · 6. Hechos y vistas · 7. Correlativos · 8. Idempotencia · 9. Cola con lease · 10. Listas por cursor · 11. Índices · 12. Funciones que cruzan empresas · 13. Migraciones

## 1. Tabla tipo

```sql
-- V2 · fase 4 (TASK.md D1): el turno, y el libro que se deriva de los hechos.
--
-- La caja es de cada cajero: un turno abierto a la vez, en una sede activa, con
-- el fondo que declara como su primer hecho. El dinero no se guarda en ningún
-- saldo: `cash_movements` lo deriva de los hechos.

CREATE TABLE cash_shifts (
    code                 uuid          PRIMARY KEY DEFAULT uuidv7(),
    tenant_code          uuid          NOT NULL REFERENCES tenants (code),
    branch_code          uuid          NOT NULL,
    cashier_account_code uuid          NOT NULL,
    opening_fund         numeric(14,2) NOT NULL,
    opened_at            timestamptz   NOT NULL DEFAULT now(),
    closed_at            timestamptz,
    CONSTRAINT cash_shifts_code_tenant_uq UNIQUE (code, tenant_code),
    CONSTRAINT cash_shifts_branch_fk FOREIGN KEY (branch_code, tenant_code)
        REFERENCES branches (code, tenant_code),
    CONSTRAINT cash_shifts_cashier_fk FOREIGN KEY (tenant_code, cashier_account_code)
        REFERENCES memberships (tenant_code, account_code),
    CONSTRAINT cash_shifts_fund_check CHECK (opening_fund >= 0)
);

-- Un turno abierto por cajero. También lista los turnos abiertos de la empresa.
CREATE UNIQUE INDEX cash_shifts_one_open_uq ON cash_shifts (tenant_code, cashier_account_code)
    WHERE closed_at IS NULL;
```

Lo que enseña:

- La cabecera dice la regla y a qué ítem de `TASK.md` pertenece. Los comentarios de SQL van en español, como la spec.
- `UNIQUE (code, tenant_code)` existe para que los hijos referencien con FK compuesta: apuntar a una fila de otra empresa es imposible por construcción.
- "A lo sumo uno abierto" es un índice único parcial, no una comprobación en la aplicación.
- El estado es una columna con significado (`closed_at`), y la fila nunca se borra.

## 2. Nombres

| Objeto | Forma | Ejemplo |
| --- | --- | --- |
| PK | `code uuid DEFAULT uuidv7()` | — |
| Columna FK | `<entidad>_code` | `branch_code` |
| Constraint FK | `<tabla>_<destino>_fk` | `cash_shifts_branch_fk` |
| UNIQUE o índice único | `<tabla>_<regla>_uq` | `cash_shifts_one_open_uq` |
| CHECK | `<tabla>_<regla>_check` | `cash_shifts_fund_check` |
| Índice | `<tabla>_<uso>_ix` | `charges_pending_ix` |
| Guardia o trigger | `<tabla>_<regla>` | `memberships_keep_owner` |
| Vista | Lo que deriva, en plural | `cash_movements`, `member_facts` |

Todo constraint lleva nombre: es lo que la aplicación traduce a un código de error.

## 3. Aislamiento por empresa

```sql
CREATE FUNCTION app_tenant() RETURNS uuid
    LANGUAGE sql STABLE PARALLEL SAFE
    AS $$ SELECT nullif(current_setting('app.tenant_code', true), '')::uuid $$;

ALTER TABLE cash_shifts ENABLE ROW LEVEL SECURITY, FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON cash_shifts
    USING (tenant_code = app_tenant()) WITH CHECK (tenant_code = app_tenant());

GRANT SELECT, INSERT ON cash_shifts TO core_app;
```

- Una política por tabla. `FORCE` la aplica también al dueño.
- El pool hace `SET ROLE core_app` al conectar: un rol sin `BYPASSRLS` y dueño de nada.
- La transacción fija el contexto con `set_config('app.tenant_code', $1, true)`: local a ella, no se filtra a la siguiente.
- Los `GRANT` son el mínimo: sólo `INSERT` en tablas de hechos, `UPDATE` sólo en columnas mutables, nunca `UPDATE` ni `DELETE` en auditoría.
- El SQL de la aplicación filtra igual por `tenant_code`: RLS es la segunda barrera, no la única.

## 4. Guardia que bloquea antes de mirar

```sql
-- Bloquear la sede antes de mirarla ordena este INSERT con quien la desactiva.
CREATE FUNCTION cash_shifts_branch_active() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM 1 FROM branches
      WHERE code = NEW.branch_code AND tenant_code = NEW.tenant_code AND is_active
      FOR SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'la sede no existe o está inactiva'
            USING ERRCODE = 'check_violation', CONSTRAINT = 'cash_shifts_branch_active';
    END IF;

    RETURN NEW;
END
$$;

CREATE TRIGGER cash_shifts_branch_active BEFORE INSERT ON cash_shifts
    FOR EACH ROW EXECUTE FUNCTION cash_shifts_branch_active();
```

El `FOR SHARE` ordena esta escritura con quien cambia la fila mirada. `CONSTRAINT = '…'` le da a la aplicación un nombre estable que traducir.

## 5. Invariante al COMMIT ("al menos uno")

```sql
CREATE FUNCTION memberships_keep_owner() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    affected uuid := COALESCE(NEW.tenant_code, OLD.tenant_code);
BEGIN
    -- Dos transacciones en que cada propietario suspende al otro verían, cada una,
    -- al otro todavía activo (write skew). El candado serializa la verificación por
    -- empresa hasta el COMMIT, y la consulta siguiente ya ve lo confirmado.
    PERFORM pg_advisory_xact_lock(hashtextextended('memberships_keep_owner:' || affected::text, 0));

    IF NOT EXISTS (SELECT 1 FROM memberships m
                     JOIN roles r ON r.code = m.role_code AND r.tenant_code = m.tenant_code
                    WHERE m.tenant_code = affected AND m.status = 'active' AND r.kind = 'owner') THEN
        RAISE EXCEPTION 'la empresa % debe conservar al menos un propietario activo', affected
            USING ERRCODE = 'check_violation', CONSTRAINT = 'memberships_keep_owner';
    END IF;

    RETURN NULL;
END
$$;

CREATE CONSTRAINT TRIGGER memberships_keep_owner
    AFTER INSERT OR UPDATE OR DELETE ON memberships
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION memberships_keep_owner();
```

Diferido: una transferencia (dar a uno, quitar a otro) es válida dentro de la transacción y la regla se comprueba al confirmar. Una regla sobre un conjunto de filas necesita su candado, o dos transacciones la rompen juntas.

## 6. Hechos y vistas

```sql
-- Con signo: lo que entra suma y lo que sale resta, así lo esperado es su suma.
CREATE VIEW cash_movements WITH (security_invoker = true) AS
SELECT s.tenant_code, s.code AS shift_code, 'fund'::text AS kind, s.opening_fund AS amount,
       s.opened_at AS at
  FROM cash_shifts s;

GRANT SELECT ON cash_movements TO core_app;
```

- Ningún saldo se guarda: la vista lo deriva de los hechos y no puede discrepar de ellos.
- `security_invoker = true` hace que RLS se aplique a quien consulta.
- Cada hecho nuevo (cobro, reverso, egreso) añade su rama a la vista; la tabla del hecho sólo recibe `INSERT`.
- Al reemplazar una vista, las columnas nuevas van al final.

## 7. Correlativos

```sql
UPDATE branch_series SET last_number = last_number + 1
 WHERE branch_code = $1 AND kind = $2 AND tenant_code = $3
RETURNING code, series, last_number AS number
```

En la misma transacción que crea el comprobante. La fila queda bloqueada hasta el COMMIT: dos no toman el mismo número y uno que se revierte lo devuelve.

## 8. Idempotencia

```sql
CREATE TABLE payments (
    -- …
    request_key uuid NOT NULL,
    CONSTRAINT payments_request_key_uq UNIQUE (tenant_code, request_key)
);
```

El handler bloquea lo que serializa a los escritores (el turno del cajero), busca la `request_key` y, si existe, devuelve esa venta con 200. El constraint es la última barrera: su violación, de dos envíos idénticos a la vez, se traduce a 409 `conflict`.

## 9. Cola con lease

```sql
CREATE FUNCTION cpe_job_claim(p_seconds integer)
    RETURNS TABLE (job uuid, lease uuid)
    LANGUAGE sql VOLATILE SECURITY DEFINER
    SET search_path = public, pg_temp
    AS $$
    UPDATE cpe_jobs
       SET lease = uuidv7(), leased_until = now() + make_interval(secs => p_seconds),
           attempts = attempts + 1
     WHERE code = (SELECT code FROM cpe_jobs
                    WHERE run_after <= now() AND (leased_until IS NULL OR leased_until < now())
                    ORDER BY run_after, code
                    LIMIT 1
                      FOR UPDATE SKIP LOCKED)
    RETURNING code, lease
$$;
```

El worker reserva en una sentencia propia, trabaja sin transacción abierta y cada escritura vuelve a entrar comprobando su lease (`WHERE code = $1 AND lease = $2 FOR UPDATE`). Sin fila, el lease se perdió y no escribe.

## 10. Listas por cursor

```sql
SELECT code, name, doc_number
  FROM customers
 WHERE tenant_code = $1 AND archived_at IS NULL
   AND ($2::text IS NULL OR (lower(name), code) > ($2, $3::uuid))
 ORDER BY lower(name), code
 LIMIT $4          -- tamaño de página + 1
```

El cursor es la clave de orden más `code` de la última fila, opaco para el cliente. Si vuelven `n + 1` filas hay otra página: se corta a `n` y se devuelve el cursor. Nunca `OFFSET`.

## 11. Índices

- Uno por cada ruta real de búsqueda o filtro; ninguno "por si acaso".
- Lo pendiente tiene índice parcial (`WHERE settled_at IS NULL`): lo ya resuelto no se recorre.
- El índice único parcial expresa "uno vivo a la vez" (`WHERE closed_at IS NULL`, `WHERE archived_at IS NULL`).
- Búsqueda de texto: una sola función de normalización (minúsculas, sin tildes) que usan todas las búsquedas. Un índice de texto o trigram entra sólo cuando el volumen medido o esperado lo pide.

## 12. Funciones que cruzan empresas

Lo que necesita ver más de una empresa pasa por una función `SECURITY DEFINER` acotada, nunca por abrir RLS:

```sql
REVOKE ALL ON FUNCTION cpe_job_claim(integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION cpe_job_claim(integer) TO core_app;
```

Siempre con `SET search_path = public, pg_temp`, con `REVOKE … FROM PUBLIC` y devolviendo sólo lo que su caso de uso requiere.

## 13. Migraciones

- Archivos `NNNN_<tema>.sql`, sólo hacia adelante. Una migración commiteada no se edita: hay bases con su checksum.
- Las aplica un comando explícito con la conexión dueña (`server migrate`). El servidor no migra al arrancar y se niega a servir si la versión aplicada no es la última que trae.
- Cada tabla nueva llega completa: constraints con nombre, RLS, política y `GRANT` mínimos.
- Después, regenera lo que deriva del esquema (`cargo sqlx prepare --workspace -- --all-targets`, `pnpm run db:generate`) y versiónalo.
- La base de desarrollo no se usa para probar una dirección sin terminar: los tests crean la suya.
