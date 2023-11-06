import { writable } from "svelte/store";
import type { Subscriber, Unsubscriber } from 'svelte/store';

/**
 * A readable store that updates its value at the given interval.
 *
 * Supports both async and non-async functions for the value calculation.
 *
 * @param initial The initial state of the store
 * @param value The function to call to get the new value
 * @param interval The interval in milliseconds to update at
 * @returns
 */
export function IntervalStore<StoreType>(initial: StoreType, value: () => StoreType | Promise<StoreType>, interval: number) {
    const store = writable(initial);
    let subscriberCount = 0;
    let updateInterval = -1;

    function subscribe(subscriber: Subscriber<StoreType>): Unsubscriber {
        if (subscriberCount === 0) {
            Promise.resolve(value()).then((value) => {
                store.set(value);
            });
            updateInterval = window.setInterval(() => {
                Promise.resolve(value()).then((value) => {
                    store.set(value);
                });
            }, interval);
        }
        subscriberCount++;
        const unsubscribe = store.subscribe(subscriber)

        return () => {
            unsubscribe();
            subscriberCount--;
            if (subscriberCount === 0) {
                window.clearInterval(updateInterval);
            }
        };
    }

    return {
        subscribe,
    }
}
