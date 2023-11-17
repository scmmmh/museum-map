<script lang="ts">
  import { onDestroy } from "svelte";
  import { fade } from "svelte/transition";
  import { Route } from "./simple-svelte-router";

  import Lobby from "./routes/Lobby.svelte";
  import Room from "./routes/Room.svelte";
  import TrackingConfig from "./components/TrackingConfig.svelte";
  import {
    isConnected,
    isBusy,
    isUpdatable,
    isReady,
    isLoaded,
    loadingProgress,
  } from "./store";

  let Floor = null;
  import("./routes/Floor.svelte").then((module) => {
    Floor = module.default;
  });
</script>

<div class="bg-neutral-600 min-h-screen">
  {#if $isConnected && $isLoaded}
    <main
      class="container mx-auto bg-neutral-700 text-white shadow-lg shadow-black font-serif tracking-default"
    >
      <Route path="/"><Lobby /></Route>
    </main>
  {:else}
    <div
      transition:fade
      class="fixed left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 p-4 bg-neutral-700 shadow-2xl rounded-2xl"
      role="alert"
    >
      <span class="sr-only"
        >Waiting for the application to become ready... Please wait...</span
      >
      <svg
        class="w-20 h-20 text-white stroke-current"
        viewBox="0 0 45 45"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
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
      {#if $isReady}
        <svg
          id="svg"
          viewBox="0 0 200 200"
          version="1.1"
          xmlns="http://www.w3.org/2000/svg"
          style="stroke-dashoffset: 0;transition: stroke-dashoffset 1s linear;stroke: #666;stroke-width: 1em;"
          class="absolute left-1/2 top-1/2 w-24 h-24 transform -translate-x-1/2 -translate-y-1/2"
          aria-hidden="true"
        >
          <circle
            r="90"
            cx="100"
            cy="100"
            fill="transparent"
            stroke-dasharray="565.48"
            stroke-dashoffset="0"
          />
          <circle
            id="bar"
            r="90"
            cx="100"
            cy="100"
            fill="transparent"
            stroke-dasharray="565.48"
            stroke-dashoffset="0"
            style="stroke: #ffffff; stroke-dashoffset: {(Math.PI *
              90 *
              2 *
              (100 - $loadingProgress)) /
              100}"
          />
        </svg>
      {/if}
    </div>
  {/if}
  <!--  <main
    class="container mx-auto bg-neutral-700 text-white shadow-lg shadow-black font-serif tracking-default"
  >
    <Route path="/"><Lobby /></Route>
    <Route path="/floor/:id"
      >{#if Floor !== null}<svelte:component this={Floor} />{/if}</Route
    >
    <Route path="/room/:id" handleFocus={false}><Room /></Route>

    {#if $isUpdatable}
      <div class="absolute left-0 bottom-0 pb-2 pl-2 z-20">
        <a
          href="./"
          class="block text-xs bg-blue-800 px-4 py-2 rounded-lg hover:underline focus:underline shadow"
          >Please reload for the latest version.</a
        >
      </div>
    {/if}

    {#if !$isReady}
      <div
        transition:fade
        class="fixed left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 p-4 bg-neutral-700 shadow-2xl rounded-2xl"
        role="alert"
      >
        <span class="sr-only"
          >Waiting for the application to become ready... Please wait...</span
        >
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
  <TrackingConfig />-->
</div>
