<template>
    <article class="room">
        <ol>
            <li v-for="item in items" :key="item.id">
                <router-link :to="'/room/' + rid + '/' + item.id">
                    <figure>
                        <img :src="thumbImageURL(item.attributes.images[0])" alt=""/>
                        <figcaption>{{ item.attributes.title ? item.attributes.title : '[untitled]' }}</figcaption>
                    </figure>
                </router-link>
            </li>
        </ol>
        <router-view></router-view>
    </article>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '@/base';

@Options({
    components: {
    },
    props: ['rid'],
    watch: {
        async rid(newValue: string) {
            this.$store.dispatch('fetchRoom', newValue);
            this.$store.dispatch('fetchRoomItems', newValue);
        }
    }
})
export default class Room extends ComponentRoot {
    $props!: {
        rid: string;
    };

    public get items() {
        if (this.$store.state.objects.items) {
            return Object.values(this.$store.state.objects.items);
        }
        return [];
    }

    public async created() {
        const promise = this.$store.dispatch('fetchRoom', this.$props.rid);
        promise.then(() => {
            this.$store.dispatch('fetchRoomItems', this.$props.rid);
        });
    }

    public thumbImageURL(imageId: string) {
        return '/images/' + imageId.split('').join('/') + '/' + imageId + '-thumb.jpg';
    }

}
</script>
