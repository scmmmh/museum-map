import { derived } from "svelte/store";
import { consent, ageBand } from "./consent";
import { location } from "../simple-svelte-router";

function createTracker() {
    let localAllowTracking = false;

    const allowTracking = derived([consent, ageBand], ([consent, ageBand]) => {
        localAllowTracking = consent === true && Number.parseInt(ageBand) > 0;
        return localAllowTracking;
    });

    async function log(action: LogAction) {
        if (localAllowTracking) {
            await window.fetch('/api/tracking/track', {
                method: 'POST',
                body: JSON.stringify({
                    timestamp: Date.now() / 1000,
                    action: action
                }),
            });
        }
    }

    return {
        subscribe: allowTracking.subscribe,
        log,
    }
}

export const tracker = createTracker();

location.subscribe((location) => {
    tracker.log({ action: "navigate", params: location });
});
