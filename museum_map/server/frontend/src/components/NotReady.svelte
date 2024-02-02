<script lang="ts">
  import { fade } from "svelte/transition";
</script>

<svelte:head>
  <title>The Museum Map is currently not available</title>
</svelte:head>

<div
  transition:fade
  class="fixed left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 max-w-full p-4 bg-neutral-700 text-white shadow-2xl rounded-2xl"
  role="alert"
>
  <p class="mb-2">Unfortuantely the Museum Map is currently not available.</p>
  <p>
    When the Museum Map becomes available, the interface will load
    automatically.
  </p>
</div>
