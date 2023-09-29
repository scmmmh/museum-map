<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { tracker } from "../store";

  export let item: JsonApiObject;
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

  function linkTo(item: JsonApiObject) {
    if (item && item.relationships.room) {
      return (
        "#/room/" +
        (item.relationships.room.data as JsonApiObjectReference).id +
        "/" +
        item.id
      );
    } else {
      return "/";
    }
  }

  function loaded() {
    dispatch("load");
  }
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
      href={linkTo(item)}
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
