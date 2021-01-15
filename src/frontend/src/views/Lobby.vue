<template>
    <article class="lobby">
        <ol>
            <li v-for="floor in floors" :key="floor.floor.id">
                <h2><button @click="setMapFloorId(floor.floor.id)">{{ floor.floor.attributes.label }}</button></h2>
                <ul class="topics">
                    <li v-for="topic in floor.topics" :key="topic.id">
                        <router-link :to="{name: 'room', params: {rid: topic.relationships.room.data.id}}">{{ topic.attributes.label }}</router-link>
                    </li>
                    <li><button @click="setMapFloorId(floor.floor.id)">...</button></li>
                </ul>
                <ul class="samples">
                    <li v-for="item in floor.samples" :key="item.id">
                        <router-link :to="{name: 'item', params: {rid: item.relationships.room.data.id, iid: item.id}}">
                            <figure>
                                <img :src="thumbImageURL(item.attributes.images[0])" :alt="item.attributes.title ? item.attributes.title : '[untitled]'"/>
                            </figure>
                        </router-link>
                    </li>
                </ul>
            </li>
        </ol>
    </article>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '@/base';
import { JSONAPIItem, JSONAPIReference } from '@/store';

interface LobbyEntry {
    floor: JSONAPIItem;
    rooms: LobbyEntryRoom[];
}

interface LobbyEntryRoom {
    room: JSONAPIItem;
    group: JSONAPIItem;
}

@Options({
    components: {
    }
})
export default class Lobby extends ComponentRoot {
    public get floors() {
        if (this.$store.state.objects.floors) {
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
            return floors.map((floor) => {
                if (floor.relationships) {
                    const topics = (floor.relationships.topics.data as JSONAPIReference[]).map((ref) => {
                        if (this.$store.state.objects['floor-topics'][ref.id]) {
                            return this.$store.state.objects['floor-topics'][ref.id];
                        } else {
                            return null;
                        }
                    }).filter((item) => {
                        return item !== null;
                    });
                    const samples = (floor.relationships.samples.data as JSONAPIReference[]).map((ref) => {
                        if (this.$store.state.objects.items[ref.id]) {
                            return this.$store.state.objects.items[ref.id];
                        } else {
                            return null;
                        }
                    }).filter((item) => {
                        return item !== null;
                    });
                    return {
                        floor: floor,
                        samples: samples,
                        topics: topics,
                    };
                } else {
                    return null;
                }
            }).filter((item) => {
                return item !== null;
            });
        }
        return [];
    }

    public setMapFloorId(floorId: string) {
        this.$store.commit('setMapFloorId', floorId);
    }

    public thumbImageURL(imageId: string) {
        if (imageId) {
            return '/images/' + imageId.split('').join('/') + '/' + imageId + '-thumb.jpg';
        } else {
            return '';
        }
    }
}
</script>
