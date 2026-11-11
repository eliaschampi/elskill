---
name: el-design
description: Diseño e implementación de interfaces al estilo de Elias con Svelte 5 y Lumi UI. Úsala siempre que se cree, cambie o revise una pantalla, página, formulario, diálogo, tabla, componente, estilo, CSS, tema, texto de interfaz o flujo de usuario, y al evaluar UX, accesibilidad o peso del frontend. Define la anatomía de página, los estados obligatorios, el ciclo de vida de diálogos y formularios, el uso de tokens Lumi sin colores sueltos, el copy en español y los presupuestos de peso.
---

# EL · Diseño

Interfaces tranquilas, densas y rápidas: Lumi pone el lenguaje visual, el servidor pone las reglas y la pantalla sólo compone. Aplica primero `el-architecture` (dueños, protocolo, cuándo detenerse).

## Núcleo

1. **Manda el proyecto.** Su `AGENTS.md` y su `docs/SPEC.md` ganan a esta skill, y esta skill gana a tus costumbres. Si chocan, obedece al proyecto y dilo.
2. **Prioridad, no invertir:** corrección → legibilidad → consistencia con el repositorio → rendimiento → simplicidad.
3. **Un dueño por regla.** Cada regla, dato y decisión vive en un solo lugar; lo demás lo consulta o lo deriva.
4. **Que lo compruebe la máquina.** Un tipo, un constraint, un lint o un tipo generado valen más que una convención que dependa de la revisión.
5. **No adivines.** Lee el código, sus tests y el fuente de la dependencia antes de usarlos. Ante dinero, identidad, permisos o migraciones, detente y pregunta.
6. **Nada especulativo.** Ni capas, ni opciones, ni rutas, tablas o permisos "para después".
7. Identificadores en inglés; documentos, copy y mensajes al usuario en español; los comentarios siguen el idioma del archivo vecino.

## 0. Antes de escribir

- **¿Producto o librería?** Esta skill cubre los productos que consumen Lumi. Dentro del repositorio `lumi-ui` mandan su `AGENTS.md` y su `docs/AGENT_GUIDE.md`: componentes neutrales al dominio, imports relativos y peso medido en cada cambio.
- **Lee las props reales** antes de usar un componente: `node_modules/@lumi-ui/svelte/dist/components/<Nombre>/types.d.ts` y su `.svelte`. No adivines props ni snippets: manda la versión instalada.
- **Copia la forma de la pantalla vecina** más parecida antes de inventar una.

| Para… | Lee |
| --- | --- |
| Elegir componente, estructura, clase o token | `references/lumi.md` |
| Escribir una página, un diálogo, un formulario o una llamada a la API | `references/svelte-patterns.md` |

## 1. Leyes

- **D1. Svelte 5 runes y TypeScript estricto.** `$state`, `$derived`, `$props`, `$effect`, `$bindable`, snippets. Nunca `export let`, `$:`, `createEventDispatcher` ni `writable()` para estado local. Lo calculable es `$derived`; `$effect` queda para sincronizar con algo externo, y limpia lo que abre.
- **D2. Sólo Lumi.** Componentes de `@lumi-ui/svelte` (o del reexport del proyecto), tokens `var(--lumi-…)` y clases `lumi-*`. Nada de Tailwind, Bootstrap ni otro kit; nada de hex, `rgb()`, espaciados sueltos ni `style="…"`.
- **D3. No toques a Lumi por dentro.** No apuntes a selectores internos de un componente ni reasignes tokens derivados `--lumi-color-*`. El tema del producto son sólo semillas (`--lumi-brand-primary`, `--lumi-brand-secondary`, en OKLCH) en un archivo. Si Lumi no tiene el contrato público que necesitas, detente y pregunta: o es composición del producto con tokens, o es un cambio en Lumi que sirve a todos sus productos. Nunca un parche a sus internos.
- **D4. Color con significado.** Sólo los roles `primary`, `secondary`, `success`, `warning`, `danger` e `info`. Un estado se comunica con color **y** con ícono o texto.
- **D5. Íconos Lucide, uno por import** (`@lucide/svelte/icons/map-pin`), pasados como componente.
- **D6. La pantalla no decide reglas.** Muestra los datos y las capacidades `can_*` que calcula el servidor. La validación del cliente sólo adelanta la respuesta, con los mismos límites y las mismas frases del servidor; decide el servidor.
- **D7. Un dueño de cada cosa:** tipos sólo del contrato generado · un cliente HTTP · un toaster · una fuente de navegación · un `can()` · la marca en `brand.ts` · fechas y dinero en un módulo de formato (`es-PE`, `PEN`, `America/Lima`).
- **D8. Nada vacío para el futuro:** ni pestañas, ni rutas, ni botones sin función.

## 2. Diseña antes de componer

