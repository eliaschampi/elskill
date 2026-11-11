# Lumi para productos

Qué usar y cómo componerlo. La verdad está en el paquete instalado; esto es el mapa para llegar rápido.

**Contenido:** 1. Dónde leer · 2. Montaje · 3. Tema · 4. Estructura · 5. Componente · 6. Clases de composición · 7. Tokens para CSS propio · 8. Escalas · 9. Comportamientos que suelen fallar · 10. Patrones CSS

## 1. Dónde leer

| Necesitas… | Lee |
| --- | --- |
| Saber si algo es público | `node_modules/@lumi-ui/svelte/dist/index.d.ts` |
| Las props de un componente | `dist/components/<Nombre>/types.d.ts`, y su `.svelte` para snippets y callbacks |
| Un token | `dist/styles/tokens.base.css` |
| Una clase de composición | `dist/styles/core.css` (`layout.css`, `utilities.css`) y `patterns.css` |
| Recetas completas | `docs/CONSUMER_REFERENCE.md` del repositorio `lumi-ui`, si está en la máquina |

Algunos snippets y callbacks son locales al `.svelte` y no aparecen en `types.d.ts`: cuando importen, abre el componente.

## 2. Montaje

```svelte
<!-- src/routes/+layout.svelte -->
<script module lang="ts">
	import { lumiEs, setLumiLocale, type LumiLocaleOptions } from '@lumi-ui/svelte';

	// Module scope: Lumi caches merged copy per messages object.
	const LUMI_LOCALE: LumiLocaleOptions = {
		locale: 'es-PE',
		currency: 'PEN',
		timeZone: 'America/Lima',
		messages: lumiEs
	};
</script>

<script lang="ts">
	// Tokens and core everywhere; each area's layout adds the patterns it uses.
	import '@lumi-ui/svelte/styles/tokens.base.css';
	import '@lumi-ui/svelte/styles/core.css';
	import '../lumi-theme.css';
	import '../app.css';
	import { Toaster } from '@lumi-ui/svelte';
	import { toaster } from '$lib/toast';

	const { children } = $props();
	setLumiLocale(LUMI_LOCALE);
</script>

{@render children()}
<Toaster {toaster} />
```

- Los estilos se importan una vez, en la raíz. Una página pública ligera puede cargar sólo `tokens.base.css` y `base.css`.
- El copy integrado está en inglés hasta que corre `setLumiLocale`; una prop explícita (`placeholder`, `closeLabel`…) siempre gana.
- Un `createToaster()` por aplicación y un solo `<Toaster>`; `toaster.show({ title, color })` se llama desde los handlers.

## 3. Tema

```css
/* src/lumi-theme.css — Product theme: Lumi seeds only. */
:root {
	--lumi-brand-primary: oklch(0.52 0.18 257);
	--lumi-brand-secondary: oklch(0.56 0.15 40);
}
```

Lumi deriva de las semillas las superficies, los bordes, los rellenos y el modo oscuro. No reasignes tokens derivados `--lumi-color-*` ni redefinas success, warning, danger o info como marca. Claro, oscuro o sistema es un controlador aparte (`@lumi-ui/svelte/color-scheme`): un script previo al pintado y una instancia por aplicación.

Cada rol expone la misma familia: `--lumi-color-{rol}` (borde, foco, ícono), `-solid` (superficie con presencia), `-foreground` (contenido sobre el sólido) y `-bg` (superficie suave). Una superficie rellena usa `solid` con `foreground`.

## 4. Estructura

| Necesitas… | Empieza con |
| --- | --- |
| Shell con navegación | `.lumi-dashboard-layout` + `Sidebar` + `Navbar` |
| Ritmo de una página | `.lumi-stack` + `PageHeader` + `Card` o `DashboardSection` |
| Filtros junto a resultados | `.lumi-layout--two-columns` + `PageSidebar` |
| Tarjetas fluidas | `.lumi-grid .lumi-grid--responsive` |
| Grilla de tarjetas de tablero | `.lumi-grid .lumi-grid--cards` |
| Columnas fijas en escritorio | `.lumi-grid` + `--columns-2-lg` … `--columns-4-lg` |
| Tarea enfocada o acceso | `.lumi-centered-layout` + `.lumi-centered-card` |
| Contenido acotado | `.lumi-container` + un modificador de tamaño |

`.lumi-grid` va siempre: un modificador solo no pone `display: grid`. No anides shells ni dupliques el drawer de `PageSidebar`. El disparador móvil de `PageSidebar` va dentro de `.lumi-page-sidebar__header-actions`.

## 5. Componente

| Necesitas… | Elige |
| --- | --- |
| Texto, número o varias líneas | `Input`, `NumberInput`, `Textarea` |
| Una opción exclusiva y visible | `SegmentedControl`; `Radio` si cada una lleva etiqueta y descripción |
| Varios interruptores o filtros independientes | `ToggleGroup`; uno solo, `Button pressed` |
| Elección larga o con poco espacio | `Select`; con búsqueda en el servidor, `RemoteSelect` |
| Un booleano que se envía o un ajuste inmediato | `Checkbox` o `Switch` |
| Aviso que persiste o que pasa | `Alert` o `Toaster` |
| Navegar o actuar | `Button href` o `Button onclick` |
| Superficie genérica o sección titulada | `Card` o `DashboardSection` |
| Registros con columnas o filas cortas | `Table`, o `List` con `ListItem`; filas de persona, `UserInfo` |
| Paginar | `Pagination` (`href` para enlaces rastreables) |
| Overlay anclado, de puntero, interruptivo o explicativo | `Dropdown`, `Context`, `Dialog`, `Tooltip` |
| Sin datos, fallo o espera | `EmptyState`, `ErrorState`, `Skeleton` o `Loading` |
| Un dato con su etiqueta | `InfoItem` |

