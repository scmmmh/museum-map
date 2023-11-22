import deepcopy from "deepcopy";
import { writable, derived } from 'svelte/store';
import { location } from "../simple-svelte-router";

import { busyCounter } from './busy';
import { currentRoom } from "./rooms";

let itemsIdQueryCache: number[] = [];
let itemsQueryPromise: Promise<Item[]> | null = null;

export async function fetchItems(itemIds: number[]): Promise<Item[]> {  // TODO: Filter existing items for caching
  if (itemsQueryPromise === null) {
    itemsIdQueryCache = deepcopy(itemIds);
    itemsQueryPromise = new Promise<Item[]>((resolve) => {
      setTimeout(async () => {
        try {
          busyCounter.start();
          const fetchitemIds = itemsIdQueryCache;
          itemsIdQueryCache = [];
          itemsQueryPromise = null;
          const response = await window.fetch("/api/items/?" + fetchitemIds.map((id) => { return "iid=" + id }).join("&"));
          if (response.status === 200) {
            const newItems = await response.json() as Item[];
            items.update((items) => {
              for (let item of newItems) {
                items[item.id] = item;
              }
              return items;
            })
            resolve(newItems);
          } else {
            resolve([]);
          }
        } finally {
          busyCounter.stop();
        }
      }, 5);
    });
  } else {
    itemsIdQueryCache = itemsIdQueryCache.concat(itemIds);
  }
  return itemsQueryPromise;
}

export const items = writable({} as { [x: number]: Item });

export const currentItems = derived([items, currentRoom], ([items, currentRoom]) => {
  if (currentRoom) {
    return currentRoom.items.map((itemId) => {
      if (items[itemId]) {
        return items[itemId];
      } else {
        fetchItems([itemId]);
        return null;
      }
    }).filter((room) => {
      return room !== null;
    }) as Item[];
  }
  return [];
});

export const currentItem = derived([items, location], ([items, location]) => {
  if (location.pathComponents.iid) {
    if (items[Number.parseInt(location.pathComponents.iid)]) {
      return items[Number.parseInt(location.pathComponents.iid)];
    } else {
      fetchItems([Number.parseInt(location.pathComponents.iid)]);
    }
  }
  return null;
});

/*const activeQueries = [];

export const cachedItems = writable({} as { [x: string]: JsonApiObject });

export async function loadItems(itemIds: string[]): Promise<JsonApiObject[]> {
    const $cachedItems = get(cachedItems);
    const missingIds = itemIds.filter((id) => { return !$cachedItems[id] });
    if (missingIds.length > 0) {
        const url = '/api/items?filter[id]=' + missingIds.map((id) => { return id }).join(',');
        if (activeQueries.indexOf(url) < 0) {
            busyCounter.start();
            activeQueries.push(url);
            const response = await window.fetch(url);
            if (response.status === 200) {
                const data = await response.json();
                for (const item of data.data) {
                    $cachedItems[item.id] = item;
                }
                cachedItems.set($cachedItems);
            }
            busyCounter.stop();
            activeQueries.splice(activeQueries.indexOf(url), 1);
        }
    }
    return itemIds.map((id) => { return $cachedItems[id]; });
}
*/