- **D9. Empieza por la persona y su acción.** Quién usa la pantalla, en qué equipo (un cajero en un celular barato con red lenta; un contador con veinte pestañas) y cuál es su acción principal. Una acción principal por vista, en el `PageHeader`, con verbo y objeto.
- **D10. Todos los estados existen antes de entregar:** cargando · vacío, con la siguiente acción si tiene permiso · error · sin permiso (lo que no puede hacer no se muestra) · ocupado, sin doble envío · éxito, con aviso y fila al día · sin conexión.
- **D11. Prevén en vez de fallar.** Si el servidor rechazaría la acción, decídelo en la pantalla con hechos que el servidor ya entregó, y explica qué falta y quién lo resuelve: un control deshabilitado con su nota vale más que un error al guardar.
- **D12. Lo destructivo se confirma** nombrando la consecuencia (qué se pierde y a quién afecta), con color `danger` y un verbo en el botón. El rojo solo no confirma nada.
- **D13. Densidad con calma.** Es un sistema de trabajo: mucha información legible, poca decoración. El inicio es una vista operativa rápida; los gráficos y reportes pesados viven en su módulo.

## 3. Anatomía de página

```svelte
<div class="lumi-stack lumi-stack--lg">
	<PageHeader title="Sedes" subtitle={`${plural(activeCount, 'sede activa', 'sedes activas')}.`} icon={MapPinIcon}>
		{#snippet actions()}
			{#if canAdd}
				<Button variant="filled" icon={PlusIcon} onclick={() => (editing = { target: null })}>Nueva sede</Button>
			{/if}
		{/snippet}
	</PageHeader>

	{#if branches.length === 0}
		<Card spaced>
			<EmptyState icon={MapPinIcon} title="Sin sedes" description="Registra tu primera sede." />
		</Card>
	{:else}
		<Card spaced>
			<Table data={branches} rowKey={(branch) => branch.code} hover aria-label="Sedes">…</Table>
		</Card>
	{/if}
</div>
```

- **D14.** Página estándar: `lumi-stack` → `PageHeader` (título, subtítulo con el dato vivo, acción con permiso) → avisos que persisten → `Card` con `Table` o `EmptyState`.
- **D15. Una lista que puede crecer es una `Table`,** con búsqueda y "Ver más" por cursor. Las tarjetas son para tableros ralos o para un bloque de identidad.
- **D16.** Cada fila tiene `rowKey` estable, su estado en un `Chip` y sus acciones al final con nombre accesible ("Editar la sede Centro").
- **D17.** Crear, editar y confirmar van en un `Dialog`. Una página completa sólo para formularios grandes.
- **D18.** Elige la estructura con la tabla de `references/lumi.md` antes de escribir CSS: shell, página, filtros con resultados, grilla, tarea centrada.

## 4. Formularios y diálogos

- **D19. Un solo ciclo de vida.** Lumi anima un cambio de `open`, nunca un diálogo que monta abierto. El diálogo a demanda lo monta la página con `{#if x}{#key x}…{/key}{/if}`; él se abre solo y pide desmontarse en `onclosed`, tras la animación. Cada apertura estrena borrador: no hay reset imperativo.
- **D20. Bloqueado mientras guarda,** y mientras se desvanece tras el éxito: sin botón de cerrar, sin Escape, sin toque en el fondo. Toda salida (cerrar, Escape, fondo, Cancelar, el gesto atrás del teléfono) pasa por una misma guarda.
- **D21. Un estado de formulario.** Una bandera `busy` impide reenviar; los errores del servidor llegan a su campo por el JSON Pointer; lo demás va a un aviso del formulario. Los valores viven en la página: un error nunca toca el borrador.
- **D22.** El error de un campo se borra al editarlo. Al fallar, el foco va al primer campo inválido. Enter envía.
- **D23. Tras guardar:** parchea la lista con la respuesta del servidor, sin volver a pedirla; invalida sólo si cambió lo que muestra el shell; un toast breve confirma.
- **D24. Idempotencia desde el cliente.** La `request_key` nace con el borrador y se reutiliza en cada reintento.
- **D25.** Un borrador largo sobrevive a que venza la sesión.
- **D26.** `Checkbox` para un booleano que se envía y `Switch` para un ajuste inmediato; `Alert` para lo que persiste y toast para lo que pasa.

## 5. Datos en el cliente

D23 y D27 a D29 describen la SPA con API de core-rs. En un monolito con actions o Inertia (faztore, coedula, aeduca) el equivalente ya existe (`use:enhance`, `fail`, `invalidate` con la clave de `depends`): usa el del proyecto, no importes el de core-rs.

- **D27.** El layout carga el contexto una vez (`depends('app:context')`) y navegar no lo repite. Cada página carga lo suyo en su `load`; un componente no hace `fetch` de datos de página.
- **D28.** Un módulo de API por recurso, sobre el único cliente. Cada función nombra su ruta y su permiso.
- **D29.** Un 401 `unauthenticated` lleva al login con `next`; un error con `pointer` va a su campo; el resto, al aviso. El mapa de códigos de error es exhaustivo: un código nuevo rompe el build hasta tener su frase.
- **D30.** Panel y POS son SPA (`adapter-static`, `ssr = false`). Una superficie pública con SEO usa SSR, enlaces reales (`Button href`) y los estilos mínimos de Lumi.

