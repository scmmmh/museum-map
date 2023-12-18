import { writable, derived, get } from "svelte/store";
import { location } from "../simple-svelte-router";

import { localPreferences, type NestedStorage } from "./preferences";

const prefs = get(localPreferences);
let localAllowTracking = false;

export const consent = writable((prefs.tracking && (prefs.tracking as NestedStorage).consent === true) || false);

export const ageBand = writable(prefs.tracking && (prefs.tracking as NestedStorage).ageBand as string || "0");

export const trackingAllowed = derived([consent, ageBand], ([consent, ageBand]) => {
  localAllowTracking = consent && Number.parseInt(ageBand) > 0;
  if (localAllowTracking) {
    track({ action: "ready", params: { userAgent: navigator.userAgent } })
  } else {
    window.fetch("/api/tracking/" + userId, {
      method: "DELETE",
    });
    localPreferences.deletePreference("tracking.userId");
    userId = null;
  }
  return localAllowTracking;
});

let trackLog: TrackEntry[] = [];
let trackTimeout = -1;
let userId = prefs.tracking && (prefs.tracking as NestedStorage).userId as string || null;
let gettingUserId = false;

/**
 * Log a single action.
 *
 * @param action The action to log
 */
export function track(action: LogAction) {
  if (localAllowTracking) {
    trackLog.push({ timestamp: Date.now() / 1000, ...action });
    window.clearTimeout(trackTimeout);
    if (userId !== null) {
      trackTimeout = window.setTimeout(sendTracking, 1000);
    } else if (gettingUserId === false) {
      gettingUserId = true;
      window.fetch("/api/tracking/register", {
        method: "POST",
      }).then((response) => {
        if (response.ok) {
          response.json().then((user: User) => {
            userId = user.id;
            localPreferences.setPreference("tracking.userId", user.id);
            trackTimeout = window.setTimeout(sendTracking, 1000);
          });
        }
        gettingUserId = false;
      });
    }
  }
}

/**
 * Send the tracking data to the server and exit.
 */
function sendTracking() {
  async () => {
    window.fetch('/api/tracking/track/' + userId, {
      method: 'POST',
      body: JSON.stringify(trackLog),
      headers: { 'Content-Type': 'application/json' },
      keepalive: true,
    });
    trackLog = [];
  }
}

/**
 * Listen to visibilitychange events and send tracking data when hiding.
 */
window.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden") {
    window.clearTimeout(trackTimeout);
    sendTracking();
  }
})

location.subscribe((location) => {
  track({ action: "navigate", params: location });
});
