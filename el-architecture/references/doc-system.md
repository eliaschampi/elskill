# El sistema de documentos

Cinco archivos y un dueño por verdad. Créalos o reorganízalos sólo cuando el usuario lo pida; en el trabajo diario se leen y se actualizan.

## Qué va en cada uno

| Archivo | Contiene | No contiene |
| --- | --- | --- |
| `AGENTS.md` | Cómo se trabaja aquí: lectura obligatoria, decisiones que no se revierten, prohibiciones, protocolo, checks y mapa | Reglas de producto: van en SPEC |
| `CLAUDE.md` | Una línea de contexto y `@AGENTS.md` | Reglas propias |
| `docs/SPEC.md` | La ley permanente, en secciones numeradas que el código cita (`SPEC §5`) | Estado, avances, tareas |
| `docs/API.md` | Cada ruta con sus tipos y su permiso; espejo de la tabla de rutas | Decisiones |
| `docs/STATUS.md` | Hechos verificados, con fecha y número real | "Debería", planes |
| `TASK.md` | El vertical activo en ítems marcables, las brechas conocidas y las ideas pendientes | Reglas durables |

## Reglas

- SPEC abre diciendo quién manda sobre quién y la prioridad (corrección → legibilidad → consistencia → rendimiento → simplicidad).
- Una decisión del dueño lleva su fecha: "Decidido por el dueño el 2026-11-04".
- Un riesgo aceptado lleva su medida y su mitigación prevista.
- Un documento para agentes se escribe para leerse entero: corto, imperativo y con el porqué. Enruta hacia el detalle en vez de copiarlo.
- Compactar es fusionar una regla en su dueño; nunca borrar contexto válido para bajar líneas.
- Al cerrar un vertical: fusiona las reglas durables en SPEC, reemplaza los hechos de STATUS, marca o reemplaza TASK, y no dejes un roadmap que compita.

## Esqueleto de `AGENTS.md`

```markdown
# <proyecto> — reglas para cualquier agente (léelas enteras)

El único reglamento de trabajo. La ley del producto es `docs/SPEC.md`; el contrato,
`docs/API.md`; el ítem activo, `TASK.md`; la evidencia, `docs/STATUS.md`. Nada de eso se
repite aquí.

<Dos líneas: qué es el producto y su stack.>

## 1. Al empezar cada sesión (obligatorio, en este orden)
1. `git log --oneline -15` y `git status`. Rama de trabajo: `<rama>`.
2. Lee `TASK.md`: el primer ítem sin marcar es tu trabajo. No elijas otro.
3. Lee `docs/SPEC.md` y `docs/API.md`.
4. Antes de usar la API de una dependencia, lee su código fuente. No adivines firmas.

## 2. Decisiones que NO se revierten (y por qué)
| Decisión | Por qué |
| --- | --- |

## 3. Prohibido
- <Capas, atajos y sistemas paralelos que este proyecto rechaza.>

## 4. Protocolo de trabajo
1. Un ítem de `TASK.md` a la vez.
2. Al terminarlo: checks (§5), marcarlo y commit sólo de tus rutas.
3. Un cambio de contrato actualiza documento, definición y tipos generados en el mismo commit.
4. Si algo choca con `SPEC.md` o no sabes qué decidir: detente y pregunta.
5. `docs/STATUS.md` guarda sólo hechos verificados.

## 5. Checks (todos en verde antes de cada commit)
<Los comandos exactos, en un bloque.>

## 6. Mapa
<Un párrafo: qué carpeta guarda qué.>
```

## Esqueleto de `docs/SPEC.md`

```markdown
# <proyecto> — especificación

Ley permanente. Contrato: `API.md`. Hechos verificados: `STATUS.md`. Ejecución: `TASK.md`.
El código manda sobre este archivo. Este archivo manda sobre `TASK.md`.
Prioridad, no invertir: corrección → legibilidad → consistencia → rendimiento → simplicidad.

## 1. Producto        quién lo usa, qué promete, qué no es
## 2. Arquitectura    el diagrama y el mapa de archivos, una línea por archivo
## 3. <La decisión central>   por ejemplo, tenancy
## 4. Identidad y sesiones
## 5. Acceso          reglas numeradas que el servidor aplica siempre
## 6. Datos           tablas, constraints con nombre, qué se deriva
## 7. Errores         la tabla estado HTTP ↔ código
## 8. Frontend
## 9. Presupuestos    rendimiento y pruebas
```

## Esqueleto de `docs/STATUS.md`

```markdown
# <proyecto> — estado verificado

| Fecha | Hecho | Evidencia |
| --- | --- | --- |
| <fecha> | <hecho, con su número real> | <comando o archivo que lo prueba> |

## Abierto
- <Lo que falta verificar, marcado "sin verificar".>
```

## Esqueleto de `TASK.md`

```markdown
# TASK.md — vertical activo

<Resultado observable del vertical, en dos líneas.>

- [ ] F1 — <ítem: una entrega pequeña que funciona entera>
- [ ] F2 — …

## Brechas conocidas
## Ideas — pendientes, sin compromiso
```
