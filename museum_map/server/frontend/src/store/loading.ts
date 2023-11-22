import { derived } from "svelte/store";

import { floors, floorTopics } from "./floors";
import { config } from "./config";

export const loadingProgress = derived([floors, floorTopics, config], (dependencies) => {
    return 100 / 3 * dependencies.filter((dep) => { return dep !== null }).length;
});

export const isLoaded = derived(loadingProgress, (progress) => {
    return progress === 100;
})
