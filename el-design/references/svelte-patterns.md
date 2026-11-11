# Patrones de Svelte 5 (el código de core-rs)

Fragmentos de `core-rs/web`, recortados y simplificados para mostrar la forma. En otro proyecto existen con otros nombres (por ejemplo `FormDialog` en faztore, `use:enhance` con actions en coedula): usa los helpers que el proyecto ya tiene antes de crear uno.

**Contenido:** 1. Mapa de `src/` · 2. Página y su `load` · 3. Lista parcheada o paginada · 4. Diálogo de formulario · 5. Confirmación · 6. Módulo de API · 7. Lo que hace el cliente · 8. Validación espejo

## 1. Mapa de `src/`

| Ruta | Papel |
| --- | --- |
| `lib/api/contract/` | Generado desde Rust. Nunca se edita |
| `lib/api/client.ts` | El único `fetch`: `ApiFailure`, id por request, 401 → login, errores de carga |
| `lib/api/<recurso>.ts` | Llamadas tipadas de un recurso |
| `lib/api/errors.ts` | `ERROR_TITLES`: el mapa exhaustivo de códigos a frases |
| `lib/forms.svelte.ts` | `FormState`: bloqueo, pointer → campo, aviso del formulario |
| `lib/patched.svelte.ts`, `lib/paged.svelte.ts` | Datos del `load` más los parches locales; listas por cursor |
| `lib/access.ts` | `can(context, permiso)`: sólo lee lo que el servidor dijo |
| `lib/validation.ts` | Respuesta inmediata que refleja los tipos del dominio |
| `lib/format.ts`, `lib/brand.ts`, `lib/toast.ts` | Un dueño de formato, de marca y de avisos |
| `lib/components/` | Composiciones compartidas (`FormDialog`, `ConfirmDialog`, `RowAction`…) |
| `routes/(app)/[tenant=slug]/<área>/` | La página y, a su lado, los diálogos que sólo ella usa |

Un componente que usa una sola página vive junto a ella; sube a `lib/components/` cuando lo usa una segunda.

## 2. Página y su `load`

```ts
// +page.ts
import { loadCtx } from '$lib/api/client';
import { listBranches } from '$lib/api/branches';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => ({
	title: 'Sedes',
	branches: await listBranches(event.params.tenant, { ctx: loadCtx(event) })
});
```

```ts
// [tenant=slug]/+layout.ts — one context call boots the shell.
export const load: LayoutLoad = async (event) => {
	event.depends('app:context');
	return { context: await getContext(event.params.tenant, { ctx: loadCtx(event) }) };
};
```

```svelte
<script lang="ts">
	const { data }: PageProps = $props();

	const branchList = new Patched(() => data.branches);
	const branches = $derived(sorted(branchList.value));

	const context = $derived(data.context);
	const manage = $derived(can(context, 'branches.manage'));
	const multiBranch = $derived(context.modules.includes('multi_branch'));
	const activeCount = $derived(branches.filter((b) => b.is_active).length);
	/** Without Multisede a new (active) branch would be refused: decide it here instead. */
	const canAdd = $derived(manage && (multiBranch || activeCount === 0));

	// Each opening mounts the editor anew; `null` = closed.
	let editing = $state<{ target: BranchView | null; draft: BranchDraft | null } | null>(null);
	let confirming = $state<ConfirmRequest | null>(null);

	async function onSaved(saved: BranchView, created: boolean): Promise<void> {
		branchList.value = created
			? [...branchList.value, saved]
			: branchList.value.map((b) => (b.code === saved.code ? saved : b));
		// The shell's branch list comes from the context.
		await invalidate('app:context');
	}
</script>

{#if manage && !canAdd}
	<Alert color="info" title="¿Abres otro local?">
		Para tener más de una sede activa, tu empresa necesita el módulo Multisede. Lo contrata tu
		proveedor: pídeselo y podrás registrar tus otros locales aquí.
	</Alert>
{/if}

<Table data={branches} rowKey={(branch) => branch.code} hover aria-label="Sedes">
	{#snippet thead()}
		<th>Sede</th>
		<th>Estado</th>
		{#if manage}<th aria-label="Acciones"></th>{/if}
	{/snippet}
	{#snippet row({ row: branch })}
		<td class="lumi-font--medium">{branch.name}</td>
		<td>
			<Chip size="sm" color={branch.is_active ? 'success' : 'warning'}>
				{branch.is_active ? 'Activa' : 'Inactiva'}
			</Chip>
		</td>
		{#if manage}
			<td>
				<RowAction
					icon={PencilIcon}
					label={`Editar la sede ${branch.name}`}
					onclick={() => (editing = { target: branch, draft: null })}
				/>
			</td>
		{/if}
	{/snippet}
</Table>

{#if editing}
	{#key editing}
		<BranchDialog target={editing.target} draft={editing.draft} onsaved={onSaved} onclosed={() => (editing = null)} />
	{/key}
{/if}
{#if confirming}
	<ConfirmDialog request={confirming} onclosed={() => (confirming = null)} />
{/if}
```

