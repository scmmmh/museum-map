<script lang="ts">
    import { useParams, useNavigate } from 'svelte-navigator';
    import { derived } from 'svelte/store';

    import Thumbnail from '../components/Thumbnail.svelte';
    import { cachedItems, cachedRooms, loadItems, loadRooms, config } from '../store';

    const params = useParams();
    const navigate = useNavigate();

    const currentItem = derived([params, cachedItems], ([params, cachedItems]) => {
        if (!cachedItems[params.iid]) {
            loadItems([params.iid]);
        }
        return cachedItems[params.iid];
    }, null);

    const currentRoom = derived(([currentItem, cachedRooms]), ([currentItem, cachedRooms]) => {
        if (currentItem) {
            if (!cachedRooms[(currentItem.relationships.room.data as JsonApiObjectReference).id]) {
                loadRooms([(currentItem.relationships.room.data as JsonApiObjectReference).id]);
            }
            return cachedRooms[(currentItem.relationships.room.data as JsonApiObjectReference).id];
        }
        return null;
    }, null);

    function processParagraph(paragraph: string) {
        return paragraph
            .replace(/<[iI]>/g, '\\begin{em}')
            .replace(/<\/[iI]>/g, '\\end{em}')
            .replace(/<[uU]>/g, '\\begin{em}')
            .replace(/<\/[uU]>/g, '\\end{em}')
            .replace(/<[bB]>/g, '\\begin{strong}')
            .replace(/<\/[bB]>/g, '\\end{strong}')
            .replace(/<\/?[a-zA-Z]+>/g, '')
            .replace(/\\begin\{em\}/g, '<em>')
            .replace(/\\end\{em\}/g, '</em>')
            .replace(/\\begin\{strong\}/g, '<strong>')
            .replace(/\\end\{strong\}/g, '</strong>');
    }

    function processText(text: string) {
        const paras = [] as string[];
        text.split('\n\n').forEach((part1) => {
            part1.split('<br><br>').forEach((part2) => {
                paras.push(processParagraph(part2));
            });
        });
        return paras;
    }

    function formatField(item: string | string[]) {
        if (Array.isArray(item)) {
            return item.join(', ');
        } else {
            return item;
        }
    }
</script>

<section class="absolute left-0 top-0 w-full h-full bg-neutral-800 bg-opacity-80" on:click={() => { navigate('/room/' + $currentRoom.id); }}>
    <div class="absolute left-0 top-0 lg:left-1/2 lg:top-1/2 lg:transform lg:-translate-x-1/2 lg:-translate-y-1/2 w-full lg:w-5/6 h-full lg:h-5/6 flex flex-col lg:flex-row bg-neutral-800 shadow-xl shadow-black overflow-auto lg:overflow-visible" on:click={(ev) => { ev.stopPropagation(); }}>
        {#if $currentItem}
            <button on:click={() => { navigate('/room/' + $currentRoom.id); }} class="block absolute right-0 top-0 lg:transform lg:translate-x-1/2 lg:-translate-y-1/2 rounded-full shadow-lg text-2xl w-10 h-10 bg-neutral-800 z-10">✖</button>
            <div class="flex-none lg:flex-1">
                <Thumbnail item={$currentItem} hideTitle={true} noLink={true} size="large"/>
            </div>
            <div class="flex-none lg:flex-1 flex flex-col overflow-hidden relative">
                <h2 class="flex-none px-6 py-4 bg-blue-900 text-lg font-bold">{$currentItem.attributes.title ? processParagraph($currentItem.attributes.title) : '[Untitled]'}</h2>
                <div class="flex-1 px-6 py-2 overflow-auto">
                    {#each $config.attributes.item.texts as textConfig}
                        {#if $currentItem.attributes[textConfig.name]}
                            {#each processText($currentItem.attributes[textConfig.name]) as para}
                                <p class="mb-2">{@html para}</p>
                            {/each}
                        {/if}
                    {/each}
                    <dl class="flex flex-row flex-wrap items-end gap-y-1">
                        {#each $config.attributes.item.fields as fieldConfig}
                            {#if $currentItem.attributes[fieldConfig.name] && $currentItem.attributes[fieldConfig.name].length}
                                <dt class="flex-none w-1/3 lg:w-1/6 text-sm text-neutral-300 text-right pr-2">{fieldConfig.label}</dt>
                                <dd class="flex-none w-2/3 lg:w-5/6 pl-2">{formatField($currentItem.attributes[fieldConfig.name])}</dd>
                            {/if}
                        {/each}
                    </dl>
                </div>
            </div>
        {/if}
    </div>
</section>
