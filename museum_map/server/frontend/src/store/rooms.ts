import deepcopy from "deepcopy";
import { writable, get } from 'svelte/store';

import { busyCounter } from './busy';

export const rooms = writable({} as { [x: number]: Room });

let roomsIdQueryCache: number[] = [];
let roomsQueryPromise: Promise<Room[]> | null = null;

export async function fetchRooms(roomIds: number[]): Promise<Room[]> {  // TODO: Filter existing rooms for caching
  if (roomsQueryPromise === null) {
    roomsIdQueryCache = deepcopy(roomIds);
    roomsQueryPromise = new Promise<Room[]>((resolve) => {
      setTimeout(async () => {
        try {
          busyCounter.start();
          const fetchRoomIds = roomsIdQueryCache;
          roomsIdQueryCache = [];
          roomsQueryPromise = null;
          const response = await window.fetch("/api/rooms/?" + fetchRoomIds.map((id) => { return "rid=" + id }).join("&"));
          if (response.status === 200) {
            const newRooms = await response.json() as Room[];
            rooms.update((rooms) => {
              for (let room of newRooms) {
                rooms[room.id] = room;
              }
              return rooms;
            })
            resolve(newRooms);
          } else {
            resolve([]);
          }
        } finally {
          busyCounter.stop();
        }
      }, 5);
    });
  } else {
    roomsIdQueryCache = roomsIdQueryCache.concat(roomIds);
  }
  return roomsQueryPromise;
  /*    try {
          busyCounter.start();
          const response = await window.fetch("/api/rooms/?" + roomIds.map((id) => { return "rid=" + id }).join("&"));
          if (response.status === 200) {
              return await response.json() as Room[];
          } else {
              return [];
          }
      } finally {
          busyCounter.stop();
      }*/
}
