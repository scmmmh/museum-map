import { writable, derived } from 'svelte/store';

import { busyCounter } from './busy';

export const floorTopics = writable([] as JsonApiObject[]);

export async function fetchFloorTopics() {
    busyCounter.start();
    const response = await window.fetch('/api/floor-topics');
    if (response.status === 200) {
        const data = await response.json() as JsonApiResponse;
        floorTopics.set(data.data as JsonApiObject[]);
    }
    busyCounter.stop();
}

export const floors = writable([] as JsonApiObject[]);

export async function fetchFloors() {
    busyCounter.start();
    const response = await window.fetch('/api/floors');
    if (response.status === 200) {
        const data = await response.json() as JsonApiResponse;
        floors.set(data.data as JsonApiObject[]);
    }
    busyCounter.stop();
}

export const majorCollections = derived([floorTopics, floors], ([floorTopics, floors]) => {
    const topics = [];
    floorTopics.forEach((topic) => {
        if (topic.relationships && topic.relationships.group && topic.relationships.floor && topic.attributes) {
            const existingTopic = topics.filter((t) => { return topic.relationships && topic.relationships.group && t.groupId === (topic.relationships.group.data as JsonApiObjectReference).id});
            const floor = floors.filter((floor) => { return (topic.relationships.floor.data as JsonApiObjectReference).id === floor.id; });
            if (floor.length > 0) {
                if (existingTopic.length === 0) {
                    topics.push({
                        id: topic.id,
                        label: topic.attributes.label as string,
                        size: topic.attributes.size as number,
                        groupId: (topic.relationships.group.data as JsonApiObjectReference).id,
                        floors: floor
                    });
                } else {
                    existingTopic[0].size = existingTopic[0].size + (topic.attributes.size as number);
                    existingTopic[0].floors.push(floor[0]);
                }
            }
        }
    });
    topics.sort((a, b) => {
        return b.size - a.size;
    });
    return topics.slice(0, 6);
});
