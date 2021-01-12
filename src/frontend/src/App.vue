<template>
    <main>
        <header>
            <h1>Museum Map<template v-if="currentRoom && currentGroup"> - {{ currentRoom.attributes.number }} {{ currentGroup.attributes.label }}</template></h1>
            <nav>
                <ol>
                    <li><router-link to="/">Virtual Museum</router-link></li>
                    <li v-if="currentRoom && currentFloor"><button>{{ currentFloor.attributes.label }}</button></li>
                    <li v-if="currentRoom && currentGroup"><button>Room {{ currentRoom.attributes.number }} - {{ currentGroup.attributes.label }}</button></li>
                </ol>
            </nav>
        </header>
        <router-view></router-view>
    </main>
    <!--<main>
        <header>
            <h1>Museum Map - Drawings (12th-17th century)</h1>
            <nav>
                <ol>
                    <li><a>Virtual Museum</a></li>
                    <li><a>Floor 3</a></li>
                    <li><a aria-current="page">Room 32 - Drawings (12th-17th century)</a></li>
                </ol>
            </nav>
        </header>
        <nav id="floors" v-if="false">
            <div>
                <div class="flex">
                    <div class="expand padding">
                        <div class="shrink flex row">
                            <h2 class="expand">Floor 3</h2>
                            <div class="shrink">
                                <svg style="width:24px;height:24px" viewBox="0 0 24 24">
                                    <path fill="currentColor" d="M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z" />
                                </svg>
                                <svg style="width:24px;height:24px" viewBox="0 0 24 24">
                                    <path fill="currentColor" d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z" />
                                </svg>
                            </div>
                        </div>
                        <p class="shrink">Drawings, Paintings, China, Textiles, Prints, Photos, ...</p>
                    </div>
                    <div class="shrink">
                        <figure class="banner">
                            <img src="https://media.vam.ac.uk/media/thira/collection_images/2006AM/2006AM0953_jpg_w.jpg" alt=""/>
                        </figure>
                        <h3 class="padding invert">Watches</h3>
                    </div>
                </div>
                <div class="map">
                    <div class="base-layer">
                        <img src="@/assets/map.png" alt=""/>
                    </div>
                    <div class="room-layer">
                        <button>Photos</button>
                    </div>
                </div>
            </div>
        </nav>
        <article>
            <ul>
                <li v-for="item in items" :key="item.id">
                    <a>
                        <figure>
                            <img :src="item.image"/>
                            <figcaption>Drawing</figcaption>
                        </figure>
                    </a>
                </li>
            </ul>
        </article>
        <footer>
            <div>
                <a href="https://collections.vam.ac.uk/" target="_blank" rel="noopener">Objects, Images, and Meta-data provided by the V&amp;A</a>
            </div>
            <div>
                <a href="http://www.getty.edu/research/tools/vocabularies/aat/" target="_blank" rel="noopener">Includes part of the AAT</a>
            </div>
        </footer>
    </main>-->
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '@/base';
import { JSONAPIReference } from '@/store';

@Options({
    components: {
    },
})
export default class App extends ComponentRoot {
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

    public get currentGroup() {
        if (this.currentRoom) {
            if (this.currentRoom.relationships && this.currentRoom.relationships.group) {
                const gid = (this.currentRoom.relationships.group.data as JSONAPIReference).id;
                if (this.$store.state.objects.groups[gid]) {
                    return this.$store.state.objects.groups[gid];
                }
            }
        }
        return null;
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
}
</script>

<style lang="scss">
body {
    margin: 0;
    padding: 0;
}

main {
    width: 1200px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #555555;
    color: #ffffff;
    position: relative;

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
        padding-top: 0.5rem;
        position: relative;
        overflow: hidden;

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

            li {
                width: 240px;
                height: 240px;

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
                }

                figure {
                    display: flex;
                    flex: 0 0 auto;
                    margin: 0;
                    background: #000000;
                    justify-content: center;
                    align-items: center;
                    width: 50%;

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

    #floors {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        z-index: 100;
        background: #555555cc;

        > div {
            position: absolute;
            left: 50%;
            top: 50%;
            width: 80%;
            height: 80%;
            max-height: 600px;
            transform: translate(-50%, -50%);
            background: #555555;
            display: flex;
            flex-direction: row;
            box-shadow: 0 0 10px #000000;

            > div {
                height: 100%;

                &:first-child {
                    width: 33.33333%;
                }
                &:last-child {
                    width: 66.66666%;
                }
            }
        }

        h2 {
            margin: 0;
            font-size: 22px;
        }

        h3 {
            margin: 0;
            font-size: 20px;
            background: #0040adff;
            color: #ffffff;
        }

        .map {
            position: relative;
            transform-origin: top left;

            .base-layer {
                position: absolute;
                left: 1rem;
                top: 1rem;
                width: calc(100% - 2rem);
                height: calc(100% - 2rem);
                z-index: 1;
            }

            .room-layer {
                position: absolute;
                left: 1rem;
                top: 1rem;
                width: calc(100% - 2rem);
                height: calc(100% - 2rem);
                z-index: 2;

                button {
                    position: absolute;
                    left: 240px;
                    top: 81px;
                    width: 58px;
                    height: 238px;
                    color: #222222;
                    background: #ffffff;
                    font-size: 0.7rem;
                    border: 0;
                    cursor: pointer;
                    transition: color 0.1s, background-color 0.1s;

                    &:hover, &:focus {
                        background: #0040adff;
                        color: #ffffff;
                    }
                }
            }
        }
    }
}

a {
    color: #ffffff;
    text-decoration: none;

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
</style>
