import { writable, derived } from 'svelte/store';

import { busyCounter } from './busy';

export const status = writable(null as { version: string, ready: boolean });

export async function fetchStatus() {
    busyCounter.start();
    const response = await window.fetch('/api');
    if (response.status === 200) {
        const data = await response.json();
        status.set(data as { version: string, ready: boolean });
    }
    busyCounter.stop();
}

export const isUpdatable = derived(status, (status) => {
    return status !== null && status.version !== '0.8.2';
});

export const config = writable(null as JsonApiObject);

export async function fetchConfig() {
    busyCounter.start();
    const response = await window.fetch('/api/config/all');
    if (response.status === 200) {
        const data = await response.json() as JsonApiResponse;
        config.set(data.data as JsonApiObject);
    }
    busyCounter.stop();
}
