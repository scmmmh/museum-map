import { writable } from "svelte/store";
import type { Subscriber } from "svelte/store";
import history from "history/hash";
import type { Location, Update } from "history";

export interface RouterLocation extends Location {
  pathComponents: string[],
};


export function createRouter() {
  const location = writable({} as RouterLocation);
  let subscriberCount = 0;

  function processLocation(newLocation: Location) {
    location.set({
      ...newLocation,
      pathComponents: newLocation.pathname.substring(1).split('/'),
    });
  }

  function update(update: Update) {
    processLocation(update.location);
  }

  function subscribe(subscriber: Subscriber<RouterLocation>) {
    let historyUnsubscribe: (() => void) | null = null;
    if (subscriberCount === 0) {
      historyUnsubscribe = history.listen(update);
      processLocation(history.location);
    }
    const locationUnsubscribe = location.subscribe(subscriber);
    subscriberCount++;

    return () => {
      locationUnsubscribe();
      subscriberCount--;
      if (subscriberCount === 0 && historyUnsubscribe !== null) {
        historyUnsubscribe();
      }
    }
  }

  return {
    subscribe,
    push: history.push,
    replace: history.replace,
  }
}

export const location = createRouter();
