<script lang="ts">
  import { onDestroy, tick } from "svelte";
  import { location } from "./store";
  import type { RouterLocation } from "./store";

  export let path: string;
  let pathComponents: string[] = [];
  let matches = false;
  let startMarker: HTMLElement | null = null;
  let endMarker: HTMLElement | null = null;

  /**
   * Focus on the first hX element we find
   */
  function focusElement() {
    console.log(startMarker, endMarker);
    if (startMarker && endMarker) {
      let element = startMarker.nextElementSibling as HTMLElement;
      let found = false;
      while (element !== null && element !== endMarker) {
        console.log(element);
        const heading = element.querySelector("h1,h2,h3,h4,h5,h6");
        if (heading !== null) {
          (heading as HTMLElement).setAttribute("tabindex", "-1");
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
   * Check if the current location matches the path for this Route
   *
   * @param location The current location
   */
  function checkMatch(location: RouterLocation) {
    matches = true;
    for (let idx = 0; idx < pathComponents.length; idx++) {
      if (idx < location.pathComponents.length) {
        if (pathComponents[idx] === "*") {
          continue;
        } else if (pathComponents[idx].startsWith(":")) {
          continue;
        } else if (pathComponents[idx] === location.pathComponents[idx]) {
          continue;
        } else {
          matches = false;
          break;
        }
      } else {
        matches = false;
        break;
      }
    }
  }

  /**
   * Process a location change.
   *
   * First check for matches and if there is one, then call the focus handling.
   *
   * @param location The current location
   */
  function process(location: RouterLocation) {
    const oldMatches = matches;
    checkMatch(location);
    if (!oldMatches && matches) {
      tick().then(focusElement);
    }
  }

  $: {
    pathComponents = path.substring(1).split("/");
    process($location);
  }

  const locationUnsubscribe = location.subscribe((location) => {
    process(location);
  });

  onDestroy(locationUnsubscribe);
</script>

{#if matches}
  <div bind:this={startMarker} />
  <slot />
  <div bind:this={endMarker} />
{/if}
