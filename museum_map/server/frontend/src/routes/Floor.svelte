<script lang="ts">
    import { Link, useParams, useNavigate } from 'svelte-navigator';
    import { derived, writable, get } from 'svelte/store';
    import { onDestroy, onMount, tick } from 'svelte';
    import Phaser from 'phaser';

    import Header from '../components/Header.svelte';
    import Footer from '../components/Footer.svelte';
    import Thumbnail from '../components/Thumbnail.svelte';
    import { floors, loadRooms, busyCounter, localPreferences, loadTopics, loadItems, matchingFloors, matchingRooms } from '../store';
    import type { NestedStorage } from '../store/preferences';

    const navigate = useNavigate();
    const params = useParams();

    const MODE_MAP = 1;
    const MODE_LIST = 2;
    let mode = ($localPreferences.ui && ($localPreferences.ui as NestedStorage).floorDisplayMode) ? ($localPreferences.ui as NestedStorage).floorDisplayMode : MODE_MAP;
    let floorListElement = null as HTMLElement;
    let hoverRoomTimeout = 0;
    const hoverRoom = writable(null as JsonApiObject | null);
    const samples = writable([] as JsonApiObject[]);
    const mousePosition = {x: -1, y: -1};

    type MapObject = {
        position: { x: number, y: number, width: number, height: number },
        rect: Phaser.GameObjects.Rectangle,
        text: Phaser.GameObjects.Text,
    };

    class FloorScene extends Phaser.Scene {
        floor: JsonApiObject;
        roomObjects: MapObject[];
        baseMap: Phaser.GameObjects.Image;
        zoom: number;
        cameraPosition: { x: number, y: number };

        constructor(floor: JsonApiObject) {
            super('floor-' + floor.id);
            this.floor = floor;
        }

        preload() {
            this.load.svg('basemap', '/images/basemap.svg');
        }

        create() {
            this.roomObjects = [];
            this.zoom = 1;
            this.baseMap = this.add.image(0, 0, 'basemap');
            this.baseMap.setOrigin(0, 0);
            loadRooms((this.floor.relationships.rooms.data as JsonApiObjectReference[]).map((ref) => { return ref.id; })).then((rooms) => {
                busyCounter.start();
                $matchingRooms = get(matchingRooms);
                for (let room of rooms) {
                    const rect = this.add.rectangle(room.attributes.position.x,
                                                    room.attributes.position.y,
                                                    room.attributes.position.width,
                                                    room.attributes.position.height,
                                                    $matchingRooms.indexOf(room.id) >= 0 ? 0x2563eb : 0xffffff);
                    rect.setOrigin(0,0);
                    rect.setData('room', room);
                    rect.setData('room_id', room.id);
                    rect.setInteractive({useHandCursor: true});
                    rect.addListener('pointerover', () => {
                        window.clearTimeout(hoverRoomTimeout);
                        hoverRoomTimeout = window.setTimeout(() => {
                            loadItems([(room.relationships.sample.data as JsonApiObjectReference).id]).then((items) => {
                                hoverRoom.set(room);
                                samples.set(items);
                            });
                        }, 500);
                    });
                    rect.addListener('pointerout', () => {
                        window.clearTimeout(hoverRoomTimeout);
                        hoverRoom.set(null);
                        samples.set([]);
                    });

                    const text = this.add.text(room.attributes.position.x + room.attributes.position.width / 2,
                                               room.attributes.position.y + room.attributes.position.height / 2,
                                               room.attributes.label.replace(' - ', '\n'),
                                               {
                                                   color: $matchingRooms.indexOf(room.id) >= 0 ? '#ffffff' : '#000000',
                                                   fontFamily: 'ui-serif, Georgia, Cambria, "Times New Roman", Times, serif',
                                                   align: 'center',
                                               });
                    text.setOrigin(0.5, 0.5);

                    this.roomObjects.push({
                        position: room.attributes.position,
                        rect: rect,
                        text: text,
                    });
                }
                this.scaleObjects(false, false);
                busyCounter.stop();
            });

            this.cameraPosition = {
                x: -this.game.canvas.width / 2 + this.baseMap.width / 2,
                y: -this.game.canvas.height / 2 + this.baseMap.height / 2
            };
            this.zoom = Math.min(this.game.canvas.width / this.baseMap.width * 0.9, this.game.canvas.height / this.baseMap.height * 0.9);
            this.scaleObjects(true, true);

            let pointerX = 0;
            let pointerY = 0;
            let baseZoom = 0;
            let mousePointerDown = false;
            let pointer1Down = false;
            let pointer2Down = false;
            let pointerDownStart = 0;

            this.input.on('pointerdown', (pointer: Phaser.Input.Pointer, objectsClicked: Phaser.GameObjects.GameObject[]) => {
                pointerX = pointer.x;
                pointerY = pointer.y;
                mousePointerDown = mousePointerDown || pointer === this.input.mousePointer;
                pointer1Down = pointer1Down || pointer === this.input.pointer1;
                pointer2Down = pointer2Down || pointer === this.input.pointer2;
                baseZoom = this.zoom;
                pointerDownStart = (new Date()).getTime();
            });
            this.input.on('pointermove', (pointer: Phaser.Input.Pointer, objectsClicked: Phaser.GameObjects.GameObject[]) => {
                if ((mousePointerDown || pointer1Down) && !pointer2Down) {
                    // Drag the map around
                    if (Math.sqrt(Math.pow(pointer.downX - pointer.upX, 2) + Math.pow(pointer.downY - pointer.upY, 2)) >= 5) {
                        this.cameraPosition.x = this.cameraPosition.x + pointerX - pointer.x;
                        this.cameraPosition.y = this.cameraPosition.y + pointerY - pointer.y;
                        this.scaleObjects(false, false);
                        pointerX = pointer.x;
                        pointerY = pointer.y;
                    }
                } else if (pointer1Down && pointer2Down) {
                    // Zoom with two fingers
                    const startDelta = (Math.sqrt(Math.pow(this.input.pointer1.downX - this.input.pointer2.downX, 2) + Math.pow(this.input.pointer1.downY - this.input.pointer2.downY, 2)));
                    const endDelta = (Math.sqrt(Math.pow(this.input.pointer1.x - this.input.pointer2.x, 2) + Math.pow(this.input.pointer1.y - this.input.pointer2.y, 2)));
                    const steps = (endDelta - startDelta) / 20;
                    if (steps > 0) {
                        this.zoom = Math.min(baseZoom + 0.1 * steps, 4);
                    } else {
                        this.zoom = Math.max(baseZoom - 0.1 * Math.abs(steps), 0.5);
                    }
                    const baseWidth = this.baseMap.displayWidth;
                    const baseHeight = this.baseMap.displayHeight;
                    this.baseMap.setScale(this.zoom);
                    const newWidth = this.baseMap.displayWidth;
                    const newHeight = this.baseMap.displayHeight;
                    const centerX = this.input.pointer1.x + (this.input.pointer2.x - this.input.pointer1.x) / 2;
                    const centerY = this.input.pointer1.y + (this.input.pointer2.y - this.input.pointer1.y) / 2;
                    this.cameraPosition.x = this.cameraPosition.x + (newWidth - baseWidth) * ((centerX + this.cameraPosition.x) / this.baseMap.displayWidth);
                    this.cameraPosition.y = this.cameraPosition.y + (newHeight - baseHeight) * ((centerY + this.cameraPosition.y) / this.baseMap.displayHeight);
                    this.scaleObjects(false, false);
                }
            });
            this.input.on('pointerup', (pointer: Phaser.Input.Pointer, objectsClicked: Phaser.GameObjects.GameObject[]) => {
                if ((mousePointerDown || pointer1Down) && !pointer2Down) {
                    if (Math.sqrt(Math.pow(pointer.downX - pointer.upX, 2) + Math.pow(pointer.downY - pointer.upY, 2)) < 5) {
                        if (objectsClicked.length > 0) {
                            const pointerDownEnd = (new Date()).getTime();
                            if (pointerDownEnd - pointerDownStart > 500) {
                                tick().then(() => {
                                    const room = objectsClicked[0].getData('room');
                                    hoverRoom.set(room);
                                    loadItems([(room.relationships.sample.data as JsonApiObjectReference).id]).then((items) => {
                                        hoverRoom.set(room);
                                        samples.set(items);
                                    });
                                })
                            } else {
                                navigate('/room/' + objectsClicked[0].getData('room_id'));
                            }
                        }
                    }
                }
                mousePointerDown = false;
                pointer1Down = false;
                pointer2Down = false;
            });
            this.input.on('wheel', (pointer, gameObjects, deltaX, deltaY, deltaZ) => {
                if (deltaY > 0) {
                    this.zoom = Math.max(this.zoom - 0.1, 0.5);
                } else if (deltaY < 0) {
                    this.zoom = Math.min(this.zoom + 0.1, 4);
                }
                const baseWidth = this.baseMap.displayWidth;
                const baseHeight = this.baseMap.displayHeight;
                this.baseMap.setScale(this.zoom);
                const newWidth = this.baseMap.displayWidth;
                const newHeight = this.baseMap.displayHeight;
                this.cameraPosition.x = this.cameraPosition.x + (newWidth - baseWidth) * ((pointer.x + this.cameraPosition.x) / this.baseMap.displayWidth);
                this.cameraPosition.y = this.cameraPosition.y + (newHeight - baseHeight) * ((pointer.y + this.cameraPosition.y) / this.baseMap.displayHeight);
                this.scaleObjects(false, false);
            });

            this.scale.on('resize', () => {
                this.zoom = Math.min(this.game.canvas.width / this.baseMap.width * 0.9, this.game.canvas.height / this.baseMap.height * 0.9);
                this.scaleObjects(true, false);
            });
        }

        scaleObjects(center: boolean, force: boolean) {
            if (this.game.scene.isActive('floor-' + this.floor.id) || force) {
                this.baseMap.setScale(this.zoom);
                if (center) {
                    this.cameraPosition = {
                        x: -this.game.canvas.width / 2 + this.baseMap.displayWidth / 2,
                        y: -this.game.canvas.height / 2 + this.baseMap.displayHeight / 2
                    };
                }
                if (this.cameras && this.cameras.main) {
                    this.cameras.main.setScroll(this.cameraPosition.x, this.cameraPosition.y);
                }
                for (const obj of this.roomObjects) {
                    obj.rect.x = obj.position.x * this.zoom;
                    obj.rect.y = obj.position.y * this.zoom;
                    obj.rect.width = obj.position.width * this.zoom;
                    obj.rect.height = obj.position.height * this.zoom;
                    obj.rect.input.hitArea.setTo(0, 0, obj.position.width * this.zoom, obj.position.height * this.zoom);
                    obj.text.x = obj.rect.x + obj.rect.width / 2;
                    obj.text.y = obj.rect.y + obj.rect.height / 2;
                    obj.text.setFontSize(this.zoom > 1 ? 16 : 13);
                    let fontSize = this.zoom > 1 ? 15 : 12;
                    if (obj.position.height > obj.position.width) {
                        obj.text.setRotation(1.5708);
                        while (obj.text.width > obj.rect.height - 4 && fontSize >= 4) {
                            obj.text.setFontSize(fontSize);
                            fontSize = fontSize - 1;
                        }
                    } else {
                        while (obj.text.width > obj.rect.width - 4 && fontSize >= 4) {
                            obj.text.setFontSize(fontSize);
                            fontSize = fontSize - 1;
                        }
                    }
                }
            }
        }
    }

    let sceneConfig = {
        type: Phaser.AUTO,
        parent: 'game',
        transparent: true,
        scale: {
            width: 200,
            height: 300,
            mode: Phaser.Scale.RESIZE,
            autoCenter: Phaser.Scale.CENTER_BOTH
        },
        input: {
            activePointers: 3
        }
    }

    let game = null as Phaser.Game;

    const currentFloor = derived([params, floors], ([params, floors]) => {
        const floor = floors.filter((floor) => {
            return floor.id === params.id;
        });
        hoverRoom.set(null);
        samples.set([]);
        if (floor.length > 0) {
            return floor[0];
        }
        return null;
    }, null);

    const previousFloor = derived([currentFloor, floors], ([currentFloor, floors]) => {
        if (currentFloor) {
            let previousFloor = null;
            for (const floor of floors) {
                if (floor === currentFloor) {
                    return previousFloor;
                }
                previousFloor = floor;
            }
        } else {
            return null;
        }
    });

    const nextFloor = derived([currentFloor, floors], ([currentFloor, floors]) => {
        if (currentFloor) {
            let found = false;
            for (const floor of floors) {
                if (found) {
                    return floor;
                }
                if (floor === currentFloor) {
                    found = true;
                }
            }
            return null;
        } else {
            return null;
        }
    });

    const currentFloorUnsubscribe = currentFloor.subscribe((currentFloor) => {
        if (currentFloor && game) {
            if (!game.scene.getScene('floor-' + currentFloor.id)) {
                game.scene.add('floor-' + currentFloor.id, new FloorScene(currentFloor));
            }
            let currentActive = false;
            for (const scene of game.scene.getScenes()) {
                if (game.scene.isActive(scene)) {
                    if ((scene as FloorScene).floor.id === currentFloor.id) {
                        currentActive = true;
                    } else {
                        game.scene.stop(scene);
                    }
                }
            }
            if (!currentActive) {
                game.scene.start('floor-' + currentFloor.id);
            }
            if (floorListElement) {
                tick().then(() => {
                    const currentElement = floorListElement.querySelector('.current-floor') as HTMLElement;
                    if (currentElement) {
                        currentElement.scrollIntoView();
                    }
                })
            }
        }
    });

    const matchingRoomsUnsubscribe = matchingRooms.subscribe((matchingRooms) => {
        if (game) {
            for (const scene of game.scene.getScenes()) {
                for (const obj of (scene as FloorScene).roomObjects) {
                    if (matchingRooms.indexOf(obj.rect.getData('room_id')) >= 0) {
                        obj.rect.fillColor = 0x2563eb;
                        obj.text.setColor('#ffffff');
                    } else {
                        obj.rect.fillColor = 0xffffff;
                        obj.text.setColor('#000000');
                    }
                }
            }
        }
    });

    const rooms = derived(currentFloor, (currentFloor, set) => {
        if (currentFloor) {
            loadRooms((currentFloor.relationships.rooms.data as JsonApiObjectReference[]).map((ref) => { return ref.id; })).then((rooms) => {
                set(rooms);
            })
        } else {
            set([]);
        }
    }, [] as JsonApiObject[]);

    const topics = derived(floors, (floors, set) => {
        if (floors) {
            let topicIds = [] as string[];
            for(const floor of floors) {
                topicIds = topicIds.concat((floor.relationships.topics.data as JsonApiObjectReference[]).map((rel) => { return rel.id; }));
            }
            loadTopics(topicIds).then((topics) => {
                const topicsMap = {} as {[x: string]: JsonApiObject[]};
                for(const floor of floors) {
                    topicIds = (floor.relationships.topics.data as JsonApiObjectReference[]).map((rel) => { return rel.id; });
                    topicsMap[floor.id] = topics.filter((topic) => { return topicIds.indexOf(topic.id) >= 0 });
                }
                set(topicsMap);
                if (floorListElement) {
                    tick().then(() => {
                        const currentElement = floorListElement.querySelector('.current-floor') as HTMLElement;
                        if (currentElement) {
                            currentElement.scrollIntoView();
                        }
                    })
                }
            });
        }
    }, {} as {[x: string]: JsonApiObject[]});

    const searchedFloors = derived([floors, matchingFloors], ([floors, matchingFloors]) => {
        return floors.map((floor: JsonApiObject) => {
            return [floor, matchingFloors.indexOf(floor.id) >= 0];
        });
    }, [] as [JsonApiObject, boolean][]);

    onMount(() => {
        document.body.addEventListener('mousemove', (ev: MouseEvent) => {
            mousePosition.x = ev.pageX;
            mousePosition.y = ev.pageY;
        });
        game = new Phaser.Game(sceneConfig);
        if ($currentFloor) {
            if (!game.scene.getScene('floor-' + $currentFloor.id)) {
                game.scene.add('floor-' + $currentFloor.id, new FloorScene($currentFloor));
            }
            game.scene.start('floor-' + $currentFloor.id);
        }
    });

    onDestroy(() => {
        currentFloorUnsubscribe();
        matchingRoomsUnsubscribe();
    });

    async function changeMode(newMode: number) {
        mode = newMode;
        localPreferences.setPreference('ui.floorDisplayMode', mode);
        if (mode === MODE_MAP) {
            await tick();
        }
    }
