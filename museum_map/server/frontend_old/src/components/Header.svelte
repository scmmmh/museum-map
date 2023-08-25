<script lang="ts">
  import { afterUpdate, onDestroy, onMount, tick } from "svelte";
  import { location } from "../simple-svelte-router";

  import { isBusy, searchTerm, searchRoom, floors } from "../store";

  export let title: string;
  export let nav: { path: string; label: string }[];

  let showNav = false;
  let showSearch = false;
  let searchElement: HTMLElement | null = null;

  const unsubscribeLocation = location.subscribe((location) => {
    if (location.pathname.startsWith("/room")) {
      const parts = location.pathname.split("/");
      searchRoom.set(parts[2]);
    } else {
      searchRoom.set(null);
    }
  });

  const unsubscribeSearchTerm = searchTerm.subscribe((searchTerm) => {
    if (
      searchTerm.trim() !== "" &&
      $location.pathname === "/" &&
      $floors.length > 0
    ) {
      location.push("/floor/" + $floors[0].id + "?search");
    }
    if (searchTerm.trim() !== "") {
      showSearch = true;
    }
  });

  function searchToggle() {
    showSearch = !showSearch;
    searchTerm.set("");
    if (showSearch) {
      tick().then(() => {
        searchElement.focus();
      });
    }
  }

  function submitSearch(ev: SubmitEvent) {
    ev.preventDefault();
    window.location.hash = "#content";
  }

  onMount(() => {
    if ($location.search === "?search") {
      location.push($location.pathname);
      tick().then(() => {
        tick().then(() => {
          if (searchElement) {
            showSearch = true;
            tick().then(() => {
              searchElement.focus();
            });
          }
        });
      });
    }
  });

  afterUpdate(() => {
    document.title = title;
  });

  onDestroy(() => {
    unsubscribeLocation();
    unsubscribeSearchTerm();
  });
</script>

<header class="sticky top-0 shadow-even shadow-black z-20 bg-inherit">
  <div class="flex flex-row border-b border-b-neutral-500 items-center">
    <h1
      class="{showSearch
        ? 'truncate'
        : ''} flex-1 text-lg font-bold px-2 py-2 md:mr-4"
    >
      {title}
    </h1>
    <a
      href="#content"
      class="block fixed z-50 top-[-200px] focus:top-0 left-1/2 transform -translate-x-1/2 bg-neutral-600 px-10 py-2 rounded-b-lg shadow-even shadow-black"
      >Jump to content</a
    >
    {#if $isBusy}
      <div class="sr-only" role="alert">Loading data</div>
      <svg
        viewBox="0 0 38 38"
        xmlns="http://www.w3.org/2000/svg"
        stroke="#ffffff"
        class="flex-none w-8 h-6 pr-2"
        aria-hidden="true"
      >
        <g fill="none" fill-rule="evenodd">
          <g transform="translate(1 1)" stroke-width="3">
            <path d="M36 18c0-9.94-8.06-18-18-18">
              <animateTransform
                attributeName="transform"
                type="rotate"
                from="0 18 18"
                to="360 18 18"
                dur="1.5s"
                repeatCount="indefinite"
              />
            </path>
          </g>
        </g>
      </svg>
    {/if}
    <form
      class="mr-2 flex flex-row border rounded-lg text-black bg-white text-black relative"
      on:submit={submitSearch}
    >
      <input
        bind:this={searchElement}
        bind:value={$searchTerm}
        type="search"
        placeholder="Search the museum..."
        class="{!showSearch
          ? 'hidden'
          : 'block'} md:block flex-1 px-2 py-1 bg-transparent items-center"
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
  </div>
  <nav class="flex flex-row items-start" aria-label="Main">
    <ol class="flex-1 flex flex-col md:flex-row md:child-separator">
      <li
        class="flex-none {!showNav && nav.length > 0 ? 'hidden md:block' : ''}"
      >
        <a
          href="#/"
          class="inline-block px-2 py-3 hover:underline focus:underline"
          on:click={() => {
            searchTerm.set("");
          }}>Lobby</a
        >
      </li>
      {#if nav}
        {#each nav as item, idx}
          <li
            class="flex-none {!showNav && idx < nav.length - 1
              ? 'hidden md:block'
              : ''}"
          >
            <button
              on:click={() => {
                showNav = !showNav;
              }}
              class="{showNav
                ? 'hidden'
                : 'block'} flex-none text-left px-2 py-3 md:hidden"
              aria-label="Toggle the main navigation">{item.label}</button
            >
            <a
              href="#{item.path}"
              class="{showNav
                ? 'inline-block'
                : ' hidden md:inline-block'} px-2 py-3 hover:underline focus:underline"
              >{item.label}</a
            >
          </li>
        {/each}
      {/if}
    </ol>
    <button
      on:click={() => {
        showNav = !showNav;
      }}
      class="flex-none block px-2 py-2 md:hidden"
      aria-label="Toggle the main navigation"
    >
      <svg viewBox="0 0 24 24" class="w-8 h-8" aria-hidden="true">
        {#if showNav}
          <path
            fill="currentColor"
            d="M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z"
          />
        {:else}
          <path
            fill="currentColor"
            d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z"
          />
        {/if}
      </svg>
    </button>
  </nav>
</header>
