<script lang="ts">
    import { afterUpdate, onDestroy, onMount, tick } from 'svelte';
    import { Link, useLocation, useNavigate } from 'svelte-navigator';

    import { isBusy, searchTerm, searchRoom, floors } from '../store';

    export let title: string;
    export let nav: {path: string; label: string;}[];

    const location = useLocation();
    const navigate = useNavigate();
    let showNav = false;
    let searchElement : HTMLElement | null = null;

    const unsubscribeLocation = location.subscribe((location) => {
        if (location.pathname.startsWith('/room')) {
            const parts = location.pathname.split('/');
            searchRoom.set(parts[2]);
        } else {
            searchRoom.set(null);
        }
    });

    const unsubscribeSearchTerm = searchTerm.subscribe((searchTerm) => {
        if (searchTerm !== '' && $location.pathname === '/' && $floors.length > 0) {
            navigate('/floor/' + $floors[0].id + '?search');
        }
    });

    onMount(() => {
        if ($location.search === '?search') {
            navigate($location.pathname);
            tick().then(() => {
                tick().then(() => {
                    if (searchElement) {
                        searchElement.focus();
                    }
                });
            });
        }
    });

    afterUpdate(() => {
        document.title = title;
    });

    onDestroy(() => {
        unsubscribeLocation();
        unsubscribeSearchTerm();
    });
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
        <form class="px-2 relative" on:submit={(ev) => { ev.preventDefault(); }}>
            <input bind:this={searchElement} bind:value={$searchTerm} type="search" placeholder="Search the museum..." class="px-2 py-1 border rounded-lg text-black"/>
            <button on:click={() => { searchTerm.set(''); }} type="button" class="block absolute right-[0.5rem] top-1/2 transform -translate-y-1/2 text-black" aria-label={$searchTerm.trim() === '' ? 'Search the museum': 'Clear your search'}>
                <svg viewBox="0 0 24 24" class="w-8 h-8" aria-hidden="true">
                    {#if $searchTerm.trim() === ''}
                        <path fill="currentColor" d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z" />
                    {:else}
                        <path fill="currentColor" d="M20 6.91L17.09 4L12 9.09L6.91 4L4 6.91L9.09 12L4 17.09L6.91 20L12 14.91L17.09 20L20 17.09L14.91 12L20 6.91Z" />
                    {/if}
                </svg>
            </button>
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
            <svg viewBox="0 0 24 24" class="w-8 h-8" aria-hidden="true">
                {#if showNav}
                    <path fill="currentColor" d="M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z" />
                {:else}
                    <path fill="currentColor" d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z" />
                {/if}
            </svg>
        </button>
    </nav>
</header>