</script>

<div class="flex flex-col h-screen">
    <Header title="{$currentFloor ? $currentFloor.attributes.label : 'Loading...'}" nav={[{label: $currentFloor ? $currentFloor.attributes.label : 'Loading...', path: '/floor/' + ($currentFloor ? $currentFloor.id : '0')}]}/>
    <div class="lg:hidden flex-none flex flex-row">
        <div class="flex-none ml-2 lg:ml-4 mt-2 lg:mt-4">
            {#if $previousFloor}
                <Link to="/floor/{$previousFloor.id}" class="inline-block bg-neutral-600 px-4 py-3 lg:py-2 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800">⇧ {$previousFloor.attributes.label}</Link>
            {:else}
                <span class="inline-block px-4 py-3 lg:py-2 rounded-lg">&nbsp;</span>
            {/if}
        </div>
        <div class="flex-1"></div>
        <div class="flex-none mr-2 lg:mr-4 mt-2 lg:mt-4">
            <button on:click={() => { changeMode(MODE_MAP); }} class="inline-block bg-neutral-600 px-3 py-3 lg:py-3 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800 {mode === MODE_MAP ? 'bg-blue-800' : ''}">
                <svg class="w-6 h-6" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M15,19L9,16.89V5L15,7.11M20.5,3C20.44,3 20.39,3 20.34,3L15,5.1L9,3L3.36,4.9C3.15,4.97 3,5.15 3,5.38V20.5A0.5,0.5 0 0,0 3.5,21C3.55,21 3.61,21 3.66,20.97L9,18.9L15,21L20.64,19.1C20.85,19 21,18.85 21,18.62V3.5A0.5,0.5 0 0,0 20.5,3Z" />
                </svg>
            </button>
        </div>
        <div class="flex-none mr-2 lg:mr-4 mt-2 lg:mt-4">
            <button on:click={() => { changeMode(MODE_LIST); }} class="inline-block bg-neutral-600 px-3 py-3 lg:py-3 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800 {mode === MODE_LIST ? 'bg-blue-800' : ''}">
                <svg class="w-6 h-6" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M7,5H21V7H7V5M7,13V11H21V13H7M4,4.5A1.5,1.5 0 0,1 5.5,6A1.5,1.5 0 0,1 4,7.5A1.5,1.5 0 0,1 2.5,6A1.5,1.5 0 0,1 4,4.5M4,10.5A1.5,1.5 0 0,1 5.5,12A1.5,1.5 0 0,1 4,13.5A1.5,1.5 0 0,1 2.5,12A1.5,1.5 0 0,1 4,10.5M7,19V17H21V19H7M4,16.5A1.5,1.5 0 0,1 5.5,18A1.5,1.5 0 0,1 4,19.5A1.5,1.5 0 0,1 2.5,18A1.5,1.5 0 0,1 4,16.5Z" />
                </svg>
            </button>
        </div>
    </div>
    <div class="flex flex-row flex-1 overflow-hidden">
        <nav class="hidden lg:block overflow-auto w-[20%]">
            <ol bind:this={floorListElement} class="p-4 w-full">
                {#each $searchedFloors as [floor, matches]}
                    <li class="border-r-2 {matches ? 'border-r-blue-600' : 'border-r-neutral-700'}">
                        <Link to="/floor/{floor.id}" class="mb-4 block group hover:underline {floor.id === $currentFloor.id ? 'current-floor' : ''}">
                            <span class="inline-block {floor.id === $currentFloor.id ? 'bg-blue-600' : 'bg-neutral-600'} px-4 lg:px-3 py-3 lg:py-1 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800 lg:group-hover:bg-blue-800 lg:group-focus:bg-blue-800">⇒ {floor.attributes.label}</span>
                            <span class="flex flex-row flex-wrap text-sm pl-4 pt-2">
                                {#if $topics[floor.id]}
                                    {#each $topics[floor.id] as topic}
                                        <span class="after:content-[','] after:mr-1 last:after:hidden">{topic.attributes.label}</span>
                                    {/each}
                                {/if}
                            </span>
                        </Link>
                    </li>
                {/each}
            </ol>
        </nav>
        <article class="flex-1 overflow-hidden relative">
            <nav class="hidden lg:flex flex-row absolute right-0 top-0">
                <div class="flex-none mr-2 lg:mr-4 mt-2 lg:mt-4">
                    <button on:click={() => { changeMode(MODE_MAP); }} class="inline-block bg-neutral-600 px-3 py-3 lg:py-3 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800 {mode === MODE_MAP ? 'bg-blue-800' : ''}">
                        <svg class="w-6 h-6" viewBox="0 0 24 24">
                            <path fill="currentColor" d="M15,19L9,16.89V5L15,7.11M20.5,3C20.44,3 20.39,3 20.34,3L15,5.1L9,3L3.36,4.9C3.15,4.97 3,5.15 3,5.38V20.5A0.5,0.5 0 0,0 3.5,21C3.55,21 3.61,21 3.66,20.97L9,18.9L15,21L20.64,19.1C20.85,19 21,18.85 21,18.62V3.5A0.5,0.5 0 0,0 20.5,3Z" />
                        </svg>
                    </button>
                </div>
                <div class="flex-none mr-2 lg:mr-4 mt-2 lg:mt-4">
                    <button on:click={() => { changeMode(MODE_LIST); }} class="inline-block bg-neutral-600 px-3 py-3 lg:py-3 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800 {mode === MODE_LIST ? 'bg-blue-800' : ''}">
                        <svg class="w-6 h-6" viewBox="0 0 24 24">
                            <path fill="currentColor" d="M7,5H21V7H7V5M7,13V11H21V13H7M4,4.5A1.5,1.5 0 0,1 5.5,6A1.5,1.5 0 0,1 4,7.5A1.5,1.5 0 0,1 2.5,6A1.5,1.5 0 0,1 4,4.5M4,10.5A1.5,1.5 0 0,1 5.5,12A1.5,1.5 0 0,1 4,13.5A1.5,1.5 0 0,1 2.5,12A1.5,1.5 0 0,1 4,10.5M7,19V17H21V19H7M4,16.5A1.5,1.5 0 0,1 5.5,18A1.5,1.5 0 0,1 4,19.5A1.5,1.5 0 0,1 2.5,18A1.5,1.5 0 0,1 4,16.5Z" />
                        </svg>
                    </button>
                </div>
            </nav>
            <div id="game" class="w-full h-full {mode === MODE_MAP ? '' : 'hidden'}" aria-hidden="true"></div>
            {#if $hoverRoom && $samples.length > 0}
                <div class="hidden lg:fixed lg:flex flex-col z-50 shadow-lg w-[150px] h-[150px] overflow-hidden bg-neutral-600" style="left: {mousePosition.x + 5}px; top: {mousePosition.y + 5}px;">
                    <h3 class="truncate block px-2 py-1 hover:underline focus:underline bg-blue-800 text-white">{$hoverRoom.attributes.label}</h3>
                    <ul class="flex-1 flex flex-col overflow-hidden px-2 py-2">
                        {#each $samples as sample}
                            <li class="flex-1 overflow-hidden"><Thumbnail item={sample} noTitle={true}/></li>
                        {/each}
                    </ul>
                </div>
                <div class="fixed lg:hidden bottom-0 left-0 flex flex-col z-50 shadow-lg w-screen h-[150px] overflow-hidden bg-neutral-600">
                    <h3 class="flex flex-row px-2 py-1 bg-blue-800 text-white">
                        <Link to="/room/{$hoverRoom.id}" class="flex-1 truncate block hover:underline focus:underline">{$hoverRoom.attributes.label}</Link>
                        <button on:click={() => { hoverRoom.set(null); samples.set([]); }} aria-label="Close">
                            <svg viewBox="0 0 24 24" class="w-6 h-6">
                                <path fill="currentColor" d="M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2C6.47,2 2,6.47 2,12C2,17.53 6.47,22 12,22C17.53,22 22,17.53 22,12C22,6.47 17.53,2 12,2M14.59,8L12,10.59L9.41,8L8,9.41L10.59,12L8,14.59L9.41,16L12,13.41L14.59,16L16,14.59L13.41,12L16,9.41L14.59,8Z" />
                            </svg>
                        </button>
                    </h3>
                    <ul class="flex-1 flex flex-col overflow-hidden px-2 py-2">
                        {#each $samples as sample}
                            <li class="flex-1 overflow-hidden"><Thumbnail item={sample} noTitle={true}/></li>
                        {/each}
                    </ul>
                </div>
            {/if}
            <div class="{mode === MODE_LIST ? '' : 'hidden'}">
                <ol class="px-4 pb-6 pt-2 columns-sm">
                    {#each $rooms as room}
                        <li><Link to="/room/{room.id}" class="block py-2 hover:underline focus:underline">{room.attributes.label}</Link></li>
                    {/each}
                </ol>
            </div>
        </article>
    </div>
    <div class="flex-none lg:hidden">
        {#if $nextFloor}
            <Link to="/floor/{$nextFloor.id}" class="inline-block bg-neutral-600 px-4 py-3 lg:py-2 ml-2 lg:ml-4 mb-2 lg:mb-4 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800">⇩ {$nextFloor.attributes.label}</Link>
        {:else}
            <span class="inline-block px-4 py-3 lg:py-2 ml-2 lg:ml-4 mb-2 lg:mb-4 rounded-lg">&nbsp;</span>
        {/if}
    </div>
    <Footer/>
</div>
