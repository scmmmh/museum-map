<script lang="ts">
  import { onDestroy } from "svelte";
  import { fade } from "svelte/transition";
  import { Route } from "./simple-svelte-router";

  import Lobby from "./routes/Lobby.svelte";
  import Floor from "./routes/Floor.svelte";
  import Room from "./routes/Room.svelte";
  import { isBusy, isUpdatable } from "./store";

  import {
    fetchFloorTopics,
    fetchFloors,
    fetchConfig,
    fetchStatus,
  } from "./store";

  let statusInterval = window.setInterval(() => {
    fetchStatus();
  }, 60000);

  fetchFloorTopics();
  fetchFloors();
  fetchConfig();
  fetchStatus();

  onDestroy(() => {
    window.clearInterval(statusInterval);
  });
</script>

<div class="bg-neutral-600 min-h-screen">
  <main
    class="container mx-auto bg-neutral-700 text-white shadow-lg shadow-black font-serif tracking-default"
  >
    <Route path="/"><Lobby /></Route>
    <Route path="/floor/:id"><Floor /></Route>
    <Route path="/room/:id"><Room /></Route>

    {#if $isUpdatable}
      <div class="absolute left-0 bottom-0 pb-2 pl-2">
        <a
          href="./"
          class="block text-xs bg-blue-800 px-4 py-2 rounded-lg hover:underline focus:underline shadow"
          >Please reload for the latest version.</a
        >
      </div>
    {/if}

    {#if $isBusy}
      <div
        transition:fade
        class="fixed left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 p-4 bg-neutral-700 shadow-2xl rounded-2xl"
        role="alert"
      >
        <span class="sr-only">Loading... Please wait...</span>
        <svg
          class="w-20 h-20 text-white stroke-current"
          viewBox="0 0 45 45"
          xmlns="http://www.w3.org/2000/svg"
        >
          <g
            fill="none"
            fill-rule="evenodd"
            transform="translate(1 1)"
            stroke-width="2"
          >
            <circle cx="22" cy="22" r="6" stroke-opacity="0">
              <animate
                attributeName="r"
                begin="1.5s"
                dur="3s"
                values="6;22"
                calcMode="linear"
                repeatCount="indefinite"
              />
              <animate
                attributeName="stroke-opacity"
                begin="1.5s"
                dur="3s"
                values="1;0"
                calcMode="linear"
                repeatCount="indefinite"
              />
              <animate
                attributeName="stroke-width"
                begin="1.5s"
                dur="3s"
                values="2;0"
                calcMode="linear"
                repeatCount="indefinite"
              />
            </circle>
            <circle cx="22" cy="22" r="6" stroke-opacity="0">
              <animate
                attributeName="r"
                begin="3s"
                dur="3s"
                values="6;22"
                calcMode="linear"
                repeatCount="indefinite"
              />
              <animate
                attributeName="stroke-opacity"
                begin="3s"
                dur="3s"
                values="1;0"
                calcMode="linear"
                repeatCount="indefinite"
              />
              <animate
                attributeName="stroke-width"
                begin="3s"
                dur="3s"
                values="2;0"
                calcMode="linear"
                repeatCount="indefinite"
              />
            </circle>
            <circle cx="22" cy="22" r="8">
              <animate
                attributeName="r"
                begin="0s"
                dur="1.5s"
                values="6;1;2;3;4;5;6"
                calcMode="linear"
                repeatCount="indefinite"
              />
            </circle>
          </g>
        </svg>
      </div>
    {/if}
  </main>
</div>

<style global>
  @tailwind base;
  @tailwind components;
  @tailwind utilities;

  @layer utilities {
    ol.child-separator li::after,
    ul.child-separator li::after {
      content: "»";
    }

    ol.child-separator li:last-child::after,
    ul.child-separator li:last-child::after {
      content: "";
    }

    ol.list-separator li::after,
    ul.list-separator li::after {
      content: ",";
    }

    ol.list-separator li:last-child::after,
    ul.list-separator li:last-child::after {
      content: "";
    }

    .hover-parent:hover .hover-child-underline,
    .hover-parent:focus .hover-child-underline {
      @apply underline;
    }

    .img-brightness img {
      @apply brightness-75;
    }
  }

  @layer components {
    figure.title-hover figcaption {
      @apply opacity-0 transition-opacity duration-300;
    }
    figure.title-hover:hover figcaption,
    figure.title-hover:focus figcaption {
      @apply opacity-100;
    }
  }
</style>
