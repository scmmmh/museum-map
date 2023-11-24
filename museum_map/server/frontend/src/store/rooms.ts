import { derived } from 'svelte/store';
import { location } from "../simple-svelte-router";

import { busyCounter } from './busy';
import { currentFloor } from "./floors";
import { createCachingStore } from "./util";

export const rooms = createCachingStore<Room>(async (ids) => {
  busyCounter.start();
  const response = await window.fetch("/api/rooms/?" + ids.map((id) => { return "rid=" + id }).join("&"));
  if (response.status === 200) {
    busyCounter.stop()
    return (await response.json()) as Room[];
  }
  busyCounter.stop()
  return [];
});

export const currentRooms = derived([rooms, currentFloor], ([$rooms, currentFloor], set) => {
  if (currentFloor) {
    rooms.fetch(currentFloor.rooms).then(set);
  } else {
    set([]);
  }
}, [] as Room[]);

export const currentRoom = derived([rooms, location], ([$rooms, location], set) => {
  if (location.pathComponents.rid) {
    rooms.fetch([Number.parseInt(location.pathComponents.rid)]).then((rooms) => {
      if (rooms.length > 0) {
        set(rooms[0]);
      } else {
        set(null);
      }
    })
  } else {
    set(null);
  }
}, null as Room | null);
