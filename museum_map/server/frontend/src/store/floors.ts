import { writable, derived } from 'svelte/store';

import { busyCounter } from './busy';
import { isReady } from './status';

export const floorTopics = writable([] as JsonApiObject[]);

export async function fetchFloorTopics() {
  busyCounter.start();
  const response = await window.fetch('/api/floor-topics');
  if (response.status === 200) {
    const data = await response.json() as JsonApiResponse;
    floorTopics.set(data.data as JsonApiObject[]);
  }
  busyCounter.stop();
}

import type { Subscriber, Unsubscriber, Readable } from 'svelte/store';

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
  return {
    subscribe,
  }
}

type Floor = {
  id: number,
  label: string,
  level: number,
  rooms: number[],
  samples: number[],
  topics: number[],
};

export const floors = DependentStore<null | Floor[], boolean>([], async (isReady) => {
  if (isReady) {
    busyCounter.start();
    try {
      const response = await window.fetch('/api/floors/');
      if (response.status === 200) {
        return await response.json() as Floor[];
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

export const majorCollections = derived([floorTopics, floors], ([floorTopics, floors]) => {
  const topics = [];
  floorTopics.forEach((topic) => {
    if (topic.relationships && topic.relationships.group && topic.relationships.floor && topic.attributes) {
      const existingTopic = topics.filter((t) => { return topic.relationships && topic.relationships.group && t.groupId === (topic.relationships.group.data as JsonApiObjectReference).id });
      const floor = floors.filter((floor) => { return (topic.relationships.floor.data as JsonApiObjectReference).id === floor.id; });
      if (floor.length > 0) {
        if (existingTopic.length === 0) {
          topics.push({
            id: topic.id,
            label: topic.attributes.label as string,
            size: topic.attributes.size as number,
            groupId: (topic.relationships.group.data as JsonApiObjectReference).id,
            floors: floor
          });
        } else {
          existingTopic[0].size = existingTopic[0].size + (topic.attributes.size as number);
          existingTopic[0].floors.push(floor[0]);
        }
      }
    }
  });
  topics.sort((a, b) => {
    return b.size - a.size;
  });
  return topics.slice(0, 6);
});
