<script lang="ts">
    import { onMount } from 'svelte';
    import { Link } from 'svelte-navigator';

    import Header from '../components/Header.svelte';
    import Thumnail from '../components/Thumbnail.svelte';
    import { config, fetchItemOfTheDay, itemOfTheDay, fetchRandomItemsSelection, randomItemsSelection, majorCollections, floors, localPreferences } from '../store';

    onMount(() => {
        fetchItemOfTheDay();
        fetchRandomItemsSelection();
    });
</script>

<Header title="Museum Map - Lobby" nav={[]}/>
<article>
    <div class="flex flex-col md:grid md:grid-cols-12 gap-8 p-4">
        {#if $config && $config.attributes.intro && (!$localPreferences.lobby  || !$localPreferences.lobby.hideWelcome)}
            <section class="col-span-12">
                <div class="relative max-w-4xl mx-auto border border-neutral-500 shadow-xl px-2 py-2">
                    <button on:click={() => { localPreferences.setPreference('lobby.hideWelcome', true); }} class="block absolute right-0 top-0 lg:transform lg:translate-x-1/2 lg:-translate-y-1/2 rounded-full shadow-lg text-lg w-8 h-8 bg-neutral-600 border border-neutral-500 z-10 shadow">✖</button>
                    {#each $config.attributes.intro.split('\n\n') as line}
                        <p>{@html line}</p>
                    {/each}
                </div>
            </section>
        {/if}
        {#if $itemOfTheDay}
            <section class="md:col-span-6 lg:col-span-4 flex flex-col">
                <h2 class="flex-none text-xl font-bold mb-4">Item of the Day</h2>
                <div class="flex-1">
                    <Thumnail item={$itemOfTheDay} hoverTitle={false}/>
                </div>
            </section>
        {/if}
        <section class="md:col-span-6 lg:col-span-8 flex flex-col">
            <h2 class="flex-none text-xl font-bold mb-4">Major Collections</h2>
            <div class="flex-1">
                <ul class="grid grid-cols-2 lg:grid-cols-3 gap-4">
                    {#each $majorCollections as collection}
                        <li>
                            <span class="font-bold text-lg">{collection.label}</span>
                            <ul class="flex flex-row flex-wrap gap-2 list-separator">
                                {#each collection.floors as floor}
                                    <li class="flex-none" role="presentation"><Link to={'/floor/' + floor.id} class="hover:underline focus:underline">{floor.attributes.label}</Link></li>
                                {/each}
                            </ul>
                        </li>
                    {/each}
                </ul>
                {#if $floors.length > 0}
                    <div class="mt-16 mb-8 text-center">
                        <Link to={'/floor/' + $floors[0].id} class="inline-block text-xl tracking-widest font-bold bg-blue-800 px-4 py-2 hover:underline focus:underline">Explore the whole collection →</Link>
                    </div>
                {/if}
            </div>
        </section>
        <section class="col-span-12">
            <div class="flex flex-row">
                <h2 class="flex-1 text-xl font-bold mb-4">Selection from our collections</h2>
                <button on:click={() => { fetchRandomItemsSelection(); }} class="flex-none px-2 py-2">
                    <svg viewBox="0 0 24 24" class="w-6 h-6 fill-white">
                        <path d="M2 12C2 16.97 6.03 21 11 21C13.39 21 15.68 20.06 17.4 18.4L15.9 16.9C14.63 18.25 12.86 19 11 19C4.76 19 1.64 11.46 6.05 7.05C10.46 2.64 18 5.77 18 12H15L19 16H19.1L23 12H20C20 7.03 15.97 3 11 3C6.03 3 2 7.03 2 12Z"></path>
                    </svg>
                </button>
            </div>
            <ul class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {#each $randomItemsSelection as item}
                    <li><Thumnail item={item}/></li>
                {/each}
            </ul>
        </section>
    </div>
</article>
