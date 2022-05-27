<script lang="ts">
    import { Link, useParams } from 'svelte-navigator';
    import { derived, writable } from 'svelte/store';

    import Header from '../components/Header.svelte';
    import Thumnail from '../components/Thumbnail.svelte';
    import { floors, floorTopics, loadRooms, loadItems } from '../store';

    const params = useParams();
    const hoverRoom = writable(null as JsonApiObject | null);
    const samples = writable([] as JsonApiObject[]);

    const currentFloor = derived([params, floors], ([params, floors]) => {
        const floor = floors.filter((floor) => {
            return floor.id === params.id;
        });
        hoverRoom.set(null);
        samples.set([]);
        if (floor.length > 0) {
            return floor[0];
        }
        return null;
    }, null);

    const floorsAndTopics = derived([floors, floorTopics], ([floors, floorTopics]) => {
        return floors.map((floor) => {
            const topicIds = (floor.relationships.topics.data as JsonApiObjectReference[]).map((ref) => { return ref.id });
            return {
                floor: floor,
                topics: floorTopics.filter((floorTopic) => { return topicIds.indexOf(floorTopic.id) >= 0}),
            }
        });
    });

    const rooms = derived(currentFloor, async (currentFloor, set) => {
        if (currentFloor !== null) {
            set(await loadRooms((currentFloor.relationships.rooms.data as JsonApiObjectReference[]).map((ref) => { return ref.id; })));
        }
    }, []);

    function shortenedLabel(label: string) {
        if (label.indexOf('-') >= 0) {
            return label.substring(0, label.indexOf('-')).trim();
        } else {
            return label;
        }
    }

    async function mouseOverRoom(room: JsonApiObject) {
        hoverRoom.set(room);
        samples.set(await loadItems([(room.relationships.sample.data as JsonApiObjectReference).id]));
    }
</script>

{#if $currentFloor}
    <Header title="Museum Map - {$currentFloor.attributes.label}" nav={[{label: $currentFloor.attributes.label, path: '/floor/' + $currentFloor.id}]}/>
    <article class="flex flex-col lg:flex-row px-4 py-2">
        <nav class="flex-none lg:w-1/4 overflow-auto">
            <ol class="flex lg:block flex-row flex-wrap">
                {#each $floorsAndTopics as tuple}
                    <li class="w-1/3 lg:w-full" role="presentation">
                        <Link to="/floor/{tuple.floor.id}" class="block hover-parent">
                            <span class="hover-child-underline text-md {tuple.floor.id === $currentFloor.id ? 'font-bold' : ''}">{tuple.floor.attributes.label}</span>
                            <ul class="hidden lg:flex flex-row flex-wrap list-separator text-sm text-gray-300 gap-x-1 ml-2 mb-2">
                                {#each tuple.topics as topic}
                                    <li>{topic.attributes.label}</li>
                                {/each}
                            </ul>
                        </Link>
                    </li>
                {/each}
            </ol>
        </nav>
        <div class="mt-8 lg:mt-0 lg:hidden px-4 py-1 bg-blue-900 text-lg font-bold text-center mb-4">{$currentFloor.attributes.label}</div>
        <div class="flex-1 lg:flex lg:flex-row lg:justify-center overflow-auto">
            <div class="lg:hidden">
                <ul>
                    {#each $rooms as room}
                        <li>
                            <Link to="/room/{room.id}" class="block py-1">
                                <span>{room.attributes.label}</span>
                            </Link>
                        </li>
                    {/each}
                </ul>
            </div>
            <div class="hidden flex-none lg:flex flex-col justify-between">
                <div class="flex-none"></div>
                <div class="flex-none relative">
                    <img src="/images/map.png" alt=""/>
                    <ul>
                        {#each $rooms as room}
                            <li on:mouseenter={() => { mouseOverRoom(room); }}>
                                <Link to="/room/{room.id}" class="absolute block text-xs bg-white text-black hover:bg-blue-800 hover:text-white focus:bg-blue-800 focus:text-white" style="{room.attributes.position}">
                                    <span class="absolute block left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full text-center">{shortenedLabel(room.attributes.label)}</span>
                                </Link>
                            </li>
                        {/each}
                    </ul>
                </div>
                <div class="flex-none px-4 py-1 bg-blue-900 text-lg font-bold text-center mb-4">{$currentFloor.attributes.label}</div>
            </div>
            <div class="hidden flex-none lg:flex flex-col justify-between w-60 ml-8">
                <div class="flex-none"></div>
                <ul class="flex-none">
                    {#each $samples as sample}
                        <li class="w-60 h-60"><Thumnail item={sample} hideTitle={true}/></li>
                    {/each}
                </ul>
                {#if $hoverRoom}
                    <div class="flex-none px-4 py-1 bg-blue-900 text-lg font-bold text-center mb-4">{$hoverRoom.attributes.label}</div>
                {/if}
            </div>
        </div>
    </article>
{/if}
