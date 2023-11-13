import { derived } from "svelte/store";

import { floors, floorTopics } from "./floors";

export const loadingProgress = derived([floors, floorTopics], (dependencies) => {
    return 100 / 2 * dependencies.filter((dep) => { return dep !== null}).length;
});

export const isLoaded = derived(loadingProgress, (progress) => {
    return progress === 100;
})
