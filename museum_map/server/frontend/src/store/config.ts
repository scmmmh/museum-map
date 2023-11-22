import { writable } from 'svelte/store';

import { busyCounter } from './busy';
import { DependentStore } from './util';
import { isReady } from './status';

// The application configuration
export const config = DependentStore<null | Config, boolean>(null, async (isReady) => {
  if (isReady) {
    busyCounter.start();
    try {
      const response = await window.fetch('/api/config/');
      if (response.status === 200) {
        return await response.json() as Config;
      } else {
        return null;
      }
    } catch (e) {
      console.error(e);
      return null;
    } finally {
      busyCounter.stop();
    }
  } else {
    return null;
  }
}, isReady);
