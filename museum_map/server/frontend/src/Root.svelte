<script lang="ts">
  import { derived } from "svelte/store";
  import { Route, NotFoundRoute } from "./simple-svelte-router";
  import { createQuery } from "@tanstack/svelte-query";

  import Lobby from "./routes/Lobby.svelte";
  import Room from "./routes/Room.svelte";
  import Loading from "./components/Loading.svelte";
  import Research from "./components/Research.svelte";
  import Reload from "./components/Reload.svelte";
  import Demographics from "./routes/Demographics.svelte";
  import NotReady from "./components/NotReady.svelte";
  import { apiRequest } from "./util";

  let Floor = null;
  import("./routes/Floor.svelte").then((module) => {
    Floor = module.default;
  });

  const apiStatus = createQuery({
    queryKey: ["/"],
    queryFn: apiRequest<APIStatus>,
    refetchInterval: 60000,
  });
</script>

<div class="bg-neutral-600 min-h-screen">
  {#if $apiStatus.isSuccess}
    {#if $apiStatus.data.ready}
      <main
        class="container mx-auto bg-neutral-700 text-white shadow-lg shadow-black font-serif tracking-default"
      >
        <Route path="/"><Lobby /></Route>
        <Route path="/floor/:fid"
          >{#if Floor !== null}<svelte:component this={Floor} />{/if}</Route
        >
        <Route path="/floor/:fid/room/:rid/*"><Room /></Route>
        <Route path="/demographics"><Demographics /></Route>
        <NotFoundRoute><Lobby /></NotFoundRoute>
      </main>
      <Research />
      {#if $apiStatus.data.version !== "1.0.1"}
        <Reload />
      {/if}
    {:else}
      <NotReady />
    {/if}
  {:else if $apiStatus.isLoading}
    <Loading />
  {:else if $apiStatus.isError}
    <p>{$apiStatus.error.message}</p>
  {/if}
</div>
