<script lang="ts">
  import Header from "../components/Header.svelte";
  import Footer from "../components/Footer.svelte";
  import Thumnail from "../components/Thumbnail.svelte";
  import {
    config,
    itemOfTheDay,
    randomItemsSelection,
    majorCollections,
    floors,
    localPreferences,
    tracker,
  } from "../store";
</script>

<Header title="Museum Map - Lobby" nav={[]} />
<article id="content" tabindex="-1">
  <div class="flex flex-col md:grid md:grid-cols-12 gap-8 p-4">
    {#if $config && $config.attributes.intro && (!$localPreferences.lobby || !$localPreferences.lobby.hideWelcome)}
      <section class="col-span-12 my-5">
        <div
          class="relative max-w-4xl mx-auto border border-neutral-500 shadow-xl px-2 py-2"
        >
          <button
            on:click={() => {
              localPreferences.setPreference("lobby.hideWelcome", true);
            }}
            class="block absolute right-0 top-0 lg:transform lg:translate-x-1/2 lg:-translate-y-1/2 rounded-full text-lg bg-neutral-600 border border-neutral-500 z-10 shadow"
            aria-label="Close"
          >
            <svg viewBox="0 0 24 24" class="w-7 h-7 p-1">
              <path
                fill="currentColor"
                d="M20 6.91L17.09 4L12 9.09L6.91 4L4 6.91L9.09 12L4 17.09L6.91 20L12 14.91L17.09 20L20 17.09L14.91 12L20 6.91Z"
              />
            </svg>
          </button>
          {#each $config.attributes.intro.split("\n\n") as line}
            <p>{@html line}</p>
          {/each}
        </div>
      </section>
    {/if}
    {#if $itemOfTheDay}
      <section class="md:col-span-6 lg:col-span-4 flex flex-col h-[25rem]">
        <h2 class="flex-none text-xl font-bold mb-4">Item of the Day</h2>
        <div class="flex-1 overflow-hidden">
          <Thumnail item={$itemOfTheDay} size="large" />
        </div>
      </section>
    {/if}
    <section class="md:col-span-6 lg:col-span-8 flex flex-col">
      <h2 class="flex-none text-xl font-bold mb-4">Major Collections</h2>
      <div class="flex-1">
        <ul class="grid grid-cols-2 lg:grid-cols-3 gap-4">
          {#each $majorCollections as collection}
            <li>
              <span class="font-bold text-lg">{collection.label}</span>
              <ul class="flex flex-row flex-wrap gap-2">
                {#each collection.floors as floor}
                  <li class="flex-none">
                    <a
                      href={"#/floor/" + floor.id}
                      class="inline-block bg-neutral-600 px-4 lg:px-3 py-3 lg:py-1 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800"
                      on:mouseenter={() => {
                        tracker.log({
                          action: "mouseenter",
                          params: { object: "floor-link", floor: floor.id },
                        });
                      }}
                      on:mouseleave={() => {
                        tracker.log({
                          action: "mouseleave",
                          params: { object: "floor-link", floor: floor.id },
                        });
                      }}
                      on:focus={() => {
                        tracker.log({
                          action: "focus",
                          params: { object: "floor-link", floor: floor.id },
                        });
                      }}
                      on:blur={() => {
                        tracker.log({
                          action: "blur",
                          params: { object: "floor-link", floor: floor.id },
                        });
                      }}>⇒ {floor.label}</a
                    >
                  </li>
                {/each}
              </ul>
            </li>
          {/each}
        </ul>
        {#if $floors && $floors.length > 0}
          <div class="mt-16 mb-8 text-center">
            <a
              href={"#/floor/" + $floors[0].id}
              class="inline-block text-xl tracking-widest font-bold bg-blue-800 px-4 py-2 rounded-lg hover:underline focus:underline"
              on:mouseenter={() => {
                tracker.log({
                  action: "mouseenter",
                  params: { object: "explore-everything" },
                });
              }}
              on:mouseleave={() => {
                tracker.log({
                  action: "mouseleave",
                  params: { object: "explore-everything" },
                });
              }}
              on:focus={() => {
                tracker.log({
                  action: "focus",
                  params: { object: "explore-everything" },
                });
              }}
              on:blur={() => {
                tracker.log({
                  action: "blur",
                  params: { object: "explore-everything" },
                });
              }}>Explore the whole collection ⇒</a
            >
          </div>
        {/if}
      </div>
    </section>
    <section class="col-span-12 mt-4">
      <div class="flex flex-row">
        <h2 class="flex-1 text-xl font-bold mb-4">
          Selection from our collections
        </h2>
        <button
          on:click={() => {
            tracker.log({
              action: "refresh-random-items",
              params: {},
            });
            randomItemsSelection.refresh();
          }}
          on:mouseenter={() => {
            tracker.log({
              action: "mouseenter",
              params: { object: "reload-random-selection" },
            });
          }}
          on:mouseleave={() => {
            tracker.log({
              action: "mouseleave",
              params: { object: "reload-random-selection" },
            });
          }}
          on:focus={() => {
            tracker.log({
              action: "focus",
              params: { object: "reload-random-selection" },
            });
          }}
          on:blur={() => {
            tracker.log({
              action: "blur",
              params: { object: "reload-random-selection" },
            });
          }}
          class="flex-none px-2 py-2"
          aria-label="Update the selection of items from the collection"
          title="Update the selection of items from the collection"
        >
          <svg
            viewBox="0 0 24 24"
            class="w-6 h-6 fill-white"
            aria-hidden="true"
          >
            <path
              d="M2 12C2 16.97 6.03 21 11 21C13.39 21 15.68 20.06 17.4 18.4L15.9 16.9C14.63 18.25 12.86 19 11 19C4.76 19 1.64 11.46 6.05 7.05C10.46 2.64 18 5.77 18 12H15L19 16H19.1L23 12H20C20 7.03 15.97 3 11 3C6.03 3 2 7.03 2 12Z"
            />
          </svg>
        </button>
      </div>
      <ul class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {#if $randomItemsSelection !== null}
          {#each $randomItemsSelection as item}
            <li><Thumnail {item} /></li>
          {/each}
        {/if}
      </ul>
    </section>
  </div>
</article>
<Footer />