## 6. Lenguaje visual

- **D31. Calma.** Si quitas una línea más de decoración y la pantalla sigue completa, estás más cerca. Sin degradados llamativos, sin bordes de colores, sin rebotes.
- **D32. Escalera de superficies:** hundido → superficie → tarjeta → elevado → flotante. Los campos son hundidos, el contenido va en tarjetas y lo flotante (diálogos, menús) es vidrio. Un rol, una receta.
- **D33. Geometría sólo con tokens:** espacio `--lumi-space-*`, radio por rol, sombra `--lumi-shadow-*`, movimiento `--lumi-duration-*` y `--lumi-transition-*`. El movimiento es sutil y respeta `prefers-reduced-motion`.
- **D34. Antes de añadir algo visual:** ¿sirve un token o una clase que ya existe? ¿crea una segunda manera de hacer lo mismo? ¿el valor por defecto es el más callado? ¿quitaste algo al añadir?
- **D35.** Buen minimalismo: menos props, menos ramas, tamaños compartidos. Mal minimalismo: quitar accesibilidad, contraste o estados vacíos.

## 7. CSS propio

Sólo cuando ninguna clase `lumi-*` compone lo que necesitas.

- **D36.** Va en el CSS de la aplicación, con tokens, nombres BEM (`document-line__amount`, `document-line--head`) y `:where()` para no ganar especificidad.
- **D37.** Propiedades lógicas (`inset-block-start`, `padding-inline`), móvil primero y cortes en `rem` alineados con los de Lumi (30, 48 y 64).
- **D38.** Un overlay va en portal; nunca dentro de un padre con `overflow: hidden`.

## 8. Accesibilidad

- **D39.** Elementos semánticos y controles reales: navegar es `href`, actuar es `onclick`.
- **D40.** Todo control de sólo ícono tiene nombre accesible y toda tabla su `aria-label`. Una etiqueta existe aunque no se vea (`lumi-sr-only`).
- **D41.** Teclado completo y foco visible con los tokens de foco. Escape cierra, salvo en un diálogo persistente. Al abrir, el foco va al primer campo sólo con puntero fino, para no levantar el teclado del celular.
- **D42.** Una tarjeta clicable no contiene controles; un menú conserva sus roles de menú.

## 9. Copy

- **D43.** Español claro, de tú, sin jerga ni códigos técnicos. Botones con verbo y objeto ("Crear sede", "Guardar cambios"); confirmaciones como pregunta ("¿Desactivar la sede «Centro»?").
- **D44.** Un error dice qué pasó y qué hacer, y nunca culpa a la persona. Un fallo inesperado ofrece un código corto para soporte.
- **D45.** El texto de ayuda explica la consecuencia, no el campo ("No se puede cambiar después").
- **D46.** Plurales, fechas y dinero salen de un helper y de `Intl`; el nombre del producto, de `brand.ts`.

## 10. Peso

- **D47.** El peso es un presupuesto escrito y medido en un celular barato con red lenta (en core-rs, menos de 150 KB de JavaScript gzip al inicio).
- **D48.** Las dependencias de runtime son Lumi y Lucide. Cualquier otra es una decisión de arquitectura: detente y pregunta.
- **D49.** Pocos chunks cacheables; los datos de referencia pesados se cargan sólo donde se usan; cada superficie importa sólo los estilos de Lumi que usa.

## 11. Cierre

Corre los checks del proyecto (en core-rs, `pnpm --dir web run check` y `pnpm --dir web run build`: svelte-check, oxlint y Prettier sin warnings). Abre el navegador sólo para resolver una duda visual o de integración concreta; reutiliza un servidor que ya corra y apaga el que inicies. Antes de entregar, repasa:

- [ ] Sólo componentes, clases y tokens de Lumi; ningún color, espaciado ni `style` suelto.
- [ ] Ninguna regla reimplementada: la pantalla usa `can_*` y los datos del servidor.
- [ ] Están los estados: cargando, vacío con su acción, error, ocupado, éxito.
- [ ] Los diálogos siguen el ciclo de vida único y se bloquean al guardar.
- [ ] Los errores con `pointer` aparecen en su campo y el foco va al primero.
- [ ] Guardar parchea la lista; no la vuelve a pedir.
- [ ] Todo control de ícono tiene nombre accesible y todo funciona con teclado.
- [ ] Copy en español, con verbos; la marca viene de `brand.ts`.
- [ ] Ninguna dependencia nueva; ningún import que traiga un paquete entero.
- [ ] Se ve bien en el ancho de un celular (unos 360 px), en claro y en oscuro.

## Referencias

- `references/lumi.md` — qué componente, qué estructura, qué clase y qué token usar; tema y comportamientos que suelen fallar.
- `references/svelte-patterns.md` — el código de core-rs: página con su `load`, diálogo de formulario, estado de formulario, lista parcheada o paginada y módulo de API.
