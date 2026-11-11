---
name: el-architecture
description: Arquitectura y método de trabajo de Elias (referencia viva core-rs). Úsala antes de cualquier tarea de código en sus proyectos y siempre que haya que decidir dónde vive una regla, crear o partir un módulo, añadir una capa, una dependencia o una tabla, planificar un vertical, refactorizar, revisar una arquitectura o iniciar un proyecto. Fija el dueño único de cada regla, las capas prohibidas, el protocolo de sesión, cuándo detenerse a preguntar y qué significa terminado. Para servidor y SQL añade el-backend; para pantallas, el-design.
---

# EL · Arquitectura

Así decide y construye Elias: pocas piezas, un dueño por regla y garantías que comprueba la máquina. Esta skill es la entrada de toda tarea de código; `el-backend` y `el-design` la dan por leída. `core-rs` es la referencia viva: cuando dudes de cómo se ve una regla aplicada, míralo como evidencia, no como plantilla.

## Núcleo

1. **Manda el proyecto.** Su `AGENTS.md` y su `docs/SPEC.md` ganan a esta skill, y esta skill gana a tus costumbres. Si chocan, obedece al proyecto y dilo.
2. **Prioridad, no invertir:** corrección → legibilidad → consistencia con el repositorio → rendimiento → simplicidad.
3. **Un dueño por regla.** Cada regla, dato y decisión vive en un solo lugar; lo demás lo consulta o lo deriva.
4. **Que lo compruebe la máquina.** Un tipo, un constraint, un lint o un tipo generado valen más que una convención que dependa de la revisión.
5. **No adivines.** Lee el código, sus tests y el fuente de la dependencia antes de usarlos. Ante dinero, identidad, permisos o migraciones, detente y pregunta.
6. **Nada especulativo.** Ni capas, ni opciones, ni rutas, tablas o permisos "para después".
7. Identificadores en inglés; documentos, copy y mensajes al usuario en español; los comentarios siguen el idioma del archivo vecino.

## 1. Autoridad: cada verdad tiene un documento dueño

| Fuente | Es dueña de |
| --- | --- |
| `AGENTS.md` | Las reglas de trabajo de todo agente. `CLAUDE.md` sólo lo importa |
| `docs/SPEC.md` | La ley permanente: producto, dominio, datos y arquitectura |
| `docs/API.md` o `docs/CONTRACT.md` | El contrato en el cable |
| `docs/STATUS.md` | Hechos verificados, con números reales. Lo demás se anota "sin verificar" |
| `TASK.md` | El ítem activo y su cola. Las ideas se anotan aquí; no se construyen |
| El código de la rama principal | La línea base aceptada y sus patrones |

- **A1.** El código manda sobre la spec al decir *qué existe*; la spec manda sobre la tarea al decir *qué debe ser*. Una tarea no deroga la spec en silencio, y ningún documento declara hecho lo que el código no contiene.
- **A2.** Si dos fuentes chocan, inspecciona el código y la evidencia, informa el conflicto y corrige lo mínimo coherente. No elijas en silencio.
- **A3.** No crees specs, roadmaps ni planes paralelos. Una regla durable se fusiona en su dueño; un refactor de documentos audita que no se pierda ninguna regla válida.
- **A4.** Si al proyecto le falta alguno, usa su equivalente (`README.md`, `docs/Architecture.md`, `task.md`). Créalo sólo si te lo piden, con `references/doc-system.md`.

## 2. Protocolo de sesión (en este orden)

Una pregunta o una edición trivial se resuelven directo; el protocolo es para el trabajo no trivial. Las reglas `A` valen siempre.

1. **Ubícate.** `git status` y `git log --oneline -15`. Lee `AGENTS.md`. Tu trabajo es lo que pidió el usuario; si no pidió nada concreto, el primer ítem sin marcar de `TASK.md`. No elijas otro.
2. **Investiga antes de escribir.** Lee línea por línea el flujo afectado, sus tests y quién lo produce y lo consume. Busca todos los callers de lo que vas a tocar: el inventario de un chat no es el mapa del repositorio. Lee la sección de `SPEC.md` que lo gobierna y el fuente de la dependencia cuya API usarás (`~/.cargo/registry/src`, `node_modules`, `vendor`). Si la spec nombra un proyecto hermano como evidencia, míralo.
3. **Define el resultado observable.** Quién lo usa, qué ve al terminar y cómo falla. Si no cabe en dos líneas, falta investigar o falta preguntar.
4. **Asigna dueños** con la tabla de §3 antes de crear un archivo.
5. **Construye el vertical entero** (§6) en el corte más pequeño que funcione completo.
6. **Verifica** con los checks del propio proyecto. Todos en verde.
7. **Cierra.** Actualiza los documentos dueños, marca el ítem y entrega el informe de §9.

