<template>
    <main>
        <header>
            <h1 v-if="isSmall"><button v-if="currentFloor && currentRoom" @click="setMapFloorId(currentFloor.id)">{{ roomTitle }}</button><template v-else>Museum Map</template></h1>
            <h1 v-else>Museum Map<template v-if="currentRoom"> - {{ roomTitle }}</template></h1>
            <nav>
                <ol>
                    <li><router-link :to="{name: 'lobby'}">Lobby</router-link></li>
                    <li v-if="currentFloor"><router-link :to="{name: 'floor', params: {fid: currentFloor.id}}">{{ currentFloor.attributes.label }}</router-link></li>
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
import OverviewMap from '@/components/FloorMap.vue';

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
        } else if (this.$router.currentRoute) {
            if (this.$router.currentRoute.value.params.fid) {
                const fid = this.$router.currentRoute.value.params.fid as string;
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

    public setMapFloorId(floor: JSONAPIItem | null) {
        this.$store.commit('setMapFloorId', floor);
    }
}
</script>

<style lang="scss">
body {
    margin: 0;
    padding: 0;
    background: #333333;
}

.icon {
    width: 1rem;
    height: 1rem;
}

main {
    max-width: 1200px;
    margin: 0 auto;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #555555;
    color: #ffffff;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 10px #000000;

    #loading {
        position: fixed;
        left: 0;
        top: 0;
        width: 100vw;
        height: 100vh;
        z-index: 10000;

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
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            margin-bottom: 2rem;
            overflow: auto;

            @media screen and (max-width: 784px) and (min-width: 241px) {
                display: flex;
                flex-direction: column;
                overflow-y: auto;
            }

            .main-areas {
                padding: 0 1rem;
                display: flex;
                flex-direction: column;

                @media screen and (max-width: 784px) and (min-width: 241px) {
                    order: 2;
                }

                h3 {
                    margin: 0 0 0.3rem 0;
                    flex: 0 0 auto;
                }

                ol {
                    flex: 1 1 auto;
                    list-style-type: none;
                    margin: 0;
                    padding: 0;
                    column-count: 2;

                    > li {
                        break-inside: avoid-column;
                        page-break-inside: avoid;
                    }

                    ul {
                        list-style-type: none;
                        margin: 0 0 1rem 0;
                        padding: 0;

                        li {
                            display: inline-block;

                            &::after {
                                content: ',';
                                padding-right: 0.3rem;
                            }

                            &:last-child {
                                &::after {
                                    content: '';
                                }
                            }
                        }
                    }
                }

                div {
                    flex: 0 0 auto;
                    padding: 1rem 0;
                    text-align: center;

                    a {
                        display: inline-block;
                        padding: 0.5rem 0.8rem;
                        font-size: 130%;
                        font-weight: bold;
                        letter-spacing: 0.3rem;
                        background: #0040ad;
                        color: #ffffff;
                    }
                }
            }

            .todays-picks {
                padding: 0 1rem;
                display: flex;
                flex-direction: column;

                @media screen and (max-width: 784px) and (min-width: 241px) {
                    height: 40vh;
                    order: 1;
                    flex: 0 0 auto;
                }

                h2 {
                    flex: 0 0 auto;
                }

                div {
                    flex: 1 1 auto;

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
                                opacity: 1;
                                transition: opacity 0.3s;
                            }

                            @media screen and (max-width: 784px) and (min-width: 241px) {
                                figcaption {
                                    opacity: 0;
                                }
                            }
                        }

                        &:hover {
                            figcaption {
                                opacity: 1;
                            }
                        }
                }
            }

            .random-picks {
                padding: 0 1rem;
                grid-column-start: 1;
                grid-column-end: 3;
                display: flex;
                flex-direction: column;

                @media screen and (max-width: 784px) and (min-width: 241px) {
                    order: 3;
                }

                h2 {
                    flex: 0 0 auto;
                    display: flex;
                    flex-direction: row;

                    span {
                        flex: 1 1 auto;
                    }

                    button {
                        flex: 0 0 auto;
                        cursor: pointer;
                        background: transparent;
                        border: 0;
                        padding: 0.2rem 0.3rem;

                        svg {
                            fill: #ffffff;
                        }

                        &:hover {
                            svg {
                                fill: #dfdfdf;
                            }
                        }
                    }
                }

                ul {
                    flex: 1 1 auto;
                    list-style-type: none;
                    display: flex;
                    flex-direction: row;
                    flex-wrap: wrap;
                    margin: 0;
                    padding: 0;

                    @media screen and (max-width: 784px) and (min-width: 241px) {
                        flex-direction: column;
                    }

                    li {
                        margin: 0.5rem 0.5rem;
                        padding: 0;
                        flex: 1 1 auto;
                        height: 100%;
                        min-width: 240px;

                        @media screen and (max-width: 784px) and (min-width: 241px) {
                            height: 40vh;
                            margin: 0.5rem 0;
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
            }
        }

        &.floor {
            display: flex;
            flex-direction: row;
            margin: 1rem 0;
            overflow-y: auto;

            > ol {
                flex: 0 0 auto;
                list-style-type: none;
                margin: 0;
                padding: 0 2rem 0 1rem;
                max-width: 25%;
                overflow-y: auto;

                a {
                    display: block;

                    &.router-link-exact-active {
                        font-weight: bold;
                    }

                    > span {
                        display: block;
                        padding: 0 0 0 0.5rem;
                        font-size: 90%;
                        color: #cccccc;

                        > span {
                            display: inline-block;
                            margin: 0;
                            padding: 0;

                            &:after {
                                content: ',';
                                padding-right: 0.3rem;
                            }

                            &:last-child {
                                &:after {
                                    content: '';
                                }
                            }
                        }
                    }
                }

                > li {
                    margin-bottom: 0.5rem;
                }
            }

            > #map {
                flex: 1 1 auto;
                padding-right: 1rem;
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
        &.overlay {
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
                box-shadow: 0 0 20px #000000;
            }
        }

        > div {
            display: flex;
            flex-direction: row;

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
                background: #222222;

                h2 {
                    margin: 0;
                    padding: 0.5rem 1rem;
                    display: flex;
                    flex-direction: row;
                    color: #ffffff;
                    background: #0040ad;
                    flex: 0 0 auto;

                    span, a {
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

                            &:after {
                                content: ',';
                                padding-right: 0.3rem;
                            }

                            &:last-child {
                                &:after {
                                    content: '';
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
