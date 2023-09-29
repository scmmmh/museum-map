import { writable, derived, get } from "svelte/store";
import { localPreferences, type NestedStorage } from "./preferences";

const prefs = get(localPreferences);

export const consent = writable(prefs.tracking && (prefs.tracking as NestedStorage).consent === true);

export const ageBand = writable(prefs.tracking && (prefs.tracking as NestedStorage).ageBand as string || "0");

export const trackingAllowed = derived([consent, ageBand], ([consent, ageBand]) => {
    return consent && Number.parseInt(ageBand) > 0;
});
