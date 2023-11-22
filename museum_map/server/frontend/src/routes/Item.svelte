<script lang="ts">
  import { onDestroy, tick } from "svelte";
  import { derived } from "svelte/store";
  import { location } from "../simple-svelte-router";

  import Thumbnail from "../components/Thumbnail.svelte";
  import {
    currentFloor,
    currentRoom,
    currentItem,
    currentItems,
    config,
    tracker,
  } from "../store";

  let itemHeading: HTMLElement | null = null;

  const previousItem = derived(
    [currentItem, currentItems],
    ([currentItem, currentItems]) => {
      if (currentItem) {
        let previousItem = null;
        for (const item of currentItems) {
          if (item.id === currentItem.id) {
            return previousItem;
          }
          previousItem = item;
        }
        if (currentItems.length > 0) {
          return currentItems[currentItems.length - 1];
        }
      }
      return null;
    },
    null as Item | null,
  );

  const nextItem = derived(
    [currentItem, currentItems],
    ([currentItem, currentItems]) => {
      if (currentItem) {
        let found = false;
        for (const item of currentItems) {
          if (found) {
            return item;
          }
          if (item.id === currentItem.id) {
            found = true;
          }
        }
        if (currentItems.length > 0) {
          return currentItems[currentItems.length - 1];
        }
      }
      return null;
    },
  );

  let touchStartX = 0;
  let touchStartY = 0;

  function touchStart(ev: TouchEvent) {
    touchStartX = ev.changedTouches[0].clientX;
    touchStartY = ev.changedTouches[0].clientY;
  }

  function touchEnd(ev: TouchEvent) {
    const touchEndX = ev.changedTouches[0].clientX;
    const touchEndY = ev.changedTouches[0].clientY;
    if (Math.abs(touchEndY - touchStartY) < 100) {
      if (touchEndX - touchStartX < 50 && $nextItem) {
        location.push(
          "/floor/" +
            $currentFloor?.id +
            "/room/" +
            $currentRoom?.id +
            "/" +
            $nextItem.id,
        );
      } else if (touchEndX - touchStartX > 50 && $previousItem) {
        location.push(
          "/floor/" +
            $currentFloor?.id +
            "/room/" +
            $currentRoom?.id +
            "/" +
            $previousItem.id,
        );
      }
    }
  }

  function processParagraph(paragraph: string) {
    return paragraph
      .replace(/<[iI]>/g, "\\begin{em}")
      .replace(/<\/[iI]>/g, "\\end{em}")
      .replace(/<[uU]>/g, "\\begin{em}")
      .replace(/<\/[uU]>/g, "\\end{em}")
      .replace(/<[bB]>/g, "\\begin{strong}")
      .replace(/<\/[bB]>/g, "\\end{strong}")
      .replace(/<\/?[a-zA-Z]+>/g, "")
      .replace(/\\begin\{em\}/g, "<em>")
      .replace(/\\end\{em\}/g, "</em>")
      .replace(/\\begin\{strong\}/g, "<strong>")
      .replace(/\\end\{strong\}/g, "</strong>");
  }

  function processText(text: string) {
    const paras = [] as string[];
    text.split("\n\n").forEach((part1) => {
      part1.split("<br><br>").forEach((part2) => {
        paras.push(processParagraph(part2));
      });
    });
    return paras;
  }

  function formatField(item: string | string[]) {
    if (Array.isArray(item)) {
      return item.join(", ");
    } else {
      return item;
    }
  }

  const currentItemUnsubscribe = currentItem.subscribe((currentItem) => {
    if (currentItem) {
      tick().then(() => {
        if (itemHeading) {
          itemHeading.focus();
        }
      });
    }
  });

  onDestroy(currentItemUnsubscribe);
</script>

<section
  on:touchstart={touchStart}
  on:touchend={touchEnd}
  class="fixed left-0 top-0 w-screen h-screen bg-neutral-800 bg-opacity-80 z-20"
  on:click={() => {
    location.push("/floor/" + $currentFloor?.id + "/room/" + $currentRoom?.id);
  }}
