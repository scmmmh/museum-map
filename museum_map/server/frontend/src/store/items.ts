import { writable, get } from 'svelte/store';

import { busyCounter } from './busy';

const activeQueries = [];

export const cachedItems = writable({} as {[x: string]: JsonApiObject});

export async function loadItems(itemIds: string[]): Promise<JsonApiObject[]> {
    const $cachedItems = get(cachedItems);
    const missingIds = itemIds.filter((id) => { return !$cachedItems[id]});
    if (missingIds.length > 0) {
        const url = '/api/items?filter[id]=' + missingIds.map((id) => { return id}).join(',');
        if (activeQueries.indexOf(url) < 0) {
            busyCounter.start();
            activeQueries.push(url);
            const response = await window.fetch(url);
            if (response.status === 200) {
                const data = await response.json();
                for (const item of data.data) {
                    $cachedItems[item.id] = item;
                }
                cachedItems.set($cachedItems);
            }
            busyCounter.stop();
            activeQueries.splice(activeQueries.indexOf(url), 1);
        }
    }
    return itemIds.map((id) => { return $cachedItems[id]; });
}
