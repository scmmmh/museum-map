<script lang="ts">
  import { createQuery } from "@tanstack/svelte-query";
  import { onDestroy, onMount, tick } from "svelte";
  import { derived } from "svelte/store";
  import { location, Route } from "../simple-svelte-router";

  import Header from "../components/Header.svelte";
  import Footer from "../components/Footer.svelte";
  import Thumnail from "../components/Thumbnail.svelte";
  import Item from "./Item.svelte";
  import { searchTerm } from "../store";
  import { apiRequest } from "../util";

  const floors = createQuery({
    queryKey: ["/floors/"],
    queryFn: apiRequest<Floor[]>,
  });

  const floor = derived([floors, location], ([floors, location]) => {
    if (location.pathComponents.fid && floors.isSuccess) {
      for (const floor of floors.data) {
        if (floor.id === Number.parseInt(location.pathComponents.fid)) {
          return floor;
        }
      }
    }
    return null;
  });

  const roomQueryOptions = derived(location, (location) => {
    return {
      queryKey: ["/rooms/", Number.parseInt(location.pathComponents.rid)],
      queryFn: apiRequest<Room>,
    };
  });
  const room = createQuery(roomQueryOptions);

  const itemsQueryOptions = derived(location, (location) => {
    return {
      queryKey: [
        "/rooms/",
        Number.parseInt(location.pathComponents.rid),
        "/items",
      ],
      queryFn: apiRequest<Item[]>,
    };
  });
  const items = createQuery(itemsQueryOptions);

  const searchQueryOptions = derived(
    [searchTerm, location],
    ([searchTerm, location]) => {
      return {
        queryKey: [
          "/api/search/room/",
          location.pathComponents.rid,
          searchTerm,
        ],
        queryFn: async () => {
          if (searchTerm.trim() !== "") {
            const response = await window.fetch(
              "/api/search/room/" +
                location.pathComponents.rid +
                "?q=" +
                searchTerm,
            );
            if (response.ok) {
              return await response.json();
            } else {
              throw new Error("Could not fetch search results");
            }
          } else {
            return { items: [] };
          }
        },
      };
    },
  );
  const searchResults = createQuery(searchQueryOptions);

  const unsubscribeItems = items.subscribe((currentItems) => {
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

{#if $floor !== null && $room.isSuccess}
  <Header
    title={$room.data.label}
    nav={[
      {
        label: $floor.label,
        path: "/floor/" + $floor.id,
      },
      {
        label: $room.data.label,
        path: "/floor/" + $floor.id + "/room/" + $room.data.id,
      },
    ]}
  />
  <article id="content" tabindex="-1">
    {#if $items.isSuccess}
      <ul
        class="grid grid-cols-1 md:grid-cols-items justify-around p-4 overflow-hidden"
      >
        {#each $items.data as item}
          <li
            class="p-4 mb-3 {$searchResults.isSuccess &&
            $searchResults.data.items.indexOf(item.id) >= 0
              ? 'bg-blue-600 rounded-lg data-matching'
              : ''}"
          >
            <Thumnail {item} on:load={debounceFocusFirstMatch} />
          </li>
        {/each}
      </ul>
    {/if}
    <Route path="/floor/:fid/room/:rid/item/:iid" handleFocus={false}
      ><Item /></Route
    >
  </article>
  <Footer />
{/if}