- **A5.** Trabaja para sobrevivir a un corte: un ítem a la vez y, al terminarlo, checks y registro. El estado vive en `TASK.md` y en git, no en la conversación.
- **A6.** Git: commit sólo cuando el proyecto o el usuario lo piden, y sólo de tus rutas (`git add <rutas>`, nunca `-A`). Nunca `push`, cambio de rama ni reescritura de historia sin orden expresa.
- **A7.** Ahorra contexto: lee la sección que necesitas, no el repositorio; no releas lo que no cambió; usa `rtk` para salidas largas si está instalado. Delega en subagentes sólo trabajo independiente y largo, y nunca pongas dos agentes sobre los mismos archivos.

## 3. Dónde vive cada cosa

Antes de crear un archivo, una función o una tabla, busca el dueño aquí. Si ya existe, extiéndelo; si la regla aparece en dos sitios, sobra uno.

| Si es… | Su dueño es… | Y nunca… |
| --- | --- | --- |
| Un invariante estructural: unicidad, pertenencia, rangos, "al menos uno", transiciones de estado | PostgreSQL: FK compuesta, `UNIQUE`, `CHECK` con nombre, trigger diferido | se vuelve a comprobar en la aplicación, que sólo traduce el constraint por su nombre |
| Una regla o un cálculo puro: impuestos, redondeo, máquina de estados | El módulo de dominio: tipos y funciones puras, sin I/O | vive en un handler, en un componente o repartida en SQL suelto |
| Una decisión de autorización | Una sola política en el servidor, un método por operación, declarada en la ruta | por nombre de rol, repartida entre handlers o sólo en la UI |
| La validez de una entrada | Un tipo que sólo existe válido y se construye en el borde (*parse, don't validate*) | comprobaciones sueltas más adentro |
| El flujo de una request: cargar hechos, preguntar, escribir, auditar, confirmar | El handler o la acción del recurso, con su SQL al lado (donde ya hay repositorios aceptados, el repositorio del agregado) | un servicio o repositorio que sólo reenvía |
| Los tipos del cable | Una definición; el cliente los recibe generados | DTO escritos a mano en los dos lados |
| Lo que el usuario puede ver o hacer | Datos y capacidades `can_*` que calcula el servidor con el mismo método que protege la mutación | reglas reimplementadas en la UI |
| Un valor derivable: total, saldo, diferencia, estado compuesto | Se deriva: vista, función o `$derived` | se guarda aparte, donde puede discrepar |
| Una garantía transversal: tenancy, transacción, CSRF, límites | Un módulo, cerrado por tipo, lint o RLS | una convención que cada handler debe recordar |
| Presentación e interacción | Componentes de UI sobre Lumi | reglas de dominio en condicionales visuales |
| Marca, navegación, avisos, cliente HTTP, sesión | Un archivo dueño cada uno | un segundo sistema "sólo para esto" |

## 4. Forma: qué se construye y qué no

- **A8. Plano y por responsabilidad.** Un archivo por recurso, con sus handlers y su SQL. Nace un submódulo cuando aparece una segunda responsabilidad cohesiva (`cash/closing.rs`), no para bajar líneas. Las carpetas nombran responsabilidades, nunca tipos de archivo (`services/forms/`, `modules/`, `Domains/`).
- **A9. Toda abstracción pasa tres pruebas, o no se crea.**
  1. *Borrado:* si la borro, ¿la complejidad reaparece en varios callers? Si sólo desaparece, era un reenvío.
  2. *Dos adaptadores:* ¿hay hoy dos implementaciones reales detrás de la interfaz? Con una sola, la costura es hipotética.
  3. *Misma razón de cambio:* ¿los usos comparten la regla o sólo se parecen? Lo parecido con motivos distintos se queda separado.
- **A10. Módulos profundos.** Mucho comportamiento detrás de una interfaz pequeña; el test cruza la misma interfaz que el caller. Si para probar hay que mirar por dentro, la forma está mal.
- **A11. Prohibido:** repositorios o servicios que sólo reenvían · traits o interfaces con una sola implementación · DTO que duplican o renombran · clases base y helpers cargados de opciones · CQRS, event sourcing y Clean/Hexagonal "por arquitectura" · contenedores de inyección · un segundo sistema de auth, UI, estado, validación o cliente HTTP · barrels de compatibilidad, facades temporales y rutas `deprecated` · rutas, pestañas, tablas, permisos o acciones vacías para el futuro.
- **A12. Corte atómico.** Un refactor mueve o borra el original en el mismo cambio y actualiza a todos los callers. Nunca dos implementaciones en paralelo. Si el corte no cabe entero, no se empieza.
- **A13. Un camino de escritura** por responsabilidad. Una consecuencia obligatoria es una llamada directa dentro de la misma transacción; los eventos son sólo para consumidores independientes.
- **A14. Hazlo imposible, no prohibido.** Cierra cada garantía con la máquina: un extractor genérico sin el cual el handler no compila; un lint que rechaza abrir transacciones fuera de su módulo; un tipo `Secret` que no implementa `Serialize`; un mapa exhaustivo que rompe el build cuando nace un código de error.
- **A15. Dependencias.** Una dependencia de runtime nueva es una decisión de arquitectura: detente y pregunta. Antes comprueba que la plataforma o lo instalado no lo resuelven. Activa sólo las features que usas.
- **A16. El porqué vive junto a la regla.** Cada módulo abre diciendo qué regla guarda y quién la protege; los comentarios explican por qué, no qué hace la línea.
- **A17. Nunca degrades para avanzar.** No se desactiva una guardia (RLS, CSRF, un lint, un freno) ni "temporalmente"; no se borra ni debilita un test para que pase; no se edita una migración ya aplicada.

## 5. Trabajo nuevo: la arquitectura por defecto

Un proyecto existente conserva su stack y sus dueños: el objetivo es **terminar** su arquitectura, no sustituirla. Un proyecto o un módulo nuevo parte de `core-rs` (detalle y arranque en `references/blueprint.md`):

- `domain` puro (tipos validados, política, contrato, aritmética) · `server` (HTTP, sesiones, SQL) · `migrations/` SQL-first · `web/` SPA. Nada más.
- La empresa va en la URL, nunca en la sesión. Aislamiento doble: por tipo en el código y por RLS en la base.
- Una transacción por request, abierta en la entrada con su contexto; el permiso se declara en la tabla de rutas.
- El contrato se define una vez y el cliente lo recibe generado.
- Un sobre de error, un enum de códigos, un estado HTTP por código.
- Los hechos (dinero, stock, auditoría) son inmutables; los saldos se derivan.
- El rendimiento es un presupuesto escrito y medido.

## 6. Vertical y alcance

- **A18.** El alcance es el ítem activo, acotado por su **resultado observable**, no por una tabla ni un controller.
- **A19.** Un vertical está completo cuando funcionan juntos: entrada y navegación · operación principal · autorización en el servidor · persistencia con sus invariantes · respuesta en lista y detalle · estados vacío, de validación y de fallo · checks en verde. Migraciones, CRUD y tests no son, por sí solos, un vertical.
- **A20.** Una capacidad adyacente sin la que el flujo no funciona **no** amplía el alcance: revisa la tarea y dilo antes de seguir. Un módulo decorativo sí lo amplía: anótalo en `TASK.md` y no lo construyas.
- **A21.** Orden que evita retrabajo: esquema y constraints → reglas puras → handler y contrato → cliente generado → pantalla → pruebas de los invariantes → documentos. Un cambio de contrato actualiza su documento, su definición y lo generado en el mismo commit.

## 7. Detente y pregunta

Para y consulta al usuario, con el hallazgo en una línea y tu recomendación, cuando:

- algo choca con `SPEC.md` o no sabes qué decidir: no improvises arquitectura;
- un término del dominio tiene dos significados operativos, o un campo o estado no tiene dueño confirmado;
- la evidencia contradice la tarea;
- un invariante no se puede proteger con claridad;
- duplicarías un dueño o un patrón que ya existe;
- parece necesaria una dependencia de runtime nueva, o Lumi no tiene el contrato público que necesitas;
- el flujo mostraría datos de otra empresa, sede o persona sin autorización confirmada;
- un check requerido falla y la causa no está en tu cambio.

Nunca adivines sobre identidad, autorización, pagos, caja, comprobantes ni migraciones. En una ambigüedad menor y reversible de interfaz, usa el patrón existente más simple y sigue.

## 8. Decisiones y revisiones

- **A22.** Una decisión que no se revierte entra en `SPEC.md` como fila *Decisión | Por qué*, con quién la tomó y la fecha. Sin el porqué, el siguiente agente la deshace.
- **A23.** Un riesgo aceptado se escribe con su medida real y con lo que lo mitigará.
- **A24.** El rendimiento es un presupuesto escrito (sentencias por request, memoria, KB de JavaScript). Una medición declara método, datos y lo que **no** demuestra; una estimación se llama estimación.
- **A25. Al revisar** una arquitectura, un PR o un diff: sólo lectura salvo permiso. Cada hallazgo trae disparador, consecuencia, regla violada (`A11`, `B12`, `D6`…) y `archivo:línea`. Separa lo confirmado de lo que es pregunta. Nada de gustos de estilo ni de rendimiento especulativo.

## 9. Terminado

Nunca declares terminado algo con un check en rojo, ni una mejora que no mediste: que compile no es que funcione. El informe final dice sólo esto:

1. evidencia inspeccionada;
2. decisiones tomadas y por qué;
3. lo implementado;
4. lo omitido a propósito;
5. checks ejecutados, con su resultado real;
6. incertidumbre de dominio que queda.

## Referencias

- `references/blueprint.md` — la arquitectura de referencia completa: forma, ciclo de una request, puertas, presupuestos, variantes y arranque. Léela al iniciar un proyecto o un módulo nuevo.
- `references/doc-system.md` — qué contiene cada documento dueño y su esqueleto. Léela al crear o reorganizar `AGENTS.md`, `SPEC.md`, `STATUS.md` o `TASK.md`.
