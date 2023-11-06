import { writable } from 'svelte/store';

import { busyCounter } from './busy';

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
