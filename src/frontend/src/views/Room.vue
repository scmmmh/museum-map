<template>
    <article class="room">
        <ol>
            <li v-for="item in items" :key="item.id">
                <item-thumbnail :rid="rid" :item="item"/>
            </li>
        </ol>
        <floor-map v-if="mapFloor" :floor="mapFloor" :overlay="true"></floor-map>
        <router-view></router-view>
    </article>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '@/base';
import { JSONAPIReference } from '@/store';
import ItemThumbnail from '../components/ItemThumbnail.vue';
import FloorMap from '../components/FloorMap.vue';

@Options({
    components: {
        ItemThumbnail,
        FloorMap,
    },
    props: ['rid'],
    watch: {
        async rid(newValue: string) {
            await this.$store.dispatch('fetchRoom', newValue);
        }
    }
})
export default class Room extends ComponentRoot {
    $props!: {
        rid: string;
    };

    public get mapFloor() {
        if (this.$store.state.ui.mapFloorId && this.$store.state.objects.floors[this.$store.state.ui.mapFloorId]) {
            return this.$store.state.objects.floors[this.$store.state.ui.mapFloorId];
        } else {
            return null;
        }
    }

    public get room() {
        if (this.$store.state.objects.rooms[this.$props.rid]) {
            return this.$store.state.objects.rooms[this.$props.rid];
        }
        return null;
    }

    public get items() {
        if (this.room && this.room.relationships && this.room.relationships.items) {
            return (this.room.relationships.items.data as JSONAPIReference[]).map((ref) => {
                if (this.$store.state.objects.items[ref.id]) {
                    return this.$store.state.objects.items[ref.id];
                } else {
                    return null;
                }
            }).filter((item) => {
                return item !== null;
            });
        } else {
            return [];
        }
    }

    public created() {
        this.$store.dispatch('fetchRoom', this.$props.rid);
    }
}
</script>
