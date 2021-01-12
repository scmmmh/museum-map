<template>
    <article class="room">
        <ol>
            <li v-for="item in items" :key="item.id">
                <button @click="selectItem(item)">
                    <figure>
                        <img :src="thumbImageURL(item.attributes.images[0])" alt=""/>
                        <figcaption>{{ item.attributes.title ? item.attributes.title : '[untitled]' }}</figcaption>
                    </figure>
                </button>
            </li>
        </ol>
        <section v-if="selectedItem" class="item" @click="overlayClick" ref="selectedItemPopup">
            <div>
                <button class="close" @click="selectItem(null)">&#x2716;</button>
                <figure>
                    <img :src="imageURL(selectedItem.attributes.images[0])" alt=""/>
                </figure>
                <div>
                    <h2>{{ selectedItem.attributes.title ? selectedItem.attributes.title : '[untitled]' }}</h2>
                    <div>
                        <template v-if="selectedItem.attributes.description">
                            <p v-for="(text, idx) in processText(selectedItem.attributes.description)" :key="idx" v-html="text"></p>
                        </template>
                        <template v-if="selectedItem.attributes.notes">
                            <p v-for="(text, idx) in processText(selectedItem.attributes.notes)" :key="idx" v-html="text"></p>
                        </template>
                        <dl>
                            <template v-for="field in fields" :key='field[1]'>
                                <template v-if="selectedItem.attributes[field[1]] && selectedItem.attributes[field[1]].length">
                                    <dt>{{ field[0] }}</dt>
                                    <dd>{{ formatField(selectedItem.attributes[field[1]]) }}</dd>
                                </template>
                            </template>
                        </dl>
                    </div>
                </div>
            </div>
        </section>
    </article>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '@/base';
import { JSONAPIItem } from '@/store';

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

    public fields = [
        ['Object', 'object'],
        ['Concepts', 'concepts'],
        ['Materials', 'materials'],
        ['Techniques', 'techniques'],
        ['Styles', 'styles'],
        ['Dimensions', 'dimensions'],
        ['Date', 'date'],
        ['Place made', 'place_made'],
        ['Subjects', 'subjects'],
        ['People', 'people'],
        ['Organisations', 'organisations'],
        ['Events', 'events'],
        ['Marks', 'marks'],
        ['Credit', 'credit'],
        ['Collections', 'collections'],
        ['Physical location', 'physical_location'],
    ];
    public selectedItem: JSONAPIItem | null = null;

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

    public imageURL(imageId: string) {
        return '/images/' + imageId.split('').join('/') + '/' + imageId + '.jpg';
    }

    public thumbImageURL(imageId: string) {
        return '/images/' + imageId.split('').join('/') + '/' + imageId + '-thumb.jpg';
    }

    public selectItem(item: JSONAPIItem | null) {
        this.selectedItem = item;
    }

    public overlayClick(ev: MouseEvent) {
        if (ev.target === this.$refs.selectedItemPopup) {
            this.selectItem(null);
        }
    }

    public formatField(item: string | string[]) {
        if (Array.isArray(item)) {
            return item.join(', ');
        } else {
            return item;
        }
    }

    public processText(text: string) {
        const paras = [] as string[];
        text.split('\n\n').forEach((part1) => {
            part1.split('<br><br>').forEach((part2) => {
                paras.push(part2
                    .replace(/<[iI]>/g, '\\begin{em}')
                    .replace(/<\/[iI]>/g, '\\end{em}')
                    .replace(/<[uU]>/g, '\\begin{em}')
                    .replace(/<\/[uU]>/g, '\\end{em}')
                    .replace(/<[bB]>/g, '\\begin{strong}')
                    .replace(/<\/[bB]>/g, '\\end{strong}')
                    .replace(/<\/?[a-zA-Z]+>/g, '')
                    .replace('\\begin{em}', '<em>')
                    .replace('\\end{em}', '</em>')
                    .replace('\\begin{strong}', '<strong>')
                    .replace('\\end{strong}', '</strong>')
                );
            });
        });
        return paras;
    }
}
</script>
