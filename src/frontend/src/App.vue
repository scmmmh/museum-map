<template>
    <main>
        <header>
            <h1 v-if="isSmall"><button v-if="currentFloor && currentRoom" @click="setMapFloorId(currentFloor.id)">{{ roomTitle }}</button><template v-else>Museum Map</template></h1>
            <h1 v-else>Museum Map<template v-if="currentRoom"> - {{ roomTitle }}</template></h1>
            <nav>
                <ol>
                    <li><router-link :to="{name: 'lobby'}">Lobby</router-link></li>
                    <li v-if="currentFloor"><button @click="setMapFloorId(currentFloor.id)">{{ currentFloor.attributes.label }}</button></li>
                    <li v-if="currentRoom && !isSmall"><button @click="setMapFloorId(currentFloor.id)">Room {{ roomTitle }}</button></li>
                </ol>
            </nav>
        </header>
        <router-view></router-view>
        <footer>
            <div>
                <a href="https://www.room3b.eu/pages/projects/digital-museum-map.html" target="_blank" rel="noopener">Find out more<span class="hide-for-small"> about how this works</span></a>
            </div>
            <div>
                <a href="https://collections.vam.ac.uk/" target="_blank" rel="noopener">Objects, Images, and Meta-data provided by the V&amp;A</a>
            </div>
            <div>
                <a href="http://www.getty.edu/research/tools/vocabularies/aat/" target="_blank" rel="noopener">Includes part of the AAT</a>
            </div>
        </footer>
        <overview-map v-if="mapFloor"></overview-map>
        <div v-if="loading" id="loading">
            <div>Loading</div>
            <svg width="100" height="100" viewBox="0 0 38 38" xmlns="http://www.w3.org/2000/svg" stroke="#1e4b9b">
                <g fill="none" fill-rule="evenodd">
                    <g transform="translate(1 1)" stroke-width="2">
                        <path d="M36 18c0-9.94-8.06-18-18-18">
                            <animateTransform attributeName="transform" type="rotate" from="0 18 18" to="360 18 18" dur="1.5s" repeatCount="indefinite"/>
                        </path>
                    </g>
                </g>
            </svg>
        </div>
    </main>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '@/base';
import { JSONAPIItem, JSONAPIReference } from '@/store';
import OverviewMap from '@/components/OverviewMap.vue';

@Options({
    components: {
        OverviewMap,
    },
    watch: {
        roomTitle: (newVal) => {
            document.title = 'Room ' + newVal;
        }
    }
})
export default class App extends ComponentRoot {
    public get mapFloor() {
        if (this.$store.state.ui.mapFloorId && this.$store.state.objects.floors[this.$store.state.ui.mapFloorId]) {
            return this.$store.state.objects.floors[this.$store.state.ui.mapFloorId];
        } else {
            return null;
        }
    }

    public get loading() {
        return this.$store.state.ui.loadingCount > 0;
    }

    public get currentRoom() {
        if (this.$router.currentRoute) {
            if (this.$router.currentRoute.value.params.rid) {
                const rid = this.$router.currentRoute.value.params.rid as string;
                if (this.$store.state.objects.rooms[rid]) {
                    return this.$store.state.objects.rooms[rid];
                }
            }
        }
        return null;
    }

    public get roomTitle() {
        if (this.currentRoom && this.currentRoom.attributes) {
            return this.currentRoom.attributes.number + ' - ' + this.currentRoom.attributes.label;
        }
        return 'Museum Map';
    }

    public get currentFloor() {
        if (this.currentRoom) {
            if (this.currentRoom.relationships && this.currentRoom.relationships.floor) {
                const fid = (this.currentRoom.relationships.floor.data as JSONAPIReference).id;
                if (this.$store.state.objects.floors[fid]) {
                    return this.$store.state.objects.floors[fid];
                }
            }
        }
        return null;
    }

    public get isSmall() {
        return window.innerWidth <= 784;
    }

