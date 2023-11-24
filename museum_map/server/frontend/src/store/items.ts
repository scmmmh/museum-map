import { derived } from 'svelte/store';
import { location } from "../simple-svelte-router";

import { busyCounter } from './busy';
import { currentRoom } from "./rooms";
import { createCachingStore } from "./util";

export const items = createCachingStore<Item>(async (ids) => {
  busyCounter.start();
  const response = await window.fetch("/api/items/?" + ids.map((id) => { return "iid=" + id }).join("&"));
  if (response.status === 200) {
    busyCounter.stop()
    return (await response.json()) as Item[];
  }
  busyCounter.stop()
  return [];
});

export const currentItems = derived([items, currentRoom], ([$items, currentRoom], set) => {
  if (currentRoom) {
    items.fetch((currentRoom.items)).then((items) => {
      set(items);
    });
  } else {
    set([]);
  }
}, [] as Item[]);

export const currentItem = derived([items, location], ([$items, location], set) => {
  if (location.pathComponents.iid) {
    items.fetch([Number.parseInt(location.pathComponents.iid)]).then((items) => {
      if (items.length > 0) {
        set(items[0]);
      } else {
        set(null);
      }
    });
  } else {
    set(null);
  }
}, null as Item | null);
