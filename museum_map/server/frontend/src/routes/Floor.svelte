<script lang="ts">
  import { derived, writable, get } from "svelte/store";
  import { onDestroy, onMount, tick } from "svelte";
  import Phaser from "phaser";
  import { location } from "../simple-svelte-router";
  import { createQuery } from "@tanstack/svelte-query";

  import Header from "../components/Header.svelte";
  import Footer from "../components/Footer.svelte";
  import Thumbnail from "../components/Thumbnail.svelte";
  import Loading from "../components/Loading.svelte";
  import { localPreferences, track, searchTerm } from "../store";
  import type { NestedStorage } from "../store/preferences";
  import { apiRequest } from "../util";

  const MODE_MAP = 1;
  const MODE_LIST = 2;
  let mode =
    $localPreferences.ui &&
    ($localPreferences.ui as NestedStorage).floorDisplayMode
      ? ($localPreferences.ui as NestedStorage).floorDisplayMode
      : MODE_MAP;
  let floorListElement: HTMLElement | null = null;
  let hoverRoomTimeout = 0;
  const hoverRoom = writable(null as Room | null);
  const mousePosition = { x: -1, y: -1 };

  const floors = createQuery({
    queryKey: ["/floors/"],
    queryFn: apiRequest<Floor[]>,
  });

  const currentFloor = derived([floors, location], ([floors, location]) => {
    if (location.pathComponents.fid && floors.isSuccess) {
      for (const floor of floors.data) {
        if (floor.id === Number.parseInt(location.pathComponents.fid)) {
          return floor;
        }
      }
    }
    return null;
  });

  const previousFloor = derived(
    [currentFloor, floors],
    ([currentFloor, floors]) => {
      if (currentFloor && floors.isSuccess) {
        let previousFloor = null;
        for (const floor of floors.data) {
          if (floor === currentFloor) {
            return previousFloor;
          }
          previousFloor = floor;
        }
      } else {
        return null;
      }
    },
  );

  const nextFloor = derived(
    [currentFloor, floors],
    ([currentFloor, floors]) => {
      if (currentFloor && floors.isSuccess) {
        let found = false;
        for (const floor of floors.data) {
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
    },
  );

  const floorTopics = createQuery({
    queryKey: ["/floor-topics/"],
    queryFn: apiRequest<FloorTopic[]>,
  });

  // The floor topics as a floor.id -> topic dictionary
  const topicsDict = derived(
    floorTopics,
    (floorTopics) => {
      if (floorTopics.isSuccess) {
        tick().then(() => {
          if (floorListElement) {
            const currentElement = floorListElement.querySelector(
              ".current-floor",
            ) as HTMLElement;
            if (currentElement) {
              currentElement.scrollIntoView();
            }
          }
        });

        const topicsDict: { [x: number]: FloorTopic[] } = {};
        for (let floorTopic of floorTopics.data) {
          if (topicsDict[floorTopic.floor]) {
            topicsDict[floorTopic.floor].push(floorTopic);
          } else {
            topicsDict[floorTopic.floor] = [floorTopic];
          }
        }
        return topicsDict;
      }
      return {};
    },
    {},
  );

  const roomsQueryOptions = derived(location, (location) => {
    return {
      queryKey: [
        "/floors/",
        Number.parseInt(location.pathComponents.fid),
        "/rooms",
      ],
      queryFn: apiRequest<Room[]>,
    };
  });
  const rooms = createQuery(roomsQueryOptions);

  const samplesQueryOptions = derived(hoverRoom, (hoverRoom) => {
    if (hoverRoom) {
      return {
        queryKey: ["/items/" + hoverRoom.sample],
        queryFn: apiRequest<Item>,
      };
    } else {
      return {
        queryKey: ["/items/-1"],
        queryFn: apiRequest<Item>,
        enabled: false,
      };
    }
  });
  const samples = createQuery(samplesQueryOptions);

  const searchQueryOptions = derived(searchTerm, (searchTerm) => {
    return {
      queryKey: ["/api/search", searchTerm],
      queryFn: async () => {
        if (searchTerm.trim() !== "") {
          const response = await window.fetch("/api/search/?q=" + searchTerm);
          if (response.ok) {
            return await response.json();
          } else {
            throw new Error("Could not fetch search results");
          }
        } else {
          return { floors: [], rooms: [] };
        }
      },
    };
  });
  const searchResultsQuery = createQuery(searchQueryOptions);

  class FloorScene extends Phaser.Scene {
    floorId: number;
    rooms: Room[];
    roomObjects: MapObject[] = [];
    baseMap!: Phaser.GameObjects.Image;
    zoom!: number;
    cameraPosition!: { x: number; y: number };

    constructor(floorId: number, rooms: Room[]) {
      super("floor-" + floorId);
      this.floorId = floorId;
      this.rooms = rooms;
    }

    preload() {
      this.load.svg("basemap", "/images/basemap.svg");
    }

    create() {
      this.roomObjects = [];
      this.zoom = 1;
      this.baseMap = this.add.image(0, 0, "basemap");
      this.baseMap.setOrigin(0, 0);
      this.baseMap.setAlpha(1);

      this.cameraPosition = {
        x: -this.game.canvas.width / 2 + this.baseMap.width / 2,
        y: -this.game.canvas.height / 2 + this.baseMap.height / 2,
      };
      this.zoom = Math.min(
        (this.game.canvas.width / this.baseMap.width) * 0.9,
        (this.game.canvas.height / this.baseMap.height) * 0.9,
      );
      for (let room of this.rooms) {
        const rect = this.add.rectangle(
          room.position.x,
          room.position.y,
          room.position.width,
          room.position.height,
          $searchResultsQuery.isSuccess &&
            $searchResultsQuery.data.rooms.indexOf(room.id) >= 0
            ? 0x2563eb
            : 0xffffff,
        );
        rect.setOrigin(0, 0);
        rect.setData("room", room);
        rect.setData("room_id", room.id);
        rect.setInteractive({ useHandCursor: true });
        rect.addListener("pointerover", () => {
          window.clearTimeout(hoverRoomTimeout);
          hoverRoomTimeout = window.setTimeout(() => {
            track({
              action: "show-samples",
              params: { object: "room", room: room.id },
            });
            hoverRoom.set(room);
          }, 500);
          track({
            action: "mousenter",
            params: { object: "room", room: room.id },
          });
        });
        rect.addListener("pointerout", () => {
          window.clearTimeout(hoverRoomTimeout);
          hoverRoom.set(null);
          track({
            action: "mouseleave",
            params: { object: "room", room: room.id },
          });
        });

        const text = this.add.text(
          room.position.x + room.position.width / 2,
          room.position.y + room.position.height / 2,
          room.label.replace(" - ", "\n"),
          {
            color:
              $searchResultsQuery.isSuccess &&
              $searchResultsQuery.data.rooms.indexOf(room.id) >= 0
                ? "#ffffff"
                : "#000000",
            fontFamily:
              'ui-serif, Georgia, Cambria, "Times New Roman", Times, serif',
            align: "center",
          },
        );
        text.setOrigin(0.5, 0.5);

        this.roomObjects.push({
          position: room.position,
          rect: rect,
          text: text,
        });
      }
      this.scaleObjects(true, true);

      let pointerX = 0;
      let pointerY = 0;
      let baseZoom = 0;
      let mousePointerDown = false;
      let pointer1Down = false;
      let pointer2Down = false;
      let pointerDownStart = 0;

      this.input.on(
        "pointerdown",
        (
          pointer: Phaser.Input.Pointer,
          objectsClicked: Phaser.GameObjects.GameObject[],
        ) => {
          pointerX = pointer.x;
          pointerY = pointer.y;
          mousePointerDown =
            mousePointerDown || pointer === this.input.mousePointer;
          pointer1Down = pointer1Down || pointer === this.input.pointer1;
          pointer2Down = pointer2Down || pointer === this.input.pointer2;
          baseZoom = this.zoom;
          pointerDownStart = new Date().getTime();
        },
      );
      this.input.on(
        "pointermove",
        (
          pointer: Phaser.Input.Pointer,
          objectsClicked: Phaser.GameObjects.GameObject[],
        ) => {
          if ((mousePointerDown || pointer1Down) && !pointer2Down) {
            // Drag the map around
            if (
              Math.sqrt(
                Math.pow(pointer.downX - pointer.upX, 2) +
                  Math.pow(pointer.downY - pointer.upY, 2),
              ) >= 5
            ) {
              this.cameraPosition.x =
                this.cameraPosition.x + pointerX - pointer.x;
              this.cameraPosition.y =
                this.cameraPosition.y + pointerY - pointer.y;
              this.scaleObjects(false, false);
              pointerX = pointer.x;
              pointerY = pointer.y;
            }
            track({
              action: "drag-map",
              params: { x: this.cameraPosition.x, y: this.cameraPosition.y },
            });
          } else if (pointer1Down && pointer2Down) {
            // Zoom with two fingers
            const startDelta = Math.sqrt(
              Math.pow(
                this.input.pointer1.downX - this.input.pointer2.downX,
                2,
              ) +
                Math.pow(
                  this.input.pointer1.downY - this.input.pointer2.downY,
                  2,
                ),
            );
            const endDelta = Math.sqrt(
              Math.pow(this.input.pointer1.x - this.input.pointer2.x, 2) +
                Math.pow(this.input.pointer1.y - this.input.pointer2.y, 2),
            );
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
            const centerX =
              this.input.pointer1.x +
              (this.input.pointer2.x - this.input.pointer1.x) / 2;
            const centerY =
              this.input.pointer1.y +
              (this.input.pointer2.y - this.input.pointer1.y) / 2;
            this.cameraPosition.x =
              this.cameraPosition.x +
              (newWidth - baseWidth) *
                ((centerX + this.cameraPosition.x) / this.baseMap.displayWidth);
            this.cameraPosition.y =
              this.cameraPosition.y +
              (newHeight - baseHeight) *
                ((centerY + this.cameraPosition.y) /
                  this.baseMap.displayHeight);
            this.scaleObjects(false, false);
            track({
              action: "zoom-map",
              params: { zoom: this.zoom },
            });
          }
        },
      );
      // Finish dragging
      this.input.on(
        "pointerup",
        (
          pointer: Phaser.Input.Pointer,
          objectsClicked: Phaser.GameObjects.GameObject[],
        ) => {
          if ((mousePointerDown || pointer1Down) && !pointer2Down) {
            if (
              Math.sqrt(
                Math.pow(pointer.downX - pointer.upX, 2) +
                  Math.pow(pointer.downY - pointer.upY, 2),
              ) < 5
            ) {
              if (objectsClicked.length > 0) {
                const pointerDownEnd = new Date().getTime();
                if (pointerDownEnd - pointerDownStart > 500) {
                  // TODO: Need to re-enable hovering on touch devices
                  /*tick().then(() => {
                    const room = objectsClicked[0].getData("room");
                    hoverRoom.set(room);
                    fetchItems([room.sample]).then((items) => {
                      hoverRoom.set(room);
                      samples.set(items);
                    });
                  });*/
                } else {
                  location.push(
                    "/floor/" +
                      $currentFloor?.id +
                      "/room/" +
                      objectsClicked[0].getData("room_id"),
                  );
                }
              }
            }
          }
          mousePointerDown = false;
          pointer1Down = false;
          pointer2Down = false;
        },
      );
      // Zoom the map
      this.input.on(
        "wheel",
        (
          pointer,
          gameObjects,
          deltaX: number,
          deltaY: number,
          deltaZ: number,
        ) => {
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
          this.cameraPosition.x =
            this.cameraPosition.x +
            (newWidth - baseWidth) *
              ((pointer.x + this.cameraPosition.x) / this.baseMap.displayWidth);
          this.cameraPosition.y =
            this.cameraPosition.y +
            (newHeight - baseHeight) *
              ((pointer.y + this.cameraPosition.y) /
                this.baseMap.displayHeight);
          this.scaleObjects(false, false);
          track({
            action: "zoom-map",
            params: { zoom: this.zoom },
          });
        },
      );

      // Handle re-scaling of the map
      this.scale.on("resize", () => {
        this.zoom = Math.min(
          (this.game.canvas.width / this.baseMap.width) * 0.9,
          (this.game.canvas.height / this.baseMap.height) * 0.9,
        );
        this.scaleObjects(true, false);
        track({
          action: "resize-map",
          params: {
            zoom: this.zoom,
            width: this.baseMap.displayWidth,
            height: this.baseMap.displayHeight,
          },
        });
      });

      // Log the map floor setup
      track({
        action: "initial-size-map",
        params: {
          zoom: this.zoom,
          width: this.baseMap.displayWidth,
          height: this.baseMap.displayHeight,
        },
      });
    }

    scaleObjects(center: boolean, force: boolean) {
      if (this.game.scene.isActive("floor-" + this.floorId) || force) {
        this.baseMap.setScale(this.zoom);
        if (center) {
          this.cameraPosition = {
            x: -this.game.canvas.width / 2 + this.baseMap.displayWidth / 2,
            y: -this.game.canvas.height / 2 + this.baseMap.displayHeight / 2,
          };
        }
        if (this.cameras && this.cameras.main) {
          this.cameras.main.setScroll(
            this.cameraPosition.x,
            this.cameraPosition.y,
          );
        }
        for (const obj of this.roomObjects) {
          obj.rect.x = obj.position.x * this.zoom;
          obj.rect.y = obj.position.y * this.zoom;
          obj.rect.width = obj.position.width * this.zoom;
          obj.rect.height = obj.position.height * this.zoom;
          obj.rect.input?.hitArea.setTo(
            0,
            0,
            obj.position.width * this.zoom,
            obj.position.height * this.zoom,
          );
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
    parent: "game",
    transparent: true,
    scale: {
      width: 200,
      height: 300,
      mode: Phaser.Scale.RESIZE,
      autoCenter: Phaser.Scale.CENTER_BOTH,
    },
    input: {
      activePointers: 3,
    },
  };

  let game: Phaser.Game | null = null;

  const currentFloorUnsubscribe = currentFloor.subscribe((currentFloor) => {
    tick().then(() => {
      const currentElement = floorListElement?.querySelector(
        ".current-floor",
      ) as HTMLElement;
      if (currentElement) {
        currentElement.scrollIntoView();
      }
    });
  });

  const searchResultsQueryUnsubscribe = searchResultsQuery.subscribe(
    (searchResultsQuery) => {
      if (game && searchResultsQuery.isSuccess) {
        for (const scene of game.scene.getScenes()) {
          for (const obj of (scene as FloorScene).roomObjects) {
            if (
              searchResultsQuery.data.rooms.indexOf(
                obj.rect.getData("room_id"),
              ) >= 0
            ) {
              obj.rect.fillColor = 0x2563eb;
              obj.text.setColor("#ffffff");
            } else {
              obj.rect.fillColor = 0xffffff;
              obj.text.setColor("#000000");
            }
          }
        }
      }
    },
  );

  function loadFloorRooms() {
    if (game && $rooms.isSuccess) {
      for (const scene of game.scene.getScenes(true)) {
        game.scene.stop(scene);
      }
      if (!game.scene.getScene("floor-" + $location.pathComponents.fid)) {
        game.scene.add(
          "floor-" + $location.pathComponents.fid,
          new FloorScene(
            Number.parseInt($location.pathComponents.fid),
            $rooms.data,
          ),
        );
      }
      game.scene.start("floor-" + $location.pathComponents.fid);
    }
  }

  const roomsUnsubcribe = rooms.subscribe(() => {
    loadFloorRooms();
  });

  onMount(() => {
    document.body.addEventListener("mousemove", (ev: MouseEvent) => {
      mousePosition.x = ev.pageX;
      mousePosition.y = ev.pageY;
    });
    game = new Phaser.Game(sceneConfig);
    loadFloorRooms();
  });

  onDestroy(() => {
    roomsUnsubcribe();
    currentFloorUnsubscribe();
    searchResultsQueryUnsubscribe();
  });

  async function changeMode(newMode: number) {
    mode = newMode;
    localPreferences.setPreference("ui.floorDisplayMode", mode);
    if (mode === MODE_MAP) {
      await tick();
    }
    track({ action: "switch-map-mode", params: { mode: newMode } });
  }
</script>

<div class="flex flex-col h-screen">
  <Header
    title={$currentFloor ? $currentFloor.label : "Loading..."}
    nav={[
      {
        label: $currentFloor ? $currentFloor.label : "Loading...",
        path: "/floor/" + ($currentFloor ? $currentFloor.id : "0"),
      },
    ]}
  />
  <div class="lg:hidden flex-none flex flex-row">
    <div class="flex-none ml-2 lg:ml-4 mt-2 lg:mt-4">
      {#if $previousFloor}
        <a
          href="#/floor/{$previousFloor.id}"
          class="inline-block bg-neutral-600 px-4 py-3 lg:py-2 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800"
          on:mouseenter={() => {
            track({
              action: "mouseenter",
              params: { object: "previous-floor", floor: $previousFloor?.id },
            });
          }}
          on:mouseleave={() => {
            track({
              action: "mouseleave",
              params: { object: "previous-floor", floor: $previousFloor?.id },
            });
          }}
          on:focus={() => {
            track({
              action: "focus",
              params: { object: "previous-floor", floor: $previousFloor?.id },
            });
          }}
          on:blur={() => {
            track({
              action: "blur",
              params: { object: "previous-floor", floor: $previousFloor?.id },
            });
          }}>⇧ {$previousFloor.label}</a
        >
      {:else}
        <span class="inline-block px-4 py-3 lg:py-2 rounded-lg">&nbsp;</span>
      {/if}
    </div>
    <div class="flex-1" />
    <div class="flex-none mr-2 lg:mr-4 mt-2 lg:mt-4">
      <button
        on:click={() => {
          changeMode(MODE_MAP);
        }}
        class="inline-block bg-neutral-600 px-3 py-3 lg:py-3 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800 {mode ===
        MODE_MAP
          ? 'bg-blue-600'
          : ''}"
        aria-label="Explore the museum's map"
      >
        <svg class="w-6 h-6" viewBox="0 0 24 24" aria-hidden="true">
          <path
            fill="currentColor"
            d="M15,19L9,16.89V5L15,7.11M20.5,3C20.44,3 20.39,3 20.34,3L15,5.1L9,3L3.36,4.9C3.15,4.97 3,5.15 3,5.38V20.5A0.5,0.5 0 0,0 3.5,21C3.55,21 3.61,21 3.66,20.97L9,18.9L15,21L20.64,19.1C20.85,19 21,18.85 21,18.62V3.5A0.5,0.5 0 0,0 20.5,3Z"
          />
        </svg>
      </button>
    </div>
    <div class="flex-none mr-2 lg:mr-4 mt-2 lg:mt-4">
      <button
        on:click={() => {
          changeMode(MODE_LIST);
        }}
        class="inline-block bg-neutral-600 px-3 py-3 lg:py-3 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800 {mode ===
        MODE_LIST
          ? 'bg-blue-600'
          : ''}"
        aria-label="Explore the museum in text form"
      >
        <svg class="w-6 h-6" viewBox="0 0 24 24" aria-hidden="true">
          <path
            fill="currentColor"
            d="M7,5H21V7H7V5M7,13V11H21V13H7M4,4.5A1.5,1.5 0 0,1 5.5,6A1.5,1.5 0 0,1 4,7.5A1.5,1.5 0 0,1 2.5,6A1.5,1.5 0 0,1 4,4.5M4,10.5A1.5,1.5 0 0,1 5.5,12A1.5,1.5 0 0,1 4,13.5A1.5,1.5 0 0,1 2.5,12A1.5,1.5 0 0,1 4,10.5M7,19V17H21V19H7M4,16.5A1.5,1.5 0 0,1 5.5,18A1.5,1.5 0 0,1 4,19.5A1.5,1.5 0 0,1 2.5,18A1.5,1.5 0 0,1 4,16.5Z"
          />
        </svg>
      </button>
    </div>
  </div>
  <div class="flex flex-row flex-1 overflow-hidden">
    <nav class="hidden lg:block overflow-auto w-[20%]">
      {#if $floors.isSuccess && $floorTopics.isSuccess}
        <ol bind:this={floorListElement} class="p-4 w-full">
          {#each $floors.data as floor}
            <li
              class="border-r-2 {$searchResultsQuery.isSuccess &&
              $searchResultsQuery.data.floors.indexOf(floor.id) >= 0
                ? 'border-r-blue-600'
                : 'border-r-neutral-700'}"
            >
              <a
                href="#/floor/{floor.id}"
                class="mb-4 block group hover:underline {floor.id ===
                $currentFloor?.id
                  ? 'current-floor'
                  : ''}"
                on:mouseenter={() => {
                  track({
                    action: "mouseenter",
                    params: {
                      object: "floor",
                      floor: floor.id,
                    },
                  });
                }}
                on:mouseleave={() => {
                  track({
                    action: "mouseleave",
                    params: {
                      object: "floor",
                      floor: floor.id,
                    },
                  });
                }}
                on:focus={() => {
                  track({
                    action: "focus",
                    params: {
                      object: "floor",
                      floor: floor.id,
                    },
                  });
                }}
                on:blur={() => {
                  track({
                    action: "blur",
                    params: {
                      object: "floor",
                      floor: floor.id,
                    },
                  });
                }}
              >
                <span
                  class="inline-block {floor.id === $currentFloor?.id
                    ? 'bg-blue-600'
                    : 'bg-neutral-600'} px-4 lg:px-3 py-3 lg:py-1 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800 lg:group-hover:bg-blue-800 lg:group-focus:bg-blue-800"
                  >⇒ {floor.label}</span
                >
                <span class="flex flex-row flex-wrap text-sm pl-4 pt-2">
                  {#if $topicsDict[floor.id]}
                    {#each $topicsDict[floor.id] as topic}
                      <span
                        class="after:content-[','] after:mr-1 last:after:hidden"
                        >{topic.label}</span
                      >
                    {/each}
                  {/if}
                </span>
              </a>
            </li>
          {/each}
        </ol>
      {/if}
      {#if $floors.isLoading || $rooms.isLoading}
        <Loading />
      {/if}
    </nav>
    <article id="content" class="flex-1 overflow-hidden relative" tabindex="-1">
      <nav class="hidden lg:flex flex-row absolute right-0 top-0">
        <div class="flex-none mr-2 lg:mr-4 mt-2 lg:mt-4">
          <button
            on:click={() => {
              changeMode(MODE_MAP);
            }}
            class="inline-block bg-neutral-600 px-3 py-3 lg:py-3 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800 {mode ===
            MODE_MAP
              ? 'bg-blue-600'
              : ''}"
            aria-label="Explore the museum's map"
          >
            <svg class="w-6 h-6" viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="M15,19L9,16.89V5L15,7.11M20.5,3C20.44,3 20.39,3 20.34,3L15,5.1L9,3L3.36,4.9C3.15,4.97 3,5.15 3,5.38V20.5A0.5,0.5 0 0,0 3.5,21C3.55,21 3.61,21 3.66,20.97L9,18.9L15,21L20.64,19.1C20.85,19 21,18.85 21,18.62V3.5A0.5,0.5 0 0,0 20.5,3Z"
              />
            </svg>
          </button>
        </div>
        <div class="flex-none mr-2 lg:mr-4 mt-2 lg:mt-4">
          <button
            on:click={() => {
              changeMode(MODE_LIST);
            }}
            class="inline-block bg-neutral-600 px-3 py-3 lg:py-3 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800 {mode ===
            MODE_LIST
              ? 'bg-blue-600'
              : ''}"
            aria-label="Explore the museum in text form"
          >
            <svg class="w-6 h-6" viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="M7,5H21V7H7V5M7,13V11H21V13H7M4,4.5A1.5,1.5 0 0,1 5.5,6A1.5,1.5 0 0,1 4,7.5A1.5,1.5 0 0,1 2.5,6A1.5,1.5 0 0,1 4,4.5M4,10.5A1.5,1.5 0 0,1 5.5,12A1.5,1.5 0 0,1 4,13.5A1.5,1.5 0 0,1 2.5,12A1.5,1.5 0 0,1 4,10.5M7,19V17H21V19H7M4,16.5A1.5,1.5 0 0,1 5.5,18A1.5,1.5 0 0,1 4,19.5A1.5,1.5 0 0,1 2.5,18A1.5,1.5 0 0,1 4,16.5Z"
              />
            </svg>
          </button>
        </div>
      </nav>
      <div
        id="game"
        class="w-full h-full {mode === MODE_MAP ? '' : 'hidden'}"
        aria-hidden="true"
      />
      {#if $hoverRoom}
        <div
          class="hidden lg:fixed lg:flex flex-col z-50 shadow-lg w-[150px] h-[150px] overflow-hidden bg-neutral-600"
          style="left: {mousePosition.x + 5}px; top: {mousePosition.y + 5}px;"
        >
          <h3
            class="truncate block px-2 py-1 hover:underline focus:underline bg-blue-800 text-white"
          >
            {$hoverRoom.label}
          </h3>
          {#if $samples.isSuccess}
            <ul class="flex-1 flex flex-col overflow-hidden px-2 py-2">
              <li class="flex-1 overflow-hidden">
                <Thumbnail item={$samples.data} noTitle={true} />
              </li>
            </ul>
          {/if}
        </div>
        <div
          class="fixed lg:hidden bottom-0 left-0 flex flex-col z-50 shadow-lg w-screen h-[150px] overflow-hidden bg-neutral-600"
        >
          <h3 class="flex flex-row px-2 py-1 bg-blue-800 text-white">
            <a
              href="#/room/{$hoverRoom.id}"
              class="flex-1 truncate block hover:underline focus:underline"
              >{$hoverRoom.label}</a
            >
            <button
              on:click={() => {
                hoverRoom.set(null);
              }}
              aria-label="Close"
            >
              <svg viewBox="0 0 24 24" class="w-6 h-6">
                <path
                  fill="currentColor"
                  d="M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2C6.47,2 2,6.47 2,12C2,17.53 6.47,22 12,22C17.53,22 22,17.53 22,12C22,6.47 17.53,2 12,2M14.59,8L12,10.59L9.41,8L8,9.41L10.59,12L8,14.59L9.41,16L12,13.41L14.59,16L16,14.59L13.41,12L16,9.41L14.59,8Z"
                />
              </svg>
            </button>
          </h3>
          {#if $samples.isSuccess}
            <ul class="flex-1 flex flex-col overflow-hidden px-2 py-2">
              <li class="flex-1 overflow-hidden">
                <Thumbnail item={$samples.data} noTitle={true} />
              </li>
            </ul>
          {/if}
        </div>
      {/if}
      <div class={mode === MODE_LIST ? "" : "hidden"}>
        {#if $rooms.isSuccess}
          <ol class="px-4 pb-6 pt-2 columns-sm">
            {#each $rooms.data as room}
              <li
                class="flex flex-row px-3 py-1 mb-3 {false // TODO: Fix search matches
                  ? 'bg-blue-600 rounded-lg data-matching'
                  : ''}"
              >
                <a
                  href="#/floor/{$currentFloor?.id}/room/{room.id}"
                  class="flex-1 block py-2 hover:underline focus:underline"
                  on:mouseenter={() => {
                    track({
                      action: "mouseenter",
                      params: {
                        object: "room",
                        floor: room.id,
                      },
                    });
                  }}
                  on:mouseleave={() => {
                    track({
                      action: "mouseleave",
                      params: {
                        object: "room",
                        floor: room.id,
                      },
                    });
                  }}
                  on:focus={() => {
                    track({
                      action: "focus",
                      params: {
                        object: "room",
                        floor: room.id,
                      },
                    });
                  }}
                  on:blur={() => {
                    track({
                      action: "blur",
                      params: {
                        object: "room",
                        floor: room.id,
                      },
                    });
                  }}>{room.label}</a
                >
              </li>
            {/each}
          </ol>
        {:else if $rooms.isLoading}
          <Loading />
        {/if}
      </div>
    </article>
  </div>
  <div class="flex-none lg:hidden">
    {#if $nextFloor}
      <a
        href="#/floor/{$nextFloor.id}"
        class="inline-block bg-neutral-600 px-4 py-3 lg:py-2 ml-2 lg:ml-4 mb-2 lg:mb-4 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800"
        on:mouseenter={() => {
          tracker.log({
            action: "mouseenter",
            params: { object: "next-floor", floor: $nextFloor?.id },
          });
        }}
        on:mouseleave={() => {
          tracker.log({
            action: "mouseleave",
            params: { object: "next-floor", floor: $nextFloor?.id },
          });
        }}
        on:focus={() => {
          tracker.log({
            action: "focus",
            params: { object: "next-floor", floor: $nextFloor?.id },
          });
        }}
        on:blur={() => {
          tracker.log({
            action: "blur",
            params: { object: "next-floor", floor: $nextFloor?.id },
          });
        }}>⇩ {$nextFloor.label}</a
      >
    {:else}
      <span
        class="inline-block px-4 py-3 lg:py-2 ml-2 lg:ml-4 mb-2 lg:mb-4 rounded-lg"
        >&nbsp;</span
      >
    {/if}
  </div>
  <Footer />
</div>
