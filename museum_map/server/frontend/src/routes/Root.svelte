<script lang="ts">
    import { Router, Route } from "svelte-navigator";
    import { fade } from "svelte/transition";

    import Lobby from "./Lobby.svelte";
    import Floor from "./Floor.svelte";
    import Room from "./Room.svelte";
    import { isBusy, isUpdatable } from "../store";
</script>

<Router>
    <Route path="/"><Lobby /></Route>
    <Route path="/floor/:id"><Floor /></Route>
    <Route path="/room/:id/*"><Room /></Route>
</Router>

{#if $isUpdatable}
    <div class="absolute left-0 bottom-0 pb-2 pl-2">
        <a
            href=""
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