Lo que enseña:

- Todo lo que se calcula es `$derived`; sólo es `$state` lo que la persona cambia.
- `canAdd` decide en la pantalla lo que el servidor rechazaría, con hechos del contexto, y el `Alert` explica qué falta y quién lo resuelve.
- El estado se dice con color y texto. La acción de fila tiene nombre accesible.
- Los diálogos se montan a demanda con `{#if}{#key}` y se desmontan en `onclosed`.
- `invalidate('app:context')` sólo porque el shell lista las sedes.

## 3. Lista parcheada o paginada

```ts
/**
 * Server data plus the local patches applied on top of it after mutations
 * (the response of a PUT replaces a row; no refetch).
 */
export class Patched<T> {
	readonly #source: () => T;
	#patch = $state.raw<{ source: T; value: T } | null>(null);

	constructor(source: () => T) {
		this.#source = source;
	}

	get value(): T {
		const source = this.#source();
		const patch = this.#patch;
		return patch && patch.source === source ? patch.value : source;
	}

	set value(value: T) {
		this.#patch = { source: this.#source(), value };
	}
}
```

Un parche pertenece a la instantánea sobre la que se hizo: cuando el `load` de la página vuelve a correr, sus datos frescos lo reemplazan.

`Paged<T>` envuelve una página `{ items, next_cursor }`: `more()` pide la siguiente con el cursor del servidor y descarta la respuesta si la lista cambió mientras tanto; `refresh(fresh)` pone al día las filas en pantalla y antepone las nuevas. El cursor es opaco: no lo interpretes.

## 4. Diálogo de formulario

```svelte
<script lang="ts">
	type Field = 'name' | 'establishmentCode' | 'addressLine' | 'ubigeo';

	const { target, draft = null, slug, onsaved, onclosed }: Props = $props();

	const initial = untrack((): BranchDraft => draft ?? { name: target?.name ?? '' /* … */ });
	let name = $state(initial.name);
	let open = $state(false);
	let fields: HTMLElement | null = $state(null);

	const form = new FormState<Field>({
		pointers: { '/name': 'name', '/establishment_code': 'establishmentCode' }
	});

	function validate() {
		return { name: textError(name, LIMITS.branchName) };
	}

	async function save(): Promise<void> {
		const saved = target
			? await updateBranch(slug, target.code, { name: name.trim() /* … */ })
			: await createBranch(slug, { name: name.trim() /* … */ });
		await onsaved(saved, !target);
		toaster.show({ title: target ? 'Sede actualizada' : 'Sede creada', color: 'success' });
	}

	async function run(): Promise<void> {
		if (await form.run(save, { hold: true, validate, root: fields })) open = false;
	}
</script>

<FormDialog
	bind:open
	title={target ? 'Editar sede' : 'Nueva sede'}
	{form}
	submitLabel={target ? 'Guardar cambios' : 'Crear sede'}
	submitIcon={SaveIcon}
	onsubmit={run}
	{onclosed}
	persistent
	scrollable
>
	<div class="lumi-stack lumi-stack--md" bind:this={fields}>
		<Input
			bind:value={name}
			label="Nombre de la sede"
			name="branch-name"
			icon={StoreIcon}
			placeholder="Por ejemplo: Tienda Centro"
			maxlength={LIMITS.branchName}
			error={form.errors.name}
			oninput={() => form.clear('name')}
			required
		/>
	</div>
</FormDialog>
```

