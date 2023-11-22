import { writable } from "svelte/store";
import type { Subscriber } from "svelte/store";
import history from "history/hash";
import type { Location, Update } from "history";

export interface RouterLocation extends Location {
  currentRoute: string | null,
  matchingRoutes: string[],
  pathComponents: { [x: string]: string },
};

type RoutePattern = {
  name: string,
  pattern: RegExp,
  length: number,
};

/**
 * Constructs a new router store.
 *
 * @returns A new router store
 */
export function createRouter() {
  const location = writable({} as RouterLocation);
  let subscriberCount = 0;
  let routeCounter = 0;
  let routePatterns: RoutePattern[] = []

  /**
   * Process a location, matching it against routes.
   *
   * @param newLocation The new location
   */
  function processLocation(newLocation: Location) {
    let pathComponents = {};
    let currentRoute = null;
    const matchingRoutes = [];
    for (let pattern of routePatterns) {
      const match = newLocation.pathname.match(pattern.pattern);
      if (match !== null) {
        if (match.groups !== undefined) {
          pathComponents = { ...pathComponents, ...match.groups };
        }
        if (currentRoute === null) {
          currentRoute = pattern.name;
        }
        matchingRoutes.push(pattern.name);
      }
    }
    location.set({
      ...newLocation,
      pathComponents,
      matchingRoutes,
      currentRoute,
    });
  }

  /**
   * Callback for the history object.
   *
   * @param update The updated location
   */
  function update(update: Update) {
    processLocation(update.location);
  }

  /**
   * Subscribe to the location changes.
   *
   * @param subscriber The subscriber callback
   * @returns An unsubscription function
   */
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

  /**
   * Register a new route.
   *
   * Used when a route component is mounted.
   *
   * @param path The path that matches the route
   * @returns The new route's unique name
   */
  function registerRoute(path: string): string {
    routeCounter++;
    const routeName = "route-" + routeCounter;
    const regex = new RegExp("^" + path.replace(/:([^\/]+)/g, "(?<$1>[^/]+)").replace(/\/\*/, "\/?.*") + "$");
    let length = 0;
    for (let idx = 0; idx < path.length; idx++) {
      if (path.charAt(idx) === "/") {
        length++;
      }
    }
    routePatterns.push({
      name: routeName,
      pattern: regex,
      length,
    });
    routePatterns.sort((a, b) => {
      return b.length - a.length;
    });
    processLocation(history.location);
    return routeName
  }

  /**
   * Unregister a route.
   *
   * Used when a Route component is unmounted.
   *
   * @param routeName The name of the route to unregister
   */
  function unRegisterRoute(routeName: string): void {
    routePatterns = routePatterns.filter((pattern) => {
      return pattern.name !== routeName;
    });
    processLocation(history.location);
  }

  return {
    subscribe,
    push: history.push,
    replace: history.replace,

    registerRoute,
    unRegisterRoute,
  }
}

export const location = createRouter();
