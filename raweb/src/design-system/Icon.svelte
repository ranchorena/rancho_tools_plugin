<script>
	export let name;
	export let size = 18;
</script>

<svg
	width={size}
	height={size}
	viewBox="0 0 24 24"
	fill="none"
	stroke="currentColor"
	stroke-width="1.75"
	stroke-linecap="round"
	stroke-linejoin="round"
	aria-hidden="true"
>
	{#if name === 'pin'}
		<path d="M12 21s7-6.1 7-11a7 7 0 1 0-14 0c0 4.9 7 11 7 11z" />
		<circle cx="12" cy="10" r="2.2" />
	{:else if name === 'user'}
		<circle cx="12" cy="8" r="3.2" />
		<path d="M5.5 19.2a6.5 6.5 0 0 1 13 0" />
	{:else if name === 'plus'}
		<path d="M12 5.5v13M5.5 12h13" />
	{:else if name === 'pencil'}
		<path d="M4 20h4L18.5 9.5a2.1 2.1 0 0 0-3-3L5 17v3z" />
		<path d="M13.2 6.8l3 3" />
	{:else if name === 'search'}
		<circle cx="11" cy="11" r="6" />
		<path d="M16 16.5 20 20.5" />
	{:else if name === 'box'}
		<path d="M3.5 8 12 4l8.5 4L12 12 3.5 8z" />
		<path d="M3.5 8v8L12 20l8.5-4V8" />
		<path d="M12 12v8" />
	{:else if name === 'calendar'}
		<rect x="4" y="5.5" width="16" height="14.5" rx="2" />
		<path d="M8 3.8v3.4M16 3.8v3.4M4 9.5h16" />
	{:else if name === 'history'}
		<path d="M4.5 12a7.5 7.5 0 1 0 2.1-5.2" />
		<path d="M4.2 5.2v4.2h4.2" />
		<path d="M12 8.5V12l2.6 1.8" />
	{:else if name === 'layers'}
		<path d="M12 4.5 4 8.5 12 12.5 20 8.5 12 4.5z" />
		<path d="M4 12.5 12 16.5 20 12.5" />
		<path d="M4 16 12 20 20 16" />
	{:else if name === 'close'}
		<path d="M6.5 6.5 17.5 17.5M17.5 6.5 6.5 17.5" />
	{:else if name === 'alert'}
		<path d="M12 4.5 3.8 19h16.4L12 4.5z" />
		<path d="M12 10v4.2" />
		<path d="M12 16.8h.01" />
	{:else if name === 'trash'}
		<path d="M4.5 7h15" />
		<path d="M9 7V5.2h6V7" />
		<path d="M7.2 7l.7 12.2h8.2L16.8 7" />
		<path d="M10 10.5v5.5M14 10.5v5.5" />
	{:else if name === 'lock'}
		<path d="M8 11V8.2a4 4 0 0 1 8 0V11" />
		<rect x="6.2" y="11" width="11.6" height="8.5" rx="1.6" />
	{:else if name === 'logout'}
		<path d="M10 5.5H6.8a1.3 1.3 0 0 0-1.3 1.3v10.4a1.3 1.3 0 0 0 1.3 1.3H10" />
		<path d="M13.2 12H20" />
		<path d="M16.8 8.8 20 12l-3.2 3.2" />
	{/if}
</svg>

<style>
	svg {
		display: block;
		flex-shrink: 0;
	}
</style>
