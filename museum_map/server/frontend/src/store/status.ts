import { derived } from 'svelte/store';

import { busyCounter } from './busy';
import { IntervalStore } from './util';

/**
 * API Status Store.
 *
 * Is automatically refreshed every 60 seconds.
 */
export const status = IntervalStore<null | APIStatus>(null, async () => {
  busyCounter.start();
  try {
    const response = await window.fetch('/api');
    if (response.status === 200) {
      return await response.json() as APIStatus;
    } else {
      return null;
    }
  } catch (e) {
    console.error(e);
    return null;
  } finally {
    busyCounter.stop();
  }
}, 60000);

/**
 * Whether we could connect to the API.
 */
export const isConnected = derived(status, (status) => {
  return status !== null;
});

/**
 * Whether the API is ready.
 */
export const isReady = derived(status, (status) => {
  return status !== null && status.ready;
});

/**
 * Whether there is the need for a version update of the frontend.
 */
export const isUpdatable = derived(status, (status) => {
  return status !== null && status.version !== '0.9.1';
});
