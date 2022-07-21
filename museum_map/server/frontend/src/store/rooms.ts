import { writable, get } from 'svelte/store';

import { busyCounter } from './busy';

const activeQueries = [];

export const cachedRooms = writable({} as {[x:string]: JsonApiObject});

export async function loadRooms(roomIds: string[]): Promise<JsonApiObject[]> {
    const $cachedRooms = get(cachedRooms);
    const missingIds = roomIds.filter((id) => { return !$cachedRooms[id]});
    if (missingIds.length > 0) {
        const url = '/api/rooms?filter[id]=' + missingIds.map((id) => { return id}).join(',');
        if (activeQueries.indexOf(url) < 0) {
            busyCounter.start();
            const response = await window.fetch(url);
            if (response.status === 200) {
                const data = await response.json();
                for (const room of data.data) {
                    $cachedRooms[room.id] = room;
                }
                cachedRooms.set($cachedRooms);
            }
            busyCounter.stop();
            activeQueries.splice(activeQueries.indexOf(url), 1);
        }
    }
    return roomIds.map((id) => { return $cachedRooms[id]; });
}