    public created() {
        this.$store.dispatch('fetchFloors').then((floors: JSONAPIItem[]) => {
            const itemIds = [] as string[];
            const topicIds = [] as string[];
            floors.forEach((floor) => {
                if (floor.relationships) {
                    (floor.relationships.samples.data as JSONAPIReference[]).forEach((ref) => {
                        if (!this.$store.state.objects.items[ref.id]) {
                            itemIds.push(ref.id);
                        }
                    });
                    (floor.relationships.topics.data as JSONAPIReference[]).forEach((ref) => {
                        if (!this.$store.state.objects['floor-topics'][ref.id]) {
                            topicIds.push(ref.id);
                        }
                    });
                }
            });
            if (itemIds.length > 0) {
                this.$store.dispatch('fetchItems', itemIds);
            }
            if (topicIds.length > 0) {
                this.$store.dispatch('fetchFloorTopics', topicIds);
            }
        });
    }

    public setMapFloorId(floor: JSONAPIItem | null) {
        this.$store.commit('setMapFloorId', floor);
    }
}
</script>

<style lang="scss">
body {
    margin: 0;
    padding: 0;

}

main {
    max-width: 1200px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #555555;
    color: #ffffff;
    position: relative;

    #loading {
        position: fixed;
        left: 0;
        top: 0;
        width: 100vw;
        height: 100vh;
        z-index: 10000;
        max-width: 1200px;

        div {
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            color: #ffffff;
            z-index: 2;
        }

        svg {
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            background: #222222cc;
            padding: 1rem;
            box-shadow: 0 0 20px #000000;
            z-index: 1;
        }
    }

    header, footer {
        flex: 0 0 auto;
        box-shadow: 0 0 10px #000000;
        z-index: 10;
    }

    h1 {
        font-size: 18px;
        margin: 0;
        padding: 0.3rem 0.5rem;
        border-bottom: 1px solid #666666;
    }

    header {
        h1 {
            button {
                cursor: pointer;
                border: 0;
                background: transparent;
                color: #ffffff;
                padding: 0;
                font-weight: inherit;

                &:hover {
                    text-decoration: underline;
                }
            }
        }
        nav {
            ol {
                list-style-type: none;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: row;

                li {
                    &:after {
                        content: '\00bb';
                    }

                    &:last-child {
                        &:after {
                            content: '';
                        }
                    }
                }

                a {
                    display: inline-block;
                    padding: 0.3rem 0.5rem;
                    cursor: pointer;
                }

                button {
                    display: inline-block;
                    padding: 0.3rem 0.5rem;
                    cursor: pointer;
                    border: 0;
                    background: transparent;
                    color: #ffffff;

                    &:hover {
                        text-decoration: underline;
                    }
                }
            }
        }
    }

    footer {
        font-size: 90%;
        padding: 0.3rem;
        display: flex;
        flex-direction: row;

        div {
            flex: 1 1 auto;
            text-align: center;
        }
    }

    article {
        flex: 1 1 auto;
        position: relative;
        overflow: hidden;

        &.lobby {
            ol {
                height: 100%;
                overflow: auto;
                margin: 0;
                padding: 0;
                list-style-type: none;

                > li {
                    padding: 0.5rem 1rem 1rem 1rem;

                    h2 {
                        margin: 0;

                        button {
                            border: 0;
                            background: transparent;
                            font-size: inherit;
                            font-weight: inherit;
                            color: inherit;
                            padding: 0;
                            margin: 0;
                            cursor: pointer;

                            &:hover {
                                text-decoration: underline;
                            }
                        }
                    }

                    ul {
                        list-style-type: none;
                        margin: 0;

                        &.samples {
                            padding-left: 0;
                            overflow: hidden;
                            display: flex;
                            flex-direction: row;
                            flex-wrap: nowrap;

                            li {
                                display: inline-block;
                                margin-right: 1rem;

                                figure {
                                    width: 5rem;
                                    height: 5rem;
                                    background: #000000;
                                    margin: 0;
                                    display: flex;
                                    justify-content: center;

                                    img {
                                        max-width: 100%;
                                        max-height: 100%;
                                    }
                                }
                            }
                        }

                        &.topics {
                            padding-left: 0;
                            padding-bottom: 1rem;

                            li {
                                display: inline;
                                padding: 0;
                                margin: 0;
                                font-size: 1.1rem;

                                + li {
                                    &:before {
                                        content: ', ';
                                    }
                                }

                                button {
                                    border: 0;
                                    padding: 0;
                                    color: #ffffff;
                                    background: transparent;
                                    cursor: pointer;

                                    &:hover, &:focus {
                                        text-decoration: underline;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        &.room {
            ol {
                height: 100%;
                overflow: auto;
                margin: 0;
                padding: 0;
                list-style-type: none;
                display: grid;
                grid-template-columns: repeat(auto-fill, 240px);
                column-gap: 2rem;
                row-gap: 2rem;
                justify-content: center;

                @media screen and (max-width: 784px) and (min-width: 241px) {
                    grid-template-columns: repeat(auto-fill, 320px);
                }

                li {
                    width: 240px;
                    height: 240px;

                    @media screen and (max-width: 784px) and (min-width: 241px) {
                        width: 320px;
                        height: 320px;
                    }

                    button {
                        display: block;
                        width: 100%;
                        height: 100%;
                        overflow: hidden;
                        cursor: pointer;
                        border: 0;
                        background: transparent;
                        color: #ffffff;
                    }

                    figure {
                        display: block;
                        width: 100%;
                        height: 100%;
                        position: relative;
                        margin: 0;
                        padding: 0;
                        background: #000000;

                        img {
                            max-width: 100%;
                            max-height: 100%;
                            position: absolute;
                            left: 50%;
                            top: 50%;
                            transform: translate(-50%, -50%);
                        }

                        figcaption {
                            position: absolute;
                            left: 0;
                            bottom: 0;
                            width: 100%;
                            z-index: 1;
                            background-color: #222222cc;
                            display: block;
                            box-sizing: border-box;
                            padding: 0.5rem;
                            opacity: 0;
                            transition: opacity 0.3s;
                        }
                    }

                    &:hover {
                        figcaption {
                            opacity: 1;
                        }
                    }
                }
            }

            section.item {
                position: absolute;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background: #222222cc;
                z-index: 2;

                > div {
                    position: relative;
                    margin: 3rem;
                    height: calc(100% - 6rem);
                    width: calc(100% - 6rem);
                    background: #222222;
                    display: flex;
                    flex-direction: row;
                    padding: 0;
                    box-shadow: 0 0 20px #000000;

                    @media screen and (max-width: 784px) {
                        margin: 0;
                        height: 100%;
                        width: 100%;
                        flex-direction: column;
                    }

                    a.close {
                        display: block;
                        position: absolute;
                        left: 0;
                        top: 0;
                        background: #222222cc;
                        color: #ffffff;
                        border: 0;
                        padding: 0.5rem 1rem;
                        font-size: 1.2rem;
                        cursor: pointer;
                        z-index: 2;
                    }

                    figure {
                        display: flex;
                        flex: 0 0 auto;
                        margin: 0;
                        background: #000000;
                        justify-content: center;
                        align-items: center;
                        width: 50%;

                        @media screen and (max-width: 784px) {
                            height: 50%;
                            width: 100%;
                        }

                        img {
                            max-height: 100%;
                            max-width: 100%;
                        }
                    }

                    > div {
                        flex: 0 0 auto;
                        display: flex;
                        flex-direction: column;
                        overflow: hidden;
                        padding: 0;
                        margin: 0;
                        width: 50%;

                        @media screen and (max-width: 784px) {
                            height: 50%;
                            width: 100%;
                        }

                        h2 {
                            background: #0040ad;
                            color: #ffffff;
                            font-size: 1.1rem;
                            padding: 1rem;
                            margin: 0;
                        }

                        > div {
                            flex: 1 1 auto;
                            overflow: auto;
                            padding: 0 1rem;

                            dl {
                                overflow: auto;
                                display: grid;
                                grid-template-columns: auto 1fr;
                                justify-content: start;

                                dt {
                                    font-size: 0.8rem;
                                    text-align: right;
                                    color: #aaaaaa;
                                    align-self: end;
                                    padding-bottom: 0.5rem;
                                }

                                dd {
                                    margin: 0;
                                    align-self: end;
                                    padding-left: 1rem;
                                    padding-bottom: 0.5rem;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    #map {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        z-index: 100;
        background: #222222cc;

        > div {
            position: absolute;
            left: 50%;
            top: 50%;
            width: calc(100% - 6rem);
            transform: translate(-50%, -50%);
            background: #222222;
            display: flex;
            flex-direction: row;
            box-shadow: 0 0 20px #000000;

            @media screen and (max-width: 784px) {
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                transform: none;
            }

            button.close {
                display: block;
                position: absolute;
                left: 0;
                top: 0;
                background: #222222cc;
                color: #ffffff;
                border: 0;
                padding: 0.5rem 1rem;
                font-size: 1.2rem;
                cursor: pointer;
                z-index: 2;

                &:hover, &:focus {
                    text-decoration: underline;
                }
            }

            .description {
                flex: 1 1 auto;
                display: flex;
                flex-direction: column;

                h2 {
                    margin: 0;
                    padding: 0.5rem 1rem;
                    display: flex;
                    flex-direction: row;
                    color: #ffffff;
                    background: #0040ad;
                    flex: 0 0 auto;

                    span {
                        flex: 1 1 auto;

                        @media screen and (max-width: 784px) {
                            padding-left: 1rem;
                        }
                    }

                    button {
                        flex: 0 0 auto;
                        padding: 0 0.2rem;
                        background: transparent;
                        border: 0;
                        cursor: pointer;

                        svg {
                            height: 24px;
                            width: 24px;

                            path {
                                fill: #ffffff;
                            }
                        }
                    }
                }

                > div {
                    flex: 1 1 auto;
                }

                ul {
                    list-style-type: none;
                    padding: 1rem;
                    margin: 0;

                    &.rooms {
                        flex: 1 1 auto;
                        overflow: auto;

                        li {
                            a {
                                display: block;
                                padding: 0.5rem 0;
                            }
                        }
                    }

                    &.topics {
                        li {
                            display: inline-block;
                            margin: 0;
                            padding: 0;

                            & + li {
                                &:before {
                                    content: ', ';
                                }
                            }
                        }
                    }
                }

                h3 {
                    flex: 0 0 auto;
                    margin: 0;
                    padding: 0.5rem 1rem;
                    color: #ffffff;
                    background: #0040ad;
                }

                figure {
                    background: #000000;
                    text-align: center;
                    margin: 0;
                    height: 140px;

                    img {
                        max-width: 100%;
                        max-height: 100%;
                    }
                }
            }

            .map {
                flex: 0 0 auto;
                background: #000000;
                padding: 1rem;
                font-family: Arial, Helvetica, sans-serif;

                @media screen and (max-width: 784px) {
                    display: none;
                }

                .wrapper {
                    position: relative;

                    a {
                        display: flex;
                        position: absolute;
                        border: 0;
                        background: #ffffff;
                        color: #000000;
                        padding: 0;
                        transition: color 0.2s, background-color 0.2s;
                        font-size: 8pt;
                        cursor: pointer;
                        align-items: center;

                        span {
                            flex: 1 1 auto;
                            text-align: center;
                        }

                        &:hover, &:focus, &[aria-selected=true] {
                            color: #ffffff;
                            background: #0040ad;
                            text-decoration: none;
                        }
                    }
                }
            }
        }
    }
}

a, button {
    color: #ffffff;
    text-decoration: none;
    font-family: inherit;
    font-size: inherit;

    &:hover {
        text-decoration: underline;
    }
}

.flex {
    display: flex;
    flex-direction: column;

    &.row {
        flex-direction: row;
    }

    > .shrink {
        flex: 0 0 auto;
    }

    > .expand {
        flex: 1 1 auto;
    }
}

figure {
    &.banner {
        display: block;
        margin: 0;
        padding: 0;
        max-height: 160px;
        overflow-y: hidden;

        img {
            transform: translateY(-20%);
            width: 100%;
        }
    }
}

.padding {
    padding: 1rem;
}

.border-box {
    box-sizing: border-box;
}

.invert {
    color: #222222;
    background: #ffffff;
}

@media screen and (max-width: 768px) {
    .hide-for-small {
        display: none;
    }
}
</style>
