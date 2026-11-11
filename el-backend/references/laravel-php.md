# Laravel y PHP (aeduca, fact, see-php)

Manda el `AGENTS.md` y el `docs/SPEC.md` de cada proyecto; esto resume lo que comparten.

## Laravel + Inertia + Svelte (aeduca, fact)

### Los dueños que ya existen

| Responsabilidad | Dueño |
| --- | --- |
| Credenciales de acceso | `AuthAccount` |
| Identidad del personal | `User` |
| Autorización | Roles, concesiones directas, alcance y `PermissionDependency` (`PermissionResolver` en fact) |
| Sede de la sesión | `BranchContext` |
| Escritura de un agregado, transacción o invariante real | Un `Action` enfocado |
| Normalización y forma de la entrada | `FormRequest` |
| Componer consultas, actions y la respuesta Inertia | El controller |
| Interacción y presentación | Svelte sobre Lumi |

Extiende estos dueños. No añadas un segundo sistema de autenticación, un paquete de autorización, un store de permisos o de sede en el cliente, una capa de repositorios, `Services/` genérica, `Domains/`, un framework de módulos ni CQRS.

### Forma

- Un dueño y un camino de escritura por responsabilidad.
- `Action` para la escritura de un agregado, una transacción o un invariante real. El alta o la edición de una fila simple y validada va directa con Eloquent.
- Prohibido: repositorios genéricos, services que lo hacen todo, Actions base, librerías de DTO que renombran arrays, wrappers de consulta para consultas simples, event sourcing.
- Subcarpetas y abstracciones compartidas sólo cuando el contenido actual lo demuestra. Un archivo cohesivo no se parte para bajar líneas.
- Una consecuencia obligatoria es una llamada directa. Los eventos exigen consumidores independientes; un observer nunca esconde un flujo crítico.

### Datos

- PK UUID `code`; FK `<entidad>_code`. Ningún identificador técnico codifica año, sede, nivel o estado.
- Relaciones con FK o tabla intermedia; nunca arrays, JSON ni polimorfismo manual `type`/`code`.
- PostgreSQL es dueño de FK, UNIQUE y CHECK con nombre.
- Un read model estable que usan listas, búsquedas, perfiles o reportes es una vista SQL con nombre; Laravel sigue autorizando, acotando, filtrando y paginando.
- Una generación o reserva atómica (un código correlativo) es una función SQL enfocada, explicable y probada.
- El CRUD simple se queda en Eloquent: no envuelvas cada insert en una vista o función ni escondas flujos en SQL.
- Las escrituras de negocio sobre varias tablas son transaccionales.
- Sin soft delete por defecto, y jamás en lo fiscal.
- Nunca autorices por nombre ni por código de rol. Autorización, pagos y caja no se esconden en triggers.

### Permisos y rendimiento

- `dominio.view` y `dominio.manage`; `manage` incluye `view` por el dueño de dependencias que ya existe. Ningún permiso por botón, campo o pestaña.
- El autoservicio de una persona se autoriza por identidad y pertenencia, no concediéndole un permiso administrativo.
- Sin N+1 ni eager loading innecesario. Las listas cargan los campos que muestran y resúmenes acotados; el detalle compone un perfil con consultas enfocadas.
- Sin caché persistente de permisos, sedes o catálogos sin medición.

### Base de datos y cierre

```bash
php artisan migrate:fresh --seed --env=testing   # tras cambiar esquema o seeds
composer run format
composer run check
pnpm run build
```

El desarrollo y los tests usan la base `<proyecto>_test`. Nunca `migrate:fresh` contra la base principal, ni migrarla para probar una dirección sin terminar.

## PHP sin framework: motor sin estado (see-php)

1. **Sin estado.** Ni base de datos, ni colas, ni sesiones, ni disco de negocio. Si algo necesita recordar, es del core.
2. **Firmar una vez.** Ninguna ruta regenera un XML ya firmado; enviar sólo transporta bytes que se verifican antes de salir.
3. **Códigos externos como texto.** Nunca `(int)` sobre un código. Interpretarlo es trabajo del core.
4. **Secretos** con `#[SensitiveParameter]`: viven una request y jamás tocan un log, un error ni el disco.
5. **Contrato estricto.** Todo campo pasa por un único lector de entrada: claves desconocidas rechazadas, montos como string, errores con JSON Pointer.
6. **Forma.** `declare(strict_types=1)`, clases `final` y `readonly`, sin framework ni capas especulativas. La librería externa se importa sólo en los módulos que la envuelven.
7. Antes de tocar plantillas, firma o transporte, lee el código de la librería en `vendor/`: su comportamiento real manda, su documentación no.

Pruebas y cierre:

- CI nunca llama al servicio externo: se prueba con un cliente falso.
- Un ejemplo nuevo del contrato llega con su golden. Los goldens se regeneran sólo a propósito, y su diff se revisa como un cambio fiscal.
- Una regla aprendida del servicio externo entra con su test, su fila en la spec y su evidencia en `STATUS.md`.

```bash
composer format
composer check     # pint --test · phpstan max · phpunit
```
