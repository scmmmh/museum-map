<script lang="ts">
  import { onMount, onDestroy, tick } from "svelte";
  import { derived } from "svelte/store";
  import { createQuery } from "@tanstack/svelte-query";
  import { location } from "../simple-svelte-router";

  import { searchTerm, tracker } from "../store";

  let showSearchBox = false;
  let searchElement: HTMLElement | null = null;

  function searchToggle() {
    showSearchBox = !showSearchBox;
    searchTerm.set("");
    if (showSearchBox) {
      tick().then(() => {
        if (searchElement) {
          searchElement.focus();
        }
      });
    }
  }

  function submitSearch(ev: SubmitEvent) {
    ev.preventDefault();
  }

  const unsubscribeSearchTerm = searchTerm.subscribe((searchTerm) => {
    if (searchTerm.trim() !== "") {
      showSearchBox = true;
    }
  });

  onMount(() => {
    if ($location.search === "?search") {
      location.push($location.pathname);
      tick().then(() => {
        tick().then(() => {
          if (searchElement) {
            showSearchBox = true;
            tick().then(() => {
              if (searchElement) {
                searchElement.focus();
              }
            });
          }
        });
      });
    }
  });

  onDestroy(() => {
    unsubscribeSearchTerm();
  });
</script>

<form
  class="mr-2 flex flex-row border rounded-lg text-black bg-white text-black relative"
  on:submit={submitSearch}
  on:mouseenter={() => {
    tracker.log({ action: "mouseenter", params: { object: "searchform" } });
  }}
  on:mouseleave={() => {
    tracker.log({ action: "mouseleave", params: { object: "searchform" } });
  }}
>
  <input
    bind:this={searchElement}
    bind:value={$searchTerm}
    type="search"
    placeholder="Search the museum..."
    class="{!showSearchBox
      ? 'hidden'
      : 'block'} md:block flex-1 px-2 py-1 bg-transparent items-center"
    on:focus={() => {
      tracker.log({ action: "focus", params: { object: "searchinput" } });
    }}
    on:blur={() => {
      tracker.log({ action: "blur", params: { object: "searchinput" } });
    }}
  />
  <button
    on:click={searchToggle}
    type="button"
    class="block"
    aria-label={$searchTerm.trim() === ""
      ? "Search the museum"
      : "Clear your search"}
  >
    <svg viewBox="0 0 24 24" class="w-6 h-6" aria-hidden="true">
      {#if $searchTerm.trim() === ""}
        <path
          fill="currentColor"
          d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"
        />
      {:else}
        <path
          fill="currentColor"
          d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"
        />
      {/if}
    </svg>
  </button>
</form>
