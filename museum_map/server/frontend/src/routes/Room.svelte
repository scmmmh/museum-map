<script lang="ts">
  import { onDestroy, onMount, tick } from "svelte";
  import { derived } from "svelte/store";
  import { location, Route } from "../simple-svelte-router";

  import Header from "../components/Header.svelte";
  import Footer from "../components/Footer.svelte";
  import Thumnail from "../components/Thumbnail.svelte";
  import Item from "./Item.svelte";
  import {
    floors,
    cachedRooms,
    loadRooms,
    cachedItems,
    loadItems,
    matchingItems,
  } from "../store";

  const currentRoom = derived(
    [location, cachedRooms],
    ([location, cachedRooms]) => {
      if (!cachedRooms[location.pathComponents[1]]) {
        loadRooms([location.pathComponents[1]]);
      }
      return cachedRooms[location.pathComponents[1]];
    },
    null
  );

  const currentFloor = derived(
    [currentRoom, floors],
    ([currentRoom, floors]) => {
      if (currentRoom) {
        const floor = floors.filter((floor) => {
          return (
            floor.id ===
            (currentRoom.relationships.floor.data as JsonApiObjectReference).id
          );
        });
        if (floor.length > 0) {
          return floor[0];
        }
      }
      return null;
    },
    null
  );

  const items = derived(
    [currentRoom, cachedItems, matchingItems],
    ([currentRoom, cachedItems, matchingItems]) => {
      if (currentRoom) {
        let itemIds = (
          currentRoom.relationships.items.data as JsonApiObjectReference[]
        ).map((ref) => {
          return ref.id;
        });
        let items = itemIds
          .map((id) => {
            return cachedItems[id];
          })
          .filter((item) => {
            return item;
          })
          .map((item) => {
            return [item, matchingItems.indexOf(item.id) >= 0];
          });
        if (itemIds.length != items.length) {
          loadItems(itemIds);
        }
        return items;
      }
      return [];
    },
    []
  );

  const unsubscribeItems = items.subscribe((items) => {
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
    }
    if ($location.pathComponents.length === 2) {
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
    title={$currentRoom.attributes.label}
    nav={[
      {
        label: $currentFloor.attributes.label,
        path: "/floor/" + $currentFloor.id,
      },
      {
        label: $currentRoom.attributes.label,
        path: "/room/" + $currentRoom.id,
      },
    ]}
  />
  <article id="content" tabindex="-1">
    <ul
      class="grid grid-cols-1 md:grid-cols-items justify-around p-4 overflow-hidden"
    >
      {#each $items as [item, matches]}
        <li
          class="p-4 mb-3 {matches
            ? 'bg-blue-600 rounded-lg data-matching'
            : ''}"
        >
          <Thumnail {item} on:load={debounceFocusFirstMatch} />
        </li>
      {/each}
    </ul>
    <Route path="/room/:rid/:iid" handleFocus={false}><Item /></Route>
  </article>
  <Footer />
{/if}
