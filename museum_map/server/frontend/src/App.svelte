<script lang="ts">
  import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query'
  import Root from "./Root.svelte";

  const queryClient = new QueryClient()
</script>

<QueryClientProvider client={queryClient}>
  <Root />
</QueryClientProvider>
