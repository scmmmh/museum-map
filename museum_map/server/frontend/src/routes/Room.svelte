<script lang="ts">
    import { Route, useParams } from 'svelte-navigator';
    import { derived } from 'svelte/store';

    import Header from '../components/Header.svelte';
    import Footer from '../components/Footer.svelte'
    import Thumnail from '../components/Thumbnail.svelte';
    import Item from './Item.svelte';
    import { floors, cachedRooms, loadRooms, cachedItems, loadItems } from '../store';

    const params = useParams();

    const currentRoom = derived([params, cachedRooms], ([params, cachedRooms]) => {
        if (!cachedRooms[params.id]) {
            loadRooms([params.id]);
        }
        return cachedRooms[params.id];
    }, null);

    const currentFloor = derived([currentRoom, floors], ([currentRoom, floors]) => {
        if (currentRoom) {
            const floor = floors.filter((floor) => { return floor.id === (currentRoom.relationships.floor.data as JsonApiObjectReference).id});
            if (floor.length > 0) {
                return floor[0];
            }
        }
        return null;
    }, null);

    const items = derived([currentRoom, cachedItems], ([currentRoom, cachedItems]) => {
        if (currentRoom) {
            let itemIds = (currentRoom.relationships.items.data as JsonApiObjectReference[]).map((ref) => { return ref.id; });
            let items = itemIds.map((id) => { return cachedItems[id]; }).filter((item) => { return item; });
            if (itemIds.length != items.length) {
                loadItems(itemIds);
            }
            return items;
        }
        return [];
    }, []);
</script>

{#if $currentRoom && $currentFloor}
    <Header title="{$currentRoom.attributes.label}" nav={[{label: $currentFloor.attributes.label, path: '/floor/' + $currentFloor.id}, {label: $currentRoom.attributes.label, path: '/room/' + $currentRoom.id}]}/>
    <article>
        <ul class="grid grid-cols-1 md:grid-cols-items justify-around gap-8 p-4 overflow-hidden">
            {#each $items as item}
                <li><Thumnail item={item}/></li>
            {/each}
        </ul>
        <Route path=":iid"><Item/></Route>
    </article>
    <Footer/>
{/if}
