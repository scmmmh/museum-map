<template>
    <main>
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
    </main>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

@Options({
    components: {
    },
})
export default class App extends Vue {
    items = [
        {id: 1, image: 'https://media.vam.ac.uk/media/thira/collection_images/2009CP/2009CP5568_jpg_ds.jpg'},
        {id: 2, image: 'https://media.vam.ac.uk/media/thira/collection_images/2014HB/2014HB6438_jpg_ws.jpg'},
        {id: 3, image: 'https://media.vam.ac.uk/media/thira/collection_images/2011FA/2011FA5317_jpg_ws.jpg'},
        {id: 4, image: 'https://media.vam.ac.uk/media/thira/collection_images/2010EJ/2010EJ1362_jpg_ws.jpg'},
        {id: 5, image: 'https://media.vam.ac.uk/media/thira/collection_images/2010EL/2010EL8510_jpg_ws.jpg'},
        {id: 6, image: 'https://media.vam.ac.uk/media/thira/collection_images/2009CP/2009CP5568_jpg_ds.jpg'},
        {id: 7, image: 'https://media.vam.ac.uk/media/thira/collection_images/2009CP/2009CP5568_jpg_ds.jpg'},
        {id: 8, image: 'https://media.vam.ac.uk/media/thira/collection_images/2017JW/2017JW8908_jpg_ws.jpg'},
        {id: 9, image: 'https://media.vam.ac.uk/media/thira/collection_images/2011EU/2011EU0058_jpg_ws.jpg'},
        {id: 10, image: 'https://media.vam.ac.uk/media/thira/collection_images/2015HJ/2015HJ4655_jpg_ws.jpg'},
        {id: 11, image: 'https://media.vam.ac.uk/media/thira/collection_images/2015HX/2015HX0218_jpg_ws.jpg'},
        {id: 12, image: 'https://media.vam.ac.uk/media/thira/collection_images/2013GD/2013GD8526_jpg_ws.jpg'},
        {id: 13},
        {id: 14},
        {id: 15},
        {id: 16},
        {id: 17},
        {id: 18},
        {id: 19},
        {id: 20},
        {id: 21},
        {id: 22},
        {id: 23},
        {id: 24},
        {id: 25},
        {id: 26},
        {id: 27},
        {id: 28},
        {id: 29},
        {id: 30},
        {id: 31},
        {id: 32},
        {id: 33},
        {id: 34},
        {id: 35},
        {id: 36},
        {id: 37},
        {id: 38},
        {id: 39},
        {id: 40},
    ]
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
        overflow: auto;
        padding-top: 0.5rem;

        ul {
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

                a {
                    display: block;
                    width: 100%;
                    height: 100%;
                    overflow: hidden;
                    cursor: pointer;
                }

                figure {
                    display: block;
                    width: 100%;
                    height: 100%;
                    position: relative;
                    margin: 0;
                    padding: 0;
                    background: #ffffff;

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

    #floors {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        z-index: 100;
        background: #555555cc;

        & > div {
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
