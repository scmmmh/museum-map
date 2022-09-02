<script lang="ts">
    import { Router, Route } from 'svelte-navigator';

    import Lobby from './Lobby.svelte';
    import Floor from './Floor.svelte';
    import Room from './Room.svelte';
</script>

<Router>
    <Route path="/"><Lobby/></Route>
    <Route path="/floor/:id"><Floor/></Route>
    <Route path="/room/:id/*"><Room/></Route>
</Router>