>
  <div
    class="absolute left-0 top-0 lg:left-1/2 lg:top-1/2 lg:transform lg:-translate-x-1/2 lg:-translate-y-1/2 w-full lg:w-5/6 xl:w-4/6 h-full lg:max-h-5/6 xl:max-h-4/6 flex flex-col bg-neutral-800 shadow-xl shadow-black overflow-auto lg:overflow-visible"
    on:click={(ev) => {
      ev.stopPropagation();
    }}
  >
    {#if $currentItem}
      <button
        on:click={() => {
          location.push(
            "/floor/" + $currentFloor?.id + "/room/" + $currentRoom?.id,
          );
        }}
        class="block absolute right-0 top-0 lg:transform lg:translate-x-1/2 lg:-translate-y-1/2 rounded-full shadow-lg text-2xl w-10 h-10 bg-neutral-800 z-10"
        >✖</button
      >
      <div class="flex flex-row items-center flex-none bg-blue-900">
        <h2
          bind:this={itemHeading}
          class="flex-1 px-4 py-2 text-lg font-bold"
          tabindex="-1"
        >
          {$currentItem.attributes.title
            ? processParagraph($currentItem.attributes.title)
            : "[Untitled]"}
        </h2>
        <div role="presentation" class="w-10" />
      </div>
      <div class="flex-none lg:flex-1 lg:flex lg:flex-row lg:overflow-hidden">
        <div class="hidden lg:flex flex-none flex-col justify-center px-4">
          <a
            href="#/floor/{$currentFloor?.id}/room/{$currentRoom?.id}/item/{$previousItem?.id}"
            class="block text-xl bg-neutral-600 px-2 py-1 rounded-lg">&laquo;</a
          >
        </div>
        <div class="p-4 lg:flex-1 lg:h-full lg:self-start lg:overflow-hidden">
          <Thumbnail
            item={$currentItem}
            noLink={true}
            noTitle={true}
            size="large"
          />
        </div>
        <div class="m-4 lg:flex-1 lg:overflow-auto">
          {#if $config}
            {#each $config.item.texts as textConfig}
              {#if $currentItem.attributes[textConfig.name]}
                {#each processText($currentItem.attributes[textConfig.name]) as para}
                  <p
                    class="mb-2"
                    on:mouseenter={() => {
                      tracker.log({
                        action: "mouseenter",
                        params: { object: "metadata", field: textConfig.name },
                      });
                    }}
                    on:mouseleave={() => {
                      tracker.log({
                        action: "mouseleave",
                        params: { object: "metadata", field: textConfig.name },
                      });
                    }}
                  >
                    {@html para}
                  </p>
                {/each}
              {/if}
            {/each}
          {/if}
          <table class="mt-8">
            {#each $config.item.fields as fieldConfig}
              {#if $currentItem.attributes[fieldConfig.name] && $currentItem.attributes[fieldConfig.name].length}
                <tr
                  on:mouseenter={() => {
                    tracker.log({
                      action: "mouseenter",
                      params: { object: "metadata", field: fieldConfig.name },
                    });
                  }}
                  on:mouseleave={() => {
                    tracker.log({
                      action: "mouseleave",
                      params: { object: "metadata", field: fieldConfig.name },
                    });
                  }}
                >
                  <th
                    scope="row"
                    class="font-normal text-sm text-neutral-300 text-right pr-2 align-bottom"
                    >{fieldConfig.label}</th
                  >
                  <td
                    >{formatField(
                      $currentItem.attributes[fieldConfig.name],
                    )}</td
                  >
                </tr>
              {/if}
            {/each}
          </table>
        </div>
        <div class="hidden lg:flex flex-none flex-col justify-center px-4">
          <a
            href="#/floor/{$currentFloor?.id}/room/{$currentRoom?.id}/item/{$nextItem.id}"
            class="block text-xl bg-neutral-600 px-2 py-1 rounded-lg">&raquo;</a
          >
        </div>
      </div>
    {:else}
      <p class="self-center text-center w-full">Loading...</p>
    {/if}
  </div>
</section>
