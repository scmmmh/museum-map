import { derived } from "svelte/store";

import { floors } from "./floors";

export const loadingProgress = derived(floors, (floors) => {
    if (floors !== null) {
        return 100;
    } else {
        return 0;
    }
});

export const isLoaded = derived(loadingProgress, (progress) => {
    return progress === 100;
})
