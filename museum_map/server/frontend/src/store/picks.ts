import { writable, get } from 'svelte/store';

import { busyCounter } from './busy';
import { tracker } from "./tracking";

// The item of the day
export const itemOfTheDay = writable(null as JsonApiObject | null);

// Fetch the item of the day
export async function fetchItemOfTheDay() {
    busyCounter.start();
    const response = await window.fetch('/api/picks/todays');
    if (response.status === 200) {
        const data = await response.json() as JsonApiResponse;
        if ((data.data as JsonApiObject[]).length > 0) {
            const newItem = (data.data as JsonApiObject[])[0];
            const currentItem = get(itemOfTheDay);
            if (currentItem === null || currentItem.id !== newItem.id) {
                itemOfTheDay.set(newItem);
            }
        }
    }
    busyCounter.stop();
}

// A random selection of items
export const randomItemsSelection = writable([] as JsonApiObject[]);

// Fetch a random selection of items
export async function fetchRandomItemsSelection() {
    busyCounter.start();
    const response = await window.fetch('/api/picks/random');
    if (response.status === 200) {
        tracker.log({ action: "reload-random-selection", params: {} })
        const data = await response.json() as JsonApiResponse;
        randomItemsSelection.set(data.data as JsonApiObject[]);
    }
    busyCounter.stop();
}
