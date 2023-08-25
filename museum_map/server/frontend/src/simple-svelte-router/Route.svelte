<script lang="ts">
  import { onDestroy } from "svelte";
  import { location } from "./store";
  import type { RouterLocation } from "./store";

  export let path: string;
  let pathComponents = [];
  let matches = false;

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

  $: {
    pathComponents = path.substring(1).split("/");
    checkMatch($location);
  }

  const locationUnsubscribe = location.subscribe((location) => {
    checkMatch(location);
  });

  onDestroy(locationUnsubscribe);
</script>

{#if matches}
  <slot />
{/if}
