import { writable, get } from "svelte/store";
import type { Subscriber, Unsubscriber, Readable } from 'svelte/store';
import deepcopy from "deepcopy";

/**
 * A readable store that updates its value at the given interval.
 *
 * Supports both async and non-async functions for the value calculation.
 *
 * @param initial The initial state of the store
 * @param value The function to call to get the new value
 * @param interval The interval in milliseconds to update at
 * @returns A new store
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


/**
 * A store that depends on the value of another store.
 *
 * @param initial The initial value to set.
 * @param value The function to calculate the value based on the parent value.
 * @param parent The parent store that this store depends on.
 * @returns A new store
 */
export function DependentStore<StoreType, ParentType>(initial: StoreType, value: (v: ParentType) => StoreType | Promise<StoreType>, parent: Readable<ParentType>) {
  const store = writable(initial);
  let subscriberCount = 0;
  let parentUnsubscribe: null | Unsubscriber = null;

  function subscribe(subscriber: Subscriber<StoreType>) {
    if (subscriberCount === 0) {
      parentUnsubscribe = parent.subscribe((parentValue: any) => {
        Promise.resolve(value(parentValue)).then((v) => {
          store.set(v);
        })
      });
    }
    subscriberCount++;
    const unsubscribe = store.subscribe(subscriber);
    return () => {
      unsubscribe();
      subscriberCount--;
      if (subscriberCount === 0 && parentUnsubscribe !== null) {
        parentUnsubscribe();
        parentUnsubscribe = null;
      }
    }
  }

  function refresh() {
    Promise.resolve(value(get(parent))).then((v) => {
      store.set(v);
    });
  }

  return {
    subscribe,
    refresh,
  }
}

type IdType = {
  id: number,
};

/**
 * A store that acts as a cache.
 *
 * When requesting items via the fetch function, will automatically fetch any uncached items from remote.
 *
 * @param value The function to load uncached ids
 * @returns A new store
 */
export function createCachingStore<StoreType extends IdType>(value: (ids: number[]) => StoreType[] | Promise<StoreType[]>) {
  const store = writable({} as {[x: number]: StoreType});

  let idsBuffer: number[] = [];
  let requestPromise: Promise<{[x: number]: StoreType}> | null = null;

  async function fetch(ids: number[]): Promise<StoreType[]> {
    if (requestPromise === null) {
      idsBuffer = deepcopy(ids);
      requestPromise = new Promise<{[x: number]: StoreType}>((resolve) => {
        setTimeout(() => {
          const idsToFetch: number[] = [];
          const $store = get(store);
          for (const id of idsBuffer) {
            if (!$store[id] && idsToFetch.indexOf(id) < 0) {
              idsToFetch.push(id);
            }
          }
          idsBuffer = [];
          requestPromise = null;
          if (idsToFetch.length > 0) {
            Promise.resolve(value(idsToFetch)).then((items) => {
              store.update((store) => {
                for (const item of items) {
                  store[item.id] = item;
                }
                return store;
              });
              resolve($store);
            });
          } else {
            resolve($store);
          }
        }, 5);
      });
    } else {
      idsBuffer = idsBuffer.concat(ids);
    }
    const items = await requestPromise;
    return ids.map((id) => { return items[id]; });
  }

  return {
    subscribe: store.subscribe,
    fetch,
  }
}
