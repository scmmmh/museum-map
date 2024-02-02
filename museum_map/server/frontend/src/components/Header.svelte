<script lang="ts">
  import { afterUpdate, onDestroy } from "svelte";
  import { location } from "../simple-svelte-router";
  import { createQuery, useIsFetching } from "@tanstack/svelte-query";

  import SearchBox from "./SearchBox.svelte";
  import { searchTerm } from "../store";
  import { apiRequest } from "../util";

  export let title: string;
  export let nav: { path: string; label: string }[];

  const isFetching = useIsFetching();
  let showNav = false;
  let showSearch = false;

  const floors = createQuery({
    queryKey: ["/floors/"],
    queryFn: apiRequest<Floor[]>,
  });

  function focusContent() {
    const element = document.querySelector("#content");
    if (element !== null) {
      (element as HTMLElement).focus();
    }
  }

  const unsubscribeSearchTerm = searchTerm.subscribe((searchTerm) => {
    if (
      searchTerm.trim() !== "" &&
      $location.pathname === "/" &&
      $floors.isSuccess &&
      $floors.data.length > 0
    ) {
      location.push("/floor/" + $floors.data[0].id + "?search");
    }
  });

  onDestroy(unsubscribeSearchTerm);
</script>

<svelte:head><title>{title}</title></svelte:head>

<header class="sticky top-0 shadow-even shadow-black z-20 bg-inherit">
  <div class="flex flex-row border-b border-b-neutral-500 items-center">
    <h1
      class="{showSearch
        ? 'truncate'
        : ''} flex-1 text-lg font-bold px-2 py-2 md:mr-4"
      tabindex="-1"
    >
      {title}
    </h1>
    <button
      on:click={focusContent}
      class="block fixed z-50 top-[-200px] focus:top-0 left-1/2 transform -translate-x-1/2 bg-neutral-600 px-10 py-2 rounded-b-lg shadow-even shadow-black"
      >Jump to content</button
    >
    {#if $isFetching > 0}
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
    <SearchBox />
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
