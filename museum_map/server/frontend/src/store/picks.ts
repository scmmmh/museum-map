import { writable, get } from 'svelte/store';

import { busyCounter } from './busy';
import { tracker } from "./tracking";
import { DependentStore } from './util';
import { isReady } from './status';

// The item of the day
export const itemOfTheDay = DependentStore<null | Item, boolean>(null, async (isReady) => {
  if (isReady) {
    busyCounter.start();
    try {
      const response = await window.fetch('/api/picks/item-of-the-day');
      if (response.status === 200) {
        return await response.json() as Item;
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


// A random selection of items
export const randomItemsSelection = DependentStore<null | Item[], boolean>(null, async (isReady) => {
  if (isReady) {
    busyCounter.start();
    try {
      const response = await window.fetch('/api/picks/random-items');
      if (response.status === 200) {
        return await response.json() as Item[];
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