## 6. Clases de composición

| Para… | Clases |
| --- | --- |
| Ritmo vertical | `.lumi-stack` + `.lumi-stack--{2xs,xs,sm,md,lg,xl}` |
| Fila flexible | `.lumi-flex` + `--{column,mobile-column,wrap,nowrap,center,between}`, `.lumi-flex--gap-{2xs,xs,sm,md,lg,xl}` |
| Alinear | `.lumi-align-items--{start,center,end,stretch}`, `.lumi-justify--{start,center,between,end}` |
| Grilla | `.lumi-grid` + `--{responsive,cards,identity-split,columns-1…4,columns-2-lg…4-lg}`, `.lumi-grid--gap-{sm,md,lg,xl}`, `.lumi-grid-item--span-all` |
| Espacio | `.lumi-padding--{none,2xs,xs,sm,md,lg,xl}`, `.lumi-margin--none`, `.lumi-margin-{top,bottom}--{2xs,xs,sm,md,lg}` |
| Texto | `.lumi-text--{xs,sm,lg,xl,2xl,4xl}`, `.lumi-text--{muted,primary,success,warning,danger,info}`, `.lumi-font--{medium,semibold,bold}` |
| Texto largo | `.lumi-text-ellipsis`, `.lumi-text-break`, `.lumi-text-clamp--{2,3}` |
| Sólo para lectores de pantalla | `.lumi-sr-only` |
| Tamaño | `.lumi-width--full`, `.lumi-min-width--0`, `.lumi-max-w--{sm,lg,4xl,prose,full}` |

Cortes responsivos: en 64rem o menos el shell pasa a navbar y contenido y las dos columnas colapsan; en 48rem o menos las grillas van a una columna; en 30rem o menos todo se apila.

Compón con estas clases antes de escribir CSS. No copies sus declaraciones a tu CSS ni apuntes a selectores internos de un componente.

## 7. Tokens para CSS propio

```css
.account-summary {
	display: grid;
	gap: var(--lumi-space-md); /* 2xs … 6xl */
	padding: var(--lumi-space-sm) var(--lumi-space-md);
	border: var(--lumi-border-width-thin) solid var(--lumi-color-border);
	border-radius: var(--lumi-radius-panel);
	background: var(--lumi-color-surface-raised);
	box-shadow: var(--lumi-shadow-md);
	color: var(--lumi-color-text); /* -text-muted, -text-light */
	transition: var(--lumi-transition-control);
}

.account-summary a:focus-visible {
	outline: var(--lumi-focus-outline);
	outline-offset: var(--lumi-focus-outline-offset);
}
```

- Radio por rol: `--lumi-radius-control`, `--lumi-radius-panel`, `--lumi-surface-radius`, `--lumi-radius-full`.
- Altura de control: `--lumi-control-height-{xs…xl}`.
- Movimiento: `--lumi-duration-fast` … `--lumi-duration-slower`, `--lumi-easing-default`; prefiere las recetas `--lumi-transition-control` y `--lumi-transition-interactive`.
- Capas: `--lumi-z-*`.
- Un número suelto sólo como tamaño de pista de una grilla en `rem`, o dentro de un `calc()` de tokens.

## 8. Escalas

- **Color:** `primary`, `secondary`, `success`, `warning`, `danger`, `info`.
- **Variante de `Button`:** `filled`, `border`, `flat`, `ghost`, `gradient`. La acción principal es `filled`; cancelar es `border`.
- **Tamaño:** depende del componente (`Input` de `xs` a `xl`; `Button` de `sm` a `xl`; `Chip` `sm`). Compruébalo en su `types.d.ts`.

## 9. Comportamientos que suelen fallar

- Lumi anima un cambio de `open`: un `Dialog` que monta ya abierto no anima. Monta cerrado y ábrelo.
- Un `Card` clicable se renderiza como botón: no anides controles interactivos dentro.
- `ListItem` con `href` u `onclick` usa un área estirada; las acciones de `trailing` siguen siendo hermanos reales.
- `Table` necesita `rowKey` si los registros no tienen `id` ni `key` estables.
- Un nombre de ícono como texto no pinta nada hasta registrarlo: pasa el componente.
- Un control de sólo ícono necesita nombre accesible; un ícono decorativo anidado, no.
- `Dropdown` y `Context` son menús, no popovers genéricos: conserva sus roles.
- Los overlays van en portal: no los metas dentro de un padre que recorta.
- `MessageList` necesita una altura.

## 10. Patrones CSS

`@lumi-ui/svelte/styles/patterns.css` es opcional y trae composiciones neutrales: resumen de filtros (`.lumi-filter-summary`), barras de sección (`.lumi-section-toolbar`, `.lumi-inline-filters`), listas de métricas (`.lumi-metric-rank-list`), filas de ítems (`.lumi-item-row`, `.lumi-item-list`), totales (`.lumi-total-box`), celdas de persona (`.lumi-person-cell`). Impórtalo en el layout del área que lo usa, aplica sus hijos BEM documentados y no inventes modificadores.
