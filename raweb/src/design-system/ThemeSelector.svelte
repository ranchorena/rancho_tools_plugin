<script>
	import { createEventDispatcher } from 'svelte';

	export let id;
	export let value = 'system';

	const dispatch = createEventDispatcher();

	function handleChange(event) {
		dispatch('change', event.currentTarget.value);
	}
</script>

<div class="theme-selector">
	<label for={id}>Tema</label>
	<select class="ds-field" {id} {value} on:change={handleChange}>
		<option value="light">Claro</option>
		<option value="dark">Oscuro</option>
		<option value="system">Sistema</option>
	</select>
</div>

<style>
	.theme-selector {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: var(--ds-text);
		flex-shrink: 0;
	}

	label {
		margin: 0;
	}

	select {
		width: auto;
		margin: 0;
		padding: 0.5rem;
	}
</style>
