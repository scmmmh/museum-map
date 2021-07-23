<template>
    <article class="lobby">
        <div class="todays-picks">
            <h2>Item of the day</h2>
            <div>
                <item-thumbnail v-if="todaysPick" :rid="todaysPick.relationships.room.data.id" :item="todaysPick"/>
            </div>
        </div>
        <div class="main-areas">
            <h2>Major Collections</h2>
            <ol>
                <li v-for="topic in topics" :key="topic.id">
                    <h3>{{topic.label}}</h3>
                    <ul>
                        <li v-for="floor in topic.floors" :key="floor"><router-link :to="{name: 'floor', params: {fid: floor.id}}">{{floor.attributes.label}}</router-link></li>
                    </ul>
                </li>
            </ol>
            <div v-if="floorZero">
                <router-link :to="{name: 'floor', params: {fid: floorZero.id}}">Explore the whole collection &rarr;</router-link>
            </div>
        </div>
        <div class="random-picks">
            <h2>
                <span>Selection from our collections</span>
                <button @click="updateRandomPicks" aria-label="Update selection" title="Select a different set of items from our collection">
                    <svg viewBox="0 0 24 24" class="icon">
                        <path d="M2 12C2 16.97 6.03 21 11 21C13.39 21 15.68 20.06 17.4 18.4L15.9 16.9C14.63 18.25 12.86 19 11 19C4.76 19 1.64 11.46 6.05 7.05C10.46 2.64 18 5.77 18 12H15L19 16H19.1L23 12H20C20 7.03 15.97 3 11 3C6.03 3 2 7.03 2 12Z" />
                    </svg>
                </button>
            </h2>
            <ul>
                <li v-for="item in randomPicks" :key="item.id">
                    <item-thumbnail v-if="item.relationships.room" :rid="item.relationships.room.data.id" :item="item"/>
                </li>
            </ul>
        </div>
    </article>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '@/base';
import { JSONAPIItem, JSONAPIReference } from '@/store';
import ItemThumbnail from '../components/ItemThumbnail.vue';

interface LobbyTopic {
    id: string;
    label: string;
    size: number;
    groupId: string;
    floors: JSONAPIItem[];
}

@Options({
    components: {
        ItemThumbnail,
    }
})
export default class Lobby extends ComponentRoot {
    public sampleWidth = '';
    public randomPicks = [];
    public todaysPick = null;

    public get topics() {
        if (this.$store.state.objects['floor-topics']) {
            const topics = [] as LobbyTopic[];
            Object.values(this.$store.state.objects['floor-topics']).forEach((topic) => {
                if (topic.relationships && topic.relationships.group && topic.relationships.floor && topic.attributes) {
                    const existingTopic = topics.filter((t) => { return topic.relationships && topic.relationships.group && t.groupId === (topic.relationships.group.data as JSONAPIReference).id});
                    const floor = this.$store.state.objects.floors[(topic.relationships.floor.data as JSONAPIReference).id];
                    if (existingTopic.length === 0) {
                        topics.push({
                            id: topic.id,
                            label: topic.attributes.label as string,
                            size: topic.attributes.size as number,
                            groupId: (topic.relationships.group.data as JSONAPIReference).id,
                            floors: [floor]
                        });
                    } else {
                        existingTopic[0].size = existingTopic[0].size + (topic.attributes.size as number);
                        existingTopic[0].floors.push(floor);
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
    }

    public get floorZero() {
        const floors = Object.values(this.$store.state.objects['floors']);
        if (floors.length > 0) {
            floors.sort((a, b) => {
                if (a.attributes && b.attributes) {
                    return (a.attributes.level as number) - (b.attributes.level as number);
                } else {
                    return 0;
                }
            });
            return floors[0];
        } else {
            return null;
        }
    }

    public created() {
        this.$store.dispatch('fetchFloors');
        this.$store.dispatch('fetchItemPicks', 'random').then((data) => {
            this.randomPicks = data;
        });
        this.$store.dispatch('fetchItemPicks', 'todays').then((data) => {
            if (data.length > 0) {
                this.todaysPick = data[0];
            } else {
                this.todaysPick = null;
            }
        });
    }

    public updateRandomPicks() {
        this.$store.dispatch('fetchItemPicks', 'random').then((data) => {
            this.randomPicks = data;
        });
    }
}
</script>
