<template>
    <section id="map">
        <div>
            <button v-if="!isSmall" class="close" @click="setMapFloorId(null)">&#x2716;</button>
            <div class="map">
                <div class="wrapper">
                    <img src="@/assets/map.png" alt=""/>
                    <router-link v-for="room in mapFloorRooms" :key="room.id" :to="{name: 'room', params: {rid: room.id}}" :style="room.attributes.position" :aria-selected="selectedRoom && room.id === selectedRoom.id ? 'true' : 'false'" @click="setMapFloorId(null)" @mouseover="highlightRoom(room)"><span>{{ mapLabel(room.attributes.label) }}</span></router-link>
                </div>
            </div>
            <div class="description">
                <h2>
                    <button v-if="isSmall" @click="setMapFloorId(null)">&#x2716;</button>
                    <span>{{ mapFloor.attributes.label }}</span>
                    <button @click="moveFloorUpDown(1)">
                        <svg viewBox="0 0 24 24">
                            <path d="M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z" />
                        </svg>
                    </button>
                    <button @click="moveFloorUpDown(-1)">
                        <svg viewBox="0 0 24 24">
                            <path d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z" />
                        </svg>
                    </button>
                </h2>
                <template v-if="isSmall">
                    <ul class="rooms">
                        <li v-for="room in mapFloorRooms" :key="room.id"><router-link :to="{name: 'room', params: {rid: room.id}}" :aria-selected="selectedRoom && room.id === selectedRoom.id ? 'true' : 'false'" @click="setMapFloorId(null)" @mouseover="highlightRoom(room)">{{ room.attributes.label }}</router-link></li>
                    </ul>
                </template>
                <template v-else>
                    <ul class="topics">
                        <li v-for="topic in mapFloorTopics" :key="topic.id">{{ topic.attributes.label }}</li>
                        <li>...</li>
                    </ul>
                    <div></div>
                    <section v-if="selectedRoom">
                        <h3>{{ selectedRoom.attributes.label }}</h3>
                        <figure v-if="selectedRoomItem">
                            <img :src="thumbImageURL(selectedRoomItem.attributes.images[0])" alt=""/>
                        </figure>
                    </section>
                </template>
            </div>
        </div>
    </section>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '@/base';
import { JSONAPIItem, JSONAPIReference } from '@/store';

@Options({
})
export default class OverviewMap extends ComponentRoot {
    public selectedRoom: JSONAPIItem | null = null;

    public get selectedRoomItem() {
        if (this.selectedRoom && this.selectedRoom.relationships && this.selectedRoom.relationships.sample) {
            if (this.$store.state.objects.items[(this.selectedRoom.relationships.sample.data as JSONAPIReference).id]) {
                return this.$store.state.objects.items[(this.selectedRoom.relationships.sample.data as JSONAPIReference).id];
            } else {
                this.$store.dispatch('fetchItem', (this.selectedRoom.relationships.sample.data as JSONAPIReference).id);
            }
        }
        return null;
    }

    public get mapFloor() {
        if (this.$store.state.ui.mapFloorId && this.$store.state.objects.floors[this.$store.state.ui.mapFloorId]) {
            return this.$store.state.objects.floors[this.$store.state.ui.mapFloorId];
        } else {
            return null;
        }
    }

    public get mapFloorRooms() {
        if (this.mapFloor && this.mapFloor.relationships) {
            const missingIds = [] as string[];
            const rooms = (this.mapFloor.relationships.rooms.data as JSONAPIReference[]).map((ref) => {
                if (this.$store.state.objects.rooms[ref.id]) {
                    return this.$store.state.objects.rooms[ref.id];
                } else {
                    missingIds.push(ref.id);
                    return null;
                }
            }).filter((room) => {
                return room !== null;
            });
            if (missingIds.length > 0) {
                this.$store.dispatch('fetchRooms', missingIds).then((rooms: JSONAPIItem[]) => {
                    const itemIds = rooms.map((room) => {
                        if (room.relationships && room.relationships.sample) {
                            if (!this.$store.state.objects.items[(room.relationships.sample.data as JSONAPIReference).id]) {
                                return (room.relationships.sample.data as JSONAPIReference).id;
                            }
                        }
                        return null;
                    }).filter((item) => {
                        return item !== null;
                    });
                    if (itemIds.length > 0) {
                        this.$store.dispatch('fetchItems', itemIds);
                    }
                });
            }
            return rooms;
        }
        return [];
    }

    public get mapFloorTopics() {
        if (this.mapFloor && this.mapFloor.relationships) {
            const topicIds = [] as string[];
            const topics = (this.mapFloor.relationships.topics.data as JSONAPIReference[]).map((ref) => {
                if (this.$store.state.objects['floor-topics'][ref.id]) {
                    return this.$store.state.objects['floor-topics'][ref.id];
                } else {
                    topicIds.push(ref.id)
                    return null;
                }
            }).filter((item) => {
                return item !== null;
            });
            if (topicIds.length > 0) {
                this.$store.dispatch('fetchFloorTopics', topicIds);
            }
            return topics;
        }
        return [];
    }

    public get isSmall() {
        return window.innerWidth <= 784;
    }

    public setMapFloorId(floor: JSONAPIItem | null) {
        this.$store.commit('setMapFloorId', floor);
    }

    public moveFloorUpDown(direction: number) {
        let floors = Object.values(this.$store.state.objects.floors);
        floors = floors.sort((a, b) => {
            if (a.attributes && b.attributes) {
                return (a.attributes.level as number) - (b.attributes.level as number);
            } else if (a.attributes) {
                return -1;
            } else if (b.attributes) {
                return 1;
            } else {
                return 0;
            }
        });
        for (let idx = 0; idx < floors.length; idx++) {
            if (floors[idx].id === this.$store.state.ui.mapFloorId) {
                if (idx + direction >= 0 && idx + direction < floors.length) {
                    this.$store.commit('setMapFloorId', floors[idx + direction].id);
                    break;
                }
            }
        }
    }

    public highlightRoom(room: JSONAPIItem) {
        this.selectedRoom = room;
    }

    public mapLabel(label: string) {
        if (label.indexOf(' - ') >= 0) {
            return label.substring(0, label.indexOf(' - '));
        } else {
            return label;
        }
    }

    public thumbImageURL(imageId: string) {
        if (imageId) {
            return '/images/' + imageId.split('').join('/') + '/' + imageId + '.jpg';
        } else {
            return '';
        }
    }
}
</script>
