import { writable, derived } from 'svelte/store';

import { busyCounter } from './busy';
import { isReady } from './status';
import { DependentStore } from './util';

// The list of available floors
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

// The list of all floor topics
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

// Major collections (defined as the six largest floor topics)
export const majorCollections = derived([floorTopics, floors], ([floorTopics, floors]) => {
  if (floorTopics !== null && floors !== null) {
    const topics: MajorCollection[] = [];
    floorTopics.forEach((topic) => {
      const existingTopic = topics.filter((t) => { return t.group === topic.group });
      const floor = floors.filter((floor) => { return topic.floor === floor.id; });
      if (floor.length > 0) {
        if (existingTopic.length === 0) {
          topics.push({
            id: topic.id,
            label: topic.label,
            size: topic.size,
            group: topic.group,
            floors: floor
          });
        } else {
          existingTopic[0].size = existingTopic[0].size + topic.size;
          existingTopic[0].floors.push(floor[0]);
        }
      }
    });
    topics.sort((a, b) => {
      return b.size - a.size;
    });
    return topics.slice(0, 6);
  } else {
    return [];
  }
}, [] as MajorCollection[]);
