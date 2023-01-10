import { writable, get } from 'svelte/store';

import { busyCounter } from './busy';

const activeQueries = [];

export const cachedTopics = writable({} as {[x:string]: JsonApiObject});

export async function loadTopics(topicIds: string[]): Promise<JsonApiObject[]> {
    const $cachedTopics = get(cachedTopics);
    const missingIds = topicIds.filter((id) => { return !$cachedTopics[id]});
    if (missingIds.length > 0) {
        const url = '/api/floor-topics?filter[id]=' + missingIds.map((id) => { return id}).join(',');
        if (activeQueries.indexOf(url) < 0) {
            busyCounter.start();
            const response = await window.fetch(url);
            if (response.status === 200) {
                const data = await response.json();
                for (const room of data.data) {
                    $cachedTopics[room.id] = room;
                }
                cachedTopics.set($cachedTopics);
            }
            busyCounter.stop();
            activeQueries.splice(activeQueries.indexOf(url), 1);
        }
    }
    return topicIds.map((id) => { return $cachedTopics[id]; });
}
