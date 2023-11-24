<script lang="ts">
  import { createQuery, useQueryClient } from "@tanstack/svelte-query";
  import { createEventDispatcher } from "svelte";
  import { derived } from "svelte/store";
  import { tracker } from "../store";
  import { apiRequest } from "../util";

  export let item: Item;
  export let noLink = false;
  export let noTitle = false;
  export let size = "small";

  const dispatch = createEventDispatcher();

  function imageLink(imageId: string[] | undefined): string {
    if (imageId) {
      return (
        "/images/" +
        imageId.join("/") +
        (size === "large" ? "" : "-240") +
        ".jpg"
      );
    } else {
      return "";
    }
  }

  function loaded() {
    dispatch("load");
  }

  const room = createQuery({
    queryKey: ["/rooms/", item.room],
    queryFn: apiRequest<Room>,
  });

  const floors = createQuery({
    queryKey: ["/floors/"],
    queryFn: apiRequest<Floor[]>,
  });

  const floor = derived([floors, room], ([floors, room]) => {
    if (floors.isSuccess && room.isSuccess) {
      for (const floor of floors.data) {
        if (floor.id === room.data.floor) {
          return floor;
        }
      }
    }
    return null;
  });
</script>

{#if item !== null}
  {#if noLink}
    <div class="block h-full w-full overflow-hidden">
      <figure
        class="flex flex-col justify-center items-center h-full overflow-hidden"
      >
        <img
          class="block shrink-1 grow-1 min-h-0"
          src={imageLink(item.attributes.images[0])}
          alt=""
          on:load={loaded}
        />
        <figcaption
          class="flex-none max-w-full pt-2 text-center text-sm {noTitle
            ? 'sr-only'
            : ''}"
        >
          {item.attributes.title}
        </figcaption>
      </figure>
    </div>
  {:else}
    <a
      href="#/floor/{$floor !== null ? $floor.id : null}/room/{$room.isSuccess
        ? $room.data.id
        : -1}/item/{item.id}"
      class="block h-full w-full overflow-hidden underline-offset-2 hover:img-brightness hover:underline focus:underline"
      aria-label={item.attributes.title}
      on:mouseenter={() => {
        tracker.log({
          action: "mouseenter",
          params: { object: "thumbnail", thumbnail: item.id },
        });
      }}
      on:mouseleave={() => {
        tracker.log({
          action: "mouseleave",
          params: { object: "thumbnail", thumbnail: item.id },
        });
      }}
      on:focus={() => {
        tracker.log({
          action: "focus",
          params: { object: "thumbnail", thumbnail: item.id },
        });
      }}
      on:blur={() => {
        tracker.log({
          action: "blur",
          params: { object: "thumbnail", thumbnail: item.id },
        });
      }}
    >
      <figure
        class="flex flex-col justify-center items-center h-full overflow-hidden"
      >
        <img
          class="block shrink-1 grow-1 min-h-0 transition"
          src={imageLink(item.attributes.images[0])}
          alt=""
          on:load={loaded}
        />
        <figcaption
          class="flex-none max-w-full pt-2 text-center text-sm {noTitle
            ? 'sr-only'
            : ''}"
        >
          {item.attributes.title}
        </figcaption>
      </figure>
    </a>
  {/if}
{/if}
