<script lang="ts">
    import { afterUpdate, onDestroy } from 'svelte';
    import { Link, useLocation } from 'svelte-navigator';

    import { isBusy, searchTerm, searchRoom } from '../store';

    export let title: string;
    export let nav: {path: string; label: string;}[];

    const location = useLocation();
    let showNav = false;

    const unsubscribeLocation = location.subscribe((location) => {
        if (location.pathname.startsWith('/room')) {
            const parts = location.pathname.split('/');
            searchRoom.set(parts[2]);
        } else {
            searchRoom.set(null);
        }
    });

    afterUpdate(() => {
        document.title = title;
    });

    onDestroy(unsubscribeLocation);
</script>

<header class="sticky top-0 shadow-even shadow-black z-20 bg-inherit">
    <div class="flex flex-row border-b border-b-neutral-500 items-center">
        <h1 class="flex-1 text-lg font-bold px-2 py-2">{title}</h1>
        {#if $isBusy}
            <div class="sr-only" role="alert">Loading data</div>
            <svg viewBox="0 0 38 38" xmlns="http://www.w3.org/2000/svg" stroke="#ffffff" class="flex-none w-8 h-6 pr-2" aria-hidden="true">
                <g fill="none" fill-rule="evenodd">
                    <g transform="translate(1 1)" stroke-width="3">
                        <path d="M36 18c0-9.94-8.06-18-18-18">
                            <animateTransform attributeName="transform" type="rotate" from="0 18 18" to="360 18 18" dur="1.5s" repeatCount="indefinite"/>
                        </path>
                    </g>
                </g>
            </svg>
        {/if}
        <form class="px-2" on:submit={(ev) => { ev.preventDefault(); }}>
            <input bind:value={$searchTerm} type="search" placeholder="Search the museum..." class="px-2 py-1 border rounded-lg text-black"/>
        </form>
    </div>
    <nav class="flex flex-row items-start" aria-label="Main">
        <ol class="flex-1 flex flex-col md:flex-row md:child-separator">
            <li class="flex-none {!showNav && nav.length > 0 ? 'hidden md:block': ''}">
                <Link to="/" class="inline-block px-2 py-3 hover:underline focus:underline">Lobby</Link>
            </li>
            {#if nav}
                {#each nav as item, idx}
                    <li class="flex-none {!showNav && idx < nav.length - 1 ? 'hidden md:block': ''}">
                        <button on:click={() => { showNav = !showNav; }} class="{ showNav ? 'hidden' : 'block'} flex-none text-left px-2 py-3 md:hidden" aria-label="Toggle the main navigation">{item.label}</button>
                        <Link to={item.path} class="{showNav ? 'inline-block': ' hidden md:inline-block'} px-2 py-3 hover:underline focus:underline">{item.label}</Link>
                    </li>
                {/each}
            {/if}
        </ol>
        <button on:click={() => { showNav = !showNav; }} class="flex-none block px-2 py-2 md:hidden" aria-label="Toggle the main navigation">
            <svg viewBox="0 0 24 24" class="w-8 h-8">
                {#if showNav}
                    <path fill="currentColor" d="M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z" />
                {:else}
                    <path fill="currentColor" d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z" />
                {/if}
            </svg>
        </button>
    </nav>
</header>
