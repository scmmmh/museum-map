import { writable, derived } from 'svelte/store';

import { busyCounter } from './busy';
import { isReady } from './status';
import { DependentStore } from './util';

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

export const floorTopics = DependentStore<null | FloorTopic[], boolean>(null, async (isReady) => {
  if (isReady) {
    busyCounter.start();
    try {
      const response = await window.fetch('/api/floor-topics/');
      if (response.status === 200) {
        return await response.json() as FloorTopic[];
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
  return [];
  /*const topics = [];
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
  return topics.slice(0, 6);*/
});
