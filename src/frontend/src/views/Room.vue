<template>
    <article class="room">
        <ol>
            <li v-for="item in items" :key="item.id">
                <router-link :to="'/room/' + rid + '/' + item.id">
                    <figure>
                        <img :src="thumbImageURL(item.attributes.images[0])" alt=""/>
                        <figcaption v-html="item.attributes.title ? processParagraph(item.attributes.title) : '[untitled]'"></figcaption>
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
import { JSONAPIReference } from '@/store';

@Options({
    components: {
    },
    props: ['rid'],
    watch: {
        async rid(newValue: string) {
            const room = await this.$store.dispatch('fetchRoom', newValue);
            if (room.relationships && room.relationships.items) {
                const ids = (room.relationships.items.data as JSONAPIReference[]).map((ref) => {
                    if (this.$store.state.objects.items[ref.id]) {
                        return null;
                    } else {
                        return ref.id;
                    }
                }).filter((id) => {
                    return id !== null;
                });
                if (ids.length > 0) {
                    this.$store.dispatch('fetchItems', ids);
                }
            }
        }
    }
})
export default class Room extends ComponentRoot {
    $props!: {
        rid: string;
    };

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
        this.$store.dispatch('fetchRoom', this.$props.rid).then((room) => {
            if (room.relationships && room.relationships.items) {
                const ids = (room.relationships.items.data as JSONAPIReference[]).map((ref) => {
                    if (this.$store.state.objects.items[ref.id]) {
                        return null;
                    } else {
                        return ref.id;
                    }
                }).filter((id) => {
                    return id !== null;
                });
                if (ids.length > 0) {
                    this.$store.dispatch('fetchItems', ids);
                }
            }
        });
    }

    public thumbImageURL(imageId: string) {
        if (imageId) {
            return '/images/' + imageId.split('').join('/') + '/' + imageId + '-thumb.jpg';
        } else {
            return '';
        }
    }

    public processParagraph(paragraph: string) {
        return paragraph
            .replace(/<[iI]>/g, '\\begin{em}')
            .replace(/<\/[iI]>/g, '\\end{em}')
            .replace(/<[uU]>/g, '\\begin{em}')
            .replace(/<\/[uU]>/g, '\\end{em}')
            .replace(/<[bB]>/g, '\\begin{strong}')
            .replace(/<\/[bB]>/g, '\\end{strong}')
            .replace(/<\/?[a-zA-Z]+>/g, '')
            .replace(/\\begin\{em\}/g, '<em>')
            .replace(/\\end\{em\}/g, '</em>')
            .replace(/\\begin\{strong\}/g, '<strong>')
            .replace(/\\end\{strong\}/g, '</strong>');
    }
}
</script>
