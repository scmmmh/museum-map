import deepcopy from "deepcopy";
import { writable, derived } from 'svelte/store';
import { location } from "../simple-svelte-router";

import { busyCounter } from './busy';
import { currentFloor } from "./floors";

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
}

export const rooms = writable({} as { [x: number]: Room });

export const currentRooms = derived([rooms, currentFloor], ([rooms, currentFloor]) => {
  if (currentFloor) {
    return currentFloor.rooms.map((roomId) => {
      if (rooms[roomId]) {
        return rooms[roomId];
      } else {
        fetchRooms([roomId]);
        return null;
      }
    }).filter((room) => {
      return room !== null;
    }) as Room[];
  }
  return [];
});

export const currentRoom = derived([rooms, location], ([rooms, location]) => {
  if (location.pathComponents.rid) {
    if (rooms[Number.parseInt(location.pathComponents.rid)]) {
      return rooms[Number.parseInt(location.pathComponents.rid)];
    } else {
      fetchRooms([Number.parseInt(location.pathComponents.rid)]);
    }
  }
  return null;
});
