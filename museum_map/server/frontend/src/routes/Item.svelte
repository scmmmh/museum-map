<script lang="ts">
    import { useParams, useNavigate, Link } from 'svelte-navigator';
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

    const prevItemRel = derived([currentItem, currentRoom], ([currentItem, currentRoom]) => {
        if (currentItem && currentRoom) {
            let lastItemRel = null;
            for (const itemRel of (currentRoom.relationships.items.data as JsonApiObjectReference[])) {
                if (itemRel.id === currentItem.id) {
                    break;
                }
                lastItemRel = itemRel;
            }
            if (lastItemRel) {
                return lastItemRel;
            } else {
                return (currentRoom.relationships.items.data as JsonApiObjectReference[])[(currentRoom.relationships.items.data as JsonApiObjectReference[]).length - 1];
            }
        } else {
            return null;
        }
    }, null);

    const nextItemRel = derived([currentItem, currentRoom], ([currentItem, currentRoom]) => {
        if (currentItem && currentRoom) {
            let found = false;
            for (const itemRel of (currentRoom.relationships.items.data as JsonApiObjectReference[])) {
                if (found) {
                    return itemRel;
                }
                if (itemRel.id === currentItem.id) {
                    found = true;
                }
            }
            return (currentRoom.relationships.items.data as JsonApiObjectReference[])[0];
        } else {
            return null;
        }
    }, null);

    let touchStartX = 0;
    let touchStartY = 0;

    function touchStart(ev: TouchEvent) {
        touchStartX = ev.changedTouches[0].clientX;
        touchStartY = ev.changedTouches[0].clientY;
    }

    function touchEnd(ev: TouchEvent) {
        const touchEndX = ev.changedTouches[0].clientX;
        const touchEndY = ev.changedTouches[0].clientY;
        if (Math.abs(touchEndY - touchStartY) < 100) {
            if (touchEndX - touchStartX < 50 && $nextItemRel) {
                navigate('/room/' + $currentRoom.id + '/' + $nextItemRel.id);
            } else if (touchEndX - touchStartX > 50 && $prevItemRel) {
                navigate('/room/' + $currentRoom.id + '/' + $prevItemRel.id);
            }
        }
    }

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

<section on:touchstart={touchStart} on:touchend={touchEnd} class="fixed left-0 top-0 w-screen h-screen bg-neutral-800 bg-opacity-80 z-20" on:click={() => { navigate('/room/' + $currentRoom.id); }}>
    <div class="absolute left-0 top-0 lg:left-1/2 lg:top-1/2 lg:transform lg:-translate-x-1/2 lg:-translate-y-1/2 w-full lg:w-5/6 xl:w-4/6 h-full lg:max-h-5/6 xl:max-h-4/6 flex flex-col bg-neutral-800 shadow-xl shadow-black overflow-auto lg:overflow-visible" on:click={(ev) => { ev.stopPropagation(); }}>
        {#if $currentItem}
            <button on:click={() => { navigate('/room/' + $currentRoom.id); }} class="block absolute right-0 top-0 lg:transform lg:translate-x-1/2 lg:-translate-y-1/2 rounded-full shadow-lg text-2xl w-10 h-10 bg-neutral-800 z-10">✖</button>
            <div class="flex flex-row items-center flex-none bg-blue-900">
                <h2 class="flex-1 px-4 py-2 text-lg font-bold">{$currentItem.attributes.title ? processParagraph($currentItem.attributes.title) : '[Untitled]'}</h2>
                <a href="https://twitter.com/intent/tweet?url={encodeURIComponent(window.location.href)}&text={$currentItem.attributes.title}&via=Hallicek" target="_blank" rel="noopener" class="flex-none">
                    <svg viewBox="0 0 24 24" class="text-white w-8 h-8">
                        <path fill="currentColor" d="M22.46,6C21.69,6.35 20.86,6.58 20,6.69C20.88,6.16 21.56,5.32 21.88,4.31C21.05,4.81 20.13,5.16 19.16,5.36C18.37,4.5 17.26,4 16,4C13.65,4 11.73,5.92 11.73,8.29C11.73,8.63 11.77,8.96 11.84,9.27C8.28,9.09 5.11,7.38 3,4.79C2.63,5.42 2.42,6.16 2.42,6.94C2.42,8.43 3.17,9.75 4.33,10.5C3.62,10.5 2.96,10.3 2.38,10C2.38,10 2.38,10 2.38,10.03C2.38,12.11 3.86,13.85 5.82,14.24C5.46,14.34 5.08,14.39 4.69,14.39C4.42,14.39 4.15,14.36 3.89,14.31C4.43,16 6,17.26 7.89,17.29C6.43,18.45 4.58,19.13 2.56,19.13C2.22,19.13 1.88,19.11 1.54,19.07C3.44,20.29 5.7,21 8.12,21C16,21 20.33,14.46 20.33,8.79C20.33,8.6 20.33,8.42 20.32,8.23C21.16,7.63 21.88,6.87 22.46,6Z" />
                    </svg>
                </a>
                <div role="presentation" class="w-10"></div>
            </div>
            <div class="flex-none lg:flex-1 lg:flex lg:flex-row lg:overflow-hidden">
                <div class="hidden lg:flex flex-none flex-col justify-center px-4">
                    {#if $prevItemRel}
                        <Link to="/room/{$currentRoom.id}/{$prevItemRel.id}" class="block text-xl bg-neutral-600 px-2 py-1 rounded-lg">&laquo;</Link>
                    {/if}
                </div>
                <div class="p-4 lg:flex-1 lg:h-full lg:self-start lg:overflow-hidden">
                    <Thumbnail item={$currentItem} noLink={true} noTitle={true} size="large"/>
                </div>
                <div class="m-4 lg:flex-1 lg:overflow-auto">
                    {#each $config.attributes.item.texts as textConfig}
                        {#if $currentItem.attributes[textConfig.name]}
                            {#each processText($currentItem.attributes[textConfig.name]) as para}
                                <p class="mb-2">{@html para}</p>
                            {/each}
                        {/if}
                    {/each}
                    <table class="mt-8">
                        {#each $config.attributes.item.fields as fieldConfig}
                            {#if $currentItem.attributes[fieldConfig.name] && $currentItem.attributes[fieldConfig.name].length}
                                <tr>
                                    <th scope="row" class="font-normal text-sm text-neutral-300 text-right pr-2 align-bottom">{fieldConfig.label}</th>
                                    <td>{formatField($currentItem.attributes[fieldConfig.name])}</td>
                                </tr>
                            {/if}
                        {/each}
                    </table>
                </div>
                <div class="hidden lg:flex flex-none flex-col justify-center px-4">
                    <Link to="/room/{$currentRoom.id}/{$nextItemRel.id}" class="block text-xl bg-neutral-600 px-2 py-1 rounded-lg">&raquo;</Link>
                </div>
            </div>
        {:else}
            <p class="self-center text-center w-full">Loading...</p>
        {/if}
    </div>
</section>