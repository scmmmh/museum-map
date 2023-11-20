<script lang="ts">
  import { onDestroy, tick } from "svelte";
  import { location } from "./store";

  export let path: string;
  export let handleFocus: boolean = true;

  let routeName: string = location.registerRoute(path);
  let matches = false;
  let startMarker: HTMLElement | null = null;
  let endMarker: HTMLElement | null = null;

  /**
   * Focus on the first hX element we find
   */
  function focusElement() {
    if (startMarker && endMarker) {
      let element = startMarker.nextElementSibling as HTMLElement;
      let found = false;
      while (element !== null && element !== endMarker) {
        const heading = element.querySelector("h1,h2,h3,h4,h5,h6");
        if (heading !== null) {
          (heading as HTMLElement).focus();
          found = true;
          break;
        }
        element = element.nextElementSibling as HTMLElement;
      }
      if (!found) {
        console.error("No heading found for post-navigation focus");
      }
    }
  }

  /**
   * Process a location change.
   *
   * First check for matches and if there is one, then call the focus handling.
   */
  const locationUnsubscribe = location.subscribe((location) => {
    matches = location.currentRoute === routeName;
    if (handleFocus && matches) {
      tick().then(focusElement);
    }
  });

  onDestroy(() => {
    locationUnsubscribe();
    location.unRegisterRoute(routeName);
  });
</script>

{#if matches}
  <div bind:this={startMarker} />
  <slot />
  <div bind:this={endMarker} />
{/if}
