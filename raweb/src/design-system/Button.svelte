<script>
	export let variant = 'primary';
	export let type = 'button';
	export let disabled = false;

	let className = '';
	export { className as class };
</script>

<button
	{...$$restProps}
	{type}
	{disabled}
	class={`ds-button ds-button--${variant}${className ? ` ${className}` : ''}`}
	on:click
	on:keydown
	on:focus
>
	<slot />
</button>
