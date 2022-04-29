import { derived, writable } from 'svelte/store';

/**
 * Create a busy counter store, which has start and end functions to indicate
 * activity starting/ending.
 */
function createBusyCounter() {
    const { subscribe, update } = writable(0);

    return {
        subscribe,
        start: () => { update((count) => { return count + 1})},
        stop: () => { update((count) => { return Math.max(0, count - 1)})},
    }
}

// A busy counter
export const busyCounter = createBusyCounter();
// A boolean indicator of whether the application is busy
export const isBusy = derived(busyCounter, (count) => {
    return count > 0;
});
