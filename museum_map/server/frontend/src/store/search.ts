import { writable, get } from 'svelte/store';

export const searchTerm = writable('');

export const searchRoom = writable(null as string | null);

export const matchingFloors = writable([] as string[]);

export const matchingRooms = writable([] as string[]);

export const matchingItems = writable([] as string[]);

searchTerm.subscribe((searchTerm) => {
    runSearch();
});

searchRoom.subscribe((searchRoom) => {
    runSearch();
})

async function runSearch() {
    const $searchTerm = get(searchTerm);
    const $searchRoom = get(searchRoom);
    if ($searchTerm.trim() !== '') {
        let url = '/api/search?q=' + encodeURIComponent($searchTerm);
        if ($searchRoom !== null) {
            url = url + '&room=' + $searchRoom;
        }
        const response = await window.fetch(url);
        if (response.status === 200) {
            const result = await response.json();
            matchingFloors.set(Object.keys(result.facetDistribution.mmap_floor));
            matchingRooms.set(Object.keys(result.facetDistribution.mmap_room));
            matchingItems.set(result.hits.map((hit: {mmap_id: string}) => { return hit.mmap_id.toString(); }))
        } else {
            matchingFloors.set([]);
            matchingRooms.set([]);
            matchingItems.set([]);
        }
    } else {
        matchingFloors.set([]);
        matchingRooms.set([]);
        matchingItems.set([]);
    }
}
