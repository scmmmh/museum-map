<template>
    <section id="map" :class="overlay ? 'overlay' : ''">
        <div>
            <button v-if="!isSmall && overlay" class="close" @click="setMapFloorId(null)">&#x2716;</button>
            <div class="map">
                <div class="wrapper">
                    <img src="@/assets/map.png" alt=""/>
                    <router-link v-for="room in rooms" :key="room.id" :to="{name: 'room', params: {rid: room.id}}" :style="room.attributes.position" :aria-selected="highlightedRoom && room.id === highlightedRoom.id ? 'true' : 'false'" @click="setMapFloorId(null)" @mouseover="highlightRoom(room)"><span>{{ mapLabel(room.attributes.label) }}</span></router-link>
                </div>
            </div>
            <div class="description">
                <h2>
                    <button v-if="isSmall && overlay" @click="setMapFloorId(null)">&#x2716;</button>
                    <router-link v-if="overlay" :to="{name: 'floor', params: {fid: floor.id}}">{{ floor.attributes.label }}</router-link>
                    <span v-else>{{ floor.attributes.label }}</span>
                    <template v-if="overlay">
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
                    </template>
                </h2>
                <template v-if="isSmall">
                    <ul class="rooms">
                        <li v-for="room in rooms" :key="room.id"><router-link :to="{name: 'room', params: {rid: room.id}}" :aria-selected="highlightedRoom && room.id === highlightedRoom.id ? 'true' : 'false'" @click="setMapFloorId(null)" @mouseover="highlightRoom(room)">{{ room.attributes.label }}</router-link></li>
                    </ul>
                </template>
                <template v-else>
                    <ul class="topics">
                        <li v-for="topic in floorTopics" :key="topic.id">{{ topic.attributes.label }}</li>
                    </ul>
                    <div></div>
                    <section v-if="highlightedRoom">
                        <h3>{{ highlightedRoom.attributes.label }}</h3>
                        <figure v-if="highlightedRoomItem">
                            <img :src="thumbImageURL(highlightedRoomItem.attributes.images[0])" alt=""/>
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
    props: ['floor', 'overlay'],
    watch: {
        async floor(newValue: JSONAPIItem) {
            await this.$store.dispatch('fetchFloor', newValue.id);
        }
    }
})
export default class FloorMap extends ComponentRoot {
    $props!: {
        floor: JSONAPIItem;
        overlay: boolean;
    }
    public highlightedRoom: JSONAPIItem | null = null;

    public get highlightedRoomItem() {
        if (this.highlightedRoom && this.highlightedRoom.relationships && this.highlightedRoom.relationships.sample) {
            if (this.$store.state.objects.items[(this.highlightedRoom.relationships.sample.data as JSONAPIReference).id]) {
                return this.$store.state.objects.items[(this.highlightedRoom.relationships.sample.data as JSONAPIReference).id];
            } else {
                this.$store.dispatch('fetchItem', (this.highlightedRoom.relationships.sample.data as JSONAPIReference).id);
            }
        }
        return null;
    }

    public get rooms() {
        if (this.$props.floor && this.$props.floor.relationships) {
            const rooms = (this.$props.floor.relationships.rooms.data as JSONAPIReference[]).map((ref) => {
                if (this.$store.state.objects.rooms[ref.id]) {
                    return this.$store.state.objects.rooms[ref.id];
                } else {
                    return null;
                }
            }).filter((room) => {
                return room !== null;
            });
            return rooms;
        }
        return [];
    }

    public get floorTopics() {
        if (this.$props.floor && this.$props.floor.relationships) {
            const topics = (this.$props.floor.relationships.topics.data as JSONAPIReference[]).map((ref) => {
                if (this.$store.state.objects['floor-topics'][ref.id]) {
                    return this.$store.state.objects['floor-topics'][ref.id];
                } else {
                    return null;
                }
            }).filter((item) => {
                return item !== null;
            });
            return topics;
        }
        return [];
    }

    public created() {
        this.$store.dispatch('fetchFloor', this.$props.floor.id);
    }

    public get isSmall() {
        return window.innerWidth <= 784;
    }

    public setMapFloorId(floor: number | null) {
        this.$store.commit('setMapFloorId', floor);
    }

    public highlightRoom(room: JSONAPIItem) {
        this.highlightedRoom = room;
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

    public moveFloorUpDown(direction: number) {
        const floors = Object.values(this.$store.state.objects.floors) as JSONAPIItem[];
        floors.sort((a, b) => {
            if (a.attributes && b.attributes) {
                return (a.attributes.level as number) - (b.attributes.level as number);
            } else {
                return 0;
            }
        });
        this.$store.commit('setMapFloorId', floors[Math.min(Math.max(floors.indexOf(this.$props.floor) + direction, 0), floors.length - 1)].id);
    }
}
</script>
