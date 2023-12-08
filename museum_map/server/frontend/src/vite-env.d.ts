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

type TrackEntry = {
  timestamp: number,
  action: string,
  params: object,
};

type User = {
  id: string,
};

type FooterConfig = {
  label: string,
  url: string,
};

type FootersConfig = {
  center: FooterConfig,
  right: FooterConfig,
};

type ItemMetadataConfig = {
  name: string,
  label: string,
};

type ItemConfig = {
  texts: ItemMetadataConfig[],
  fields: ItemMetadataConfig[],
};

type Config = {
  base_url: string,
  intro: string,
  footer: FootersConfig,
  item: ItemConfig,
}

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

type Room = {
  id: number,
  label: string,
  levelnumber: string,
  position: MapObjectPosition,
  group: number,
  floor: number,
  sample: number,
  items: number[],
}

type MajorCollection = {
  id: number,
  label: string,
  size: number,
  group: number,
  floors: Floor[],
};

type Item = {
  id: number,
  group: number,
  room: number,
  attributes: ItemAttributes,
  sequence: number,
};

type ItemAttributes = {
  title: string,
  images: string[][],
};

type MapObjectPosition = {
  x: number,
  y: number,
  width: number,
  height: number,
};

type MapObject = {
  position: MapObjectPosition;
  rect: Phaser.GameObjects.Rectangle;
  text: Phaser.GameObjects.Text;
};
