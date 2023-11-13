/// <reference types="svelte" />
/// <reference types="vite/client" />

type APIStatus = {
  ready: boolean,
  version: string,
};

type LogAction = {
  action: string,
  params: object,
};

type Floor = {
  id: number,
  label: string,
  level: number,
  rooms: number[],
  samples: number[],
  topics: number[],
};

type FloorTopic = {
  id: number,
  label: string,
  size: number,
  floor: number,
  group: number,
};
