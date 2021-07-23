<template>
    <article class="floor">
        <ol>
            <li v-for="floor in floors" :key="floor.floor.id">
                <router-link :to="{name: 'floor', params: {fid: floor.floor.id}}">{{floor.floor.attributes.label}}
                    <span>
                        <span v-for="topic in floor.topics" :key="topic.id">{{topic.attributes.label}}</span>
                    </span>
                </router-link>
            </li>
        </ol>
        <floor-map v-if="floor" :floor="floor" :overlay="false"/>
    </article>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '@/base';
import FloorMap from '../components/FloorMap.vue';
import { JSONAPIItem, JSONAPIReference } from '@/store';

@Options({
    components: {
        FloorMap,
    },
    props: ['fid']
})
export default class Room extends ComponentRoot {
    $props!: {
        fid: string;
    };

    public get floors() {
        const floors = Object.values(this.$store.state.objects.floors) as JSONAPIItem[];
        floors.sort((a, b) => {
            if (a.attributes && b.attributes) {
                return (a.attributes.level as number) - (b.attributes.level as number);
            } else {
                return 0;
            }
        });
        return floors.map((floor) => {
            let topics = [] as JSONAPIItem[];
            if (floor.relationships) {
                topics = (floor.relationships.topics.data as JSONAPIReference[]).map((ref) => {
                    if (this.$store.state.objects['floor-topics'][ref.id]) {
                        return this.$store.state.objects['floor-topics'][ref.id];
                    } else {
                        return null;
                    }
                }).filter((item) => { return item !== null; }) as JSONAPIItem[];
            }
            return {
                floor: floor,
                topics: topics
            }
        });
    }

    public get floor() {
        if (this.$store.state.objects.floors[this.$props.fid]) {
            return this.$store.state.objects.floors[this.$props.fid];
        }
        return null;
    }

    public created() {
        this.$store.dispatch('fetchFloors');
    }
}
</script>
