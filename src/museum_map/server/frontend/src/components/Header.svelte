<script lang="ts">
    import { afterUpdate } from 'svelte';
    import { Link } from 'svelte-navigator';

    import { isBusy } from '../store';

    export let title: string;
    export let nav: {path: string; label: string;}[];

    let showNav = false;

    afterUpdate(() => {
        document.title = title;
    });
</script>

<header class="sticky top-0 shadow-even shadow-black z-10 bg-inherit">
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
    <nav class="flex flex-row items-start">
        <ol class="flex-1 flex flex-col md:flex-row md:child-separator">
            <li role="presentation" class="flex-none {!showNav ? 'hidden md:block': ''}">
                <Link to="/" class="inline-block px-2 py-1 hover:underline focus:underline">Lobby</Link>
            </li>
            {#each nav as item, idx}
                <li role="presentation" class="flex-none {!showNav && idx < nav.length - 1 ? 'hidden md:block': ''}">
                    <Link to={item.path} class="inline-block px-2 py-1 hover:underline focus:underline">{item.label}</Link>
                </li>
            {/each}
        </ol>
        <button on:click={() => { showNav = !showNav; }} class="flex-none block px-2 py-1 md:hidden">
            <svg viewBox="0 0 24 24" class="w-6 h-6">
                <path fill="currentColor" d="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z" />
            </svg>
        </button>
    </nav>
</header>
