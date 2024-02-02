<script lang="ts">
  import { QueryClient, QueryClientProvider } from "@tanstack/svelte-query";
  import Root from "./Root.svelte";

  import { track } from "./store";

  const queryClient = new QueryClient();

  function visibilityChange() {
    track({
      action: "visibility-change",
      params: { state: document.visibilityState },
    });
  }
</script>

<svelte:window on:visibilitychange={visibilityChange} />

<QueryClientProvider client={queryClient}>
  <Root />
</QueryClientProvider>
