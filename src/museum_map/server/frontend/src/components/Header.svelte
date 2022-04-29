<script lang="ts">
    import { afterUpdate } from 'svelte';
    import { Link } from 'svelte-navigator';

    import { isBusy } from '../store';

    export let title: string;
    export let nav: {path: string; label: string;}[];

    afterUpdate(() => {
        document.title = title;
    });
</script>

<header class="flex-none shadow-even shadow-black">
    <div class="flex flex-row border-b border-b-neutral-500">
        <h1 class="flex-1 text-lg font-bold px-2 py-1">{title}</h1>
        {#if $isBusy}
            <div class="sr-only" role="alert">Loading data</div>
            <svg viewBox="0 0 38 38" xmlns="http://www.w3.org/2000/svg" stroke="#ffffff" class="flex-none w-8 h-6 pr-2 self-center" aria-hidden="true">
                <g fill="none" fill-rule="evenodd">
                    <g transform="translate(1 1)" stroke-width="3">
                        <path d="M36 18c0-9.94-8.06-18-18-18">
                            <animateTransform attributeName="transform" type="rotate" from="0 18 18" to="360 18 18" dur="1.5s" repeatCount="indefinite"/>
                        </path>
                    </g>
                </g>
            </svg>
        {/if}
    </div>
    <nav>
        <ol class="flex flex-row child-separator">
            <li role="presentation" class="flex-none">
                <Link to="/" class="inline-block px-2 py-1 hover:underline focus:underline">Lobby</Link>
            </li>
            {#each nav as item}
                <li role="presentation" class="flex-none">
                    <Link to={item.path} class="inline-block px-2 py-1 hover:underline focus:underline">{item.label}</Link>
                </li>
            {/each}
        </ol>
    </nav>
</header>