`FormState<F>` es el único estado de formulario:

| Miembro | Para qué |
| --- | --- |
| `busy` | Bloquea el reenvío y los controles |
| `errors` | Un mensaje por campo: de `validate` o del JSON Pointer del servidor |
| `error` | El aviso del formulario, para lo que no tiene campo |
| `code` | El último código, para páginas que ramifican por él |
| `run(action, { validate, hold, root })` | Valida, ejecuta una vez, reparte el fallo y enfoca el primer inválido. `hold` mantiene el bloqueo mientras el diálogo se desvanece |
| `clear(field?)` | Borra el error de un campo al editarlo, o todos |

`FormDialog` monta cerrado, se abre en `onMount` y avisa `onclosed` tras la animación; mientras `form.busy` oculta el cierre e ignora Escape y el fondo; los botones viven en el pie y Enter envía igual. Los valores viven en la página: un error nunca toca el borrador.

## 5. Confirmación

```ts
confirm({
	title: `¿Desactivar la sede «${target.name}»?`,
	message: 'Nadie podrá operar en ella hasta que la reactives.',
	items: names?.length ? names : undefined, // a quién afecta, por su nombre
	detail: 'Estas personas se quedarán sin sede activa: asígnales otra en Equipo.',
	confirmLabel: 'Desactivar sede',
	color: 'danger',
	action: run
});
```

El título pregunta, el mensaje dice la consecuencia, la lista nombra a los afectados y el botón repite el verbo. La acción corre con el diálogo bloqueado, y un fallo se queda dentro con su mensaje.

## 6. Módulo de API

```ts
/** Branches (sedes). */
import { request, tenantPath, type CallOptions } from './client';
import type { BranchView } from './contract/BranchView';
import type { CreateBranch } from './contract/CreateBranch';

/** GET /api/t/{slug}/branches (branches.view). */
export function listBranches(slug: string, options?: CallOptions): Promise<BranchView[]> {
	return request('GET', tenantPath(slug, '/branches'), undefined, options);
}

/** POST /api/t/{slug}/branches → 201 BranchView (branches.manage). */
export function createBranch(slug: string, body: CreateBranch): Promise<BranchView> {
	return request('POST', tenantPath(slug, '/branches'), body);
}
```

Una función por ruta, con su método, su ruta y su permiso en el comentario. Los tipos vienen sólo del contrato generado.

## 7. Lo que hace el cliente (y no se repite en ninguna página)

- JSON del mismo origen con la cookie de sesión y un `X-Request-Id` por llamada.
- Toda falla se vuelve un `ApiFailure` con `status`, `code`, `pointer`, `requestId` y `retryAfter`.
- Desde un `load` (`ctx: loadCtx(event)`): un 401 es un `redirect` al login y cualquier otra falla un `error` de SvelteKit, que pinta el `+error.svelte` más cercano.
- Desde un handler: un 401 `unauthenticated` guarda los borradores abiertos, lleva al login con `next` y aún lanza, para que el caller se detenga.
- Sin respuesta: código `network`. Una respuesta que no es nuestro sobre: `unavailable`.
- Un `internal_error` añade un código corto de soporte tomado del id de la request.
- `next` sólo apunta dentro de la aplicación (`safeNext`).

## 8. Validación espejo

```ts
/**
 * Instant client-side feedback that mirrors `crates/domain/src/identity.rs`.
 * The server stays authoritative: these only spare the user a round trip, and
 * every message is the server's own sentence, so both sources read the same.
 */
import { LIMITS } from '$lib/api/contract/limits';
```

Los límites se generan con el contrato; no escribas un máximo a mano en un componente. Si la regla no está en el dominio, no la inventes en el cliente.
