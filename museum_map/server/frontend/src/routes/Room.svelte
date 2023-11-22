<script lang="ts">
  import { onDestroy, onMount, tick } from "svelte";
  import { derived } from "svelte/store";
  import { location, Route } from "../simple-svelte-router";

  import Header from "../components/Header.svelte";
  import Footer from "../components/Footer.svelte";
  import Thumnail from "../components/Thumbnail.svelte";
  import Item from "./Item.svelte";
  import { currentFloor, currentRoom, currentItems } from "../store";

  const matchedItems = derived(currentItems, (currentItems) => {
    return currentItems.map((item) => {
      return [item, false];
    });
  });

  const unsubscribeItems = currentItems.subscribe((currentItems) => {
    tick().then(() => {
      focusFirstMatch(true);
    });
  });

  onMount(() => {
    tick().then(() => {
      focusFirstMatch(false);
    });
  });

  onDestroy(unsubscribeItems);

  function focusFirstMatch(smooth: boolean) {
    const firstMatch = document.querySelector("li.data-matching");
    if (firstMatch) {
      firstMatch.scrollIntoView({
        block: "center",
        behavior: smooth ? "smooth" : "auto",
      });
    } else {
      const element = document.querySelector("h1");
      if (element) {
        (element as HTMLElement).focus();
      }
    }
  }

  let debounceFocusFirstMatchTimeout = -1;

  function debounceFocusFirstMatch() {
    window.clearTimeout(debounceFocusFirstMatchTimeout);
    debounceFocusFirstMatchTimeout = window.setTimeout(() => {
      focusFirstMatch(true);
    }, 50);
  }
</script>

{#if $currentRoom && $currentFloor}
  <Header
    title={$currentRoom.label}
    nav={[
      {
        label: $currentFloor.label,
        path: "/floor/" + $currentFloor.id,
      },
      {
        label: $currentRoom.label,
        path: "/floor/" + $currentFloor.id + "/room/" + $currentRoom.id,
      },
    ]}
  />
  <article id="content" tabindex="-1">
    <ul
      class="grid grid-cols-1 md:grid-cols-items justify-around p-4 overflow-hidden"
    >
      {#each $matchedItems as [item, matches]}
        <li
          class="p-4 mb-3 {matches
            ? 'bg-blue-600 rounded-lg data-matching'
            : ''}"
        >
          <Thumnail {item} on:load={debounceFocusFirstMatch} />
        </li>
      {/each}
    </ul>
    <Route path="/floor/:fid/room/:rid/item/:iid" handleFocus={false}
      ><Item /></Route
    >
  </article>
  <Footer />
{/if}
