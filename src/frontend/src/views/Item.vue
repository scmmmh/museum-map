<template>
    <section class="item" @click="overlayClick" ref="itemPopup">
        <div v-if="item">
            <router-link :to="'/room/' + rid" class="close">&#x2716;</router-link>
            <figure>
                <img :src="imageURL(item.attributes.images[0])" alt=""/>
            </figure>
            <div>
                <h2>{{ item.attributes.title ? item.attributes.title : '[untitled]' }}</h2>
                <div>
                    <template v-if="item.attributes.description">
                        <p v-for="(text, idx) in processText(item.attributes.description)" :key="idx" v-html="text"></p>
                    </template>
                    <template v-if="item.attributes.notes">
                        <p v-for="(text, idx) in processText(item.attributes.notes)" :key="idx" v-html="text"></p>
                    </template>
                    <dl>
                        <template v-for="field in fields" :key='field[1]'>
                            <template v-if="item.attributes[field[1]] && item.attributes[field[1]].length">
                                <dt>{{ field[0] }}</dt>
                                <dd>{{ formatField(item.attributes[field[1]]) }}</dd>
                            </template>
                        </template>
                    </dl>
                </div>
            </div>
        </div>
    </section>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '@/base';
import { JSONAPIItem } from '@/store';

@Options({
    components: {
    },
    props: ['rid', 'iid'],
    watch: {
        async iid(newValue) {
            this.item = await this.$store.dispatch('fetchItem', newValue);
        }
    }
})
export default class Item extends ComponentRoot {
    public $props!: {
        rid: string;
        iid: string;
    };
    public item: null | JSONAPIItem = null;
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

    public mounted() {
        this.$store.dispatch('fetchItem', this.$props.iid).then((item) => {
            this.item = item;
        });
    }

    public overlayClick(ev: MouseEvent) {
        if (ev.target === this.$refs.itemPopup) {
            this.$router.push({name: 'room', params: {rid: this.$props.rid }});
        }
    }

    public imageURL(imageId: string) {
        return '/images/' + imageId.split('').join('/') + '/' + imageId + '.jpg';
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
