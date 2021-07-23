import { createStore } from 'vuex';

export const NOT_READY = 0;
export const BUSY = 1;
export const READY = 2;

interface State {
    objects: JSONAPIStore;
    ui: UIState;
}

interface JSONAPIStore {
    [x: string]: JSONAPISet;
}

interface JSONAPISet {
    [x: string]: JSONAPIItem;
}

export interface JSONAPIItem {
    type: string;
    id: string;
    attributes?: JSONAPIAttributes;
    relationships?: JSONAPIRelationships;
}

interface JSONAPIAttributes {
    [x: string]: string | number | string[];
}

interface JSONAPIRelationships {
    [x: string]: JSONAPIRelationship;
}

interface JSONAPIRelationship {
    data: JSONAPIReference | JSONAPIReference[];
}

export interface JSONAPIReference {
    type: string;
    id: string;
}

interface UIState {
    loadingCount: number;
    mapFloorId: string | null;
}

interface FetchObjectsPayload {
    type: string;
    query?: string;
}

function getMissingIds(state: State, relationship: JSONAPIReference[]) {
    return relationship.map((ref) => {
        if (state.objects[ref.type][ref.id]) {
            return null;
        } else {
            return ref.id;
        }
    }).filter((id) => { return id !== null; });
}

export default createStore({
    state: {
        objects: {
            rooms: {},
            floors: {},
            items: {},
            'floor-topics': {},
        },
        ui: {
            loadingCount: 0,
            mapFloorId: null,
        }
    } as State,

    mutations: {
        storeObject(state, payload: JSONAPIItem) {
            state.objects[payload.type][payload.id] = payload;
        },

        storeObjects(state, payload: JSONAPIItem[]) {
            payload.forEach((object) => {
                state.objects[object.type][object.id] = object;
            });
        },

        startLoading(state) {
            state.ui.loadingCount = state.ui.loadingCount + 1;
        },

        completedLoading(state) {
            state.ui.loadingCount = state.ui.loadingCount - 1;
        },

        setMapFloorId(state, payload: string | null) {
            state.ui.mapFloorId = payload;
        },
    },

    actions: {
        async fetchObjects({ commit }, payload: FetchObjectsPayload) {
            commit('startLoading');
            let url = '/api/' + payload.type;
            if (payload.query) {
                url = url + payload.query;
            }
            const response = await fetch(url);
            if (response.status === 200 || response.status === 304) {
                const objects = (await response.json()).data;
                commit('storeObjects', objects);
                commit('completedLoading');
                return objects;
            }
            commit('completedLoading');
        },

        async fetchObject({ state, commit }, payload: JSONAPIReference) {
            if (state.objects[payload.type] && state.objects[payload.type][payload.id]) {
                return state.objects[payload.type][payload.id];
            } else {
                commit('startLoading');
                const response = await fetch('/api/' + payload.type + '/' + payload.id);
                if (response.status === 200 || response.status === 304) {
                    const object = (await response.json()).data;
                    commit('storeObject', object);
                    commit('completedLoading');
                    return object;
                }
                commit('completedLoading');
            }
        },

        async fetchRooms({ state, dispatch }, payload: string[] | null) {
            const params = {type: 'rooms'} as FetchObjectsPayload;
            if (payload) {
                params.query = '?filter[id]=' + payload.join(',');
            }
            const rooms = await dispatch('fetchObjects', params) as JSONAPIItem[];
            let missingIds = rooms.map((room) => {
                if (room.relationships) {
                    if (!state.objects.items[(room.relationships.sample.data as JSONAPIReference).id]) {
                        return (room.relationships.sample.data as JSONAPIReference).id;
                    }
                }
                return null;
            }).filter((id) => { return id !== null; });
            if (missingIds.length > 0) {
                dispatch('fetchItems', missingIds);
            }
            missingIds = rooms.map((room) => {
                if (room.relationships) {
                    if (!state.objects.floors[(room.relationships.floor.data as JSONAPIReference).id]) {
                        return (room.relationships.floor.data as JSONAPIReference).id;
                    }
                }
                return null;
            }).filter((id) => { return id !== null; });
            if (missingIds.length > 0) {
                dispatch('fetchFloors', missingIds);
            }
            return rooms;
        },

        async fetchRoom({ state, dispatch }, payload: string) {
            if (!state.objects.rooms[payload]) {
                const room = await dispatch('fetchObject', {type: 'rooms', id: payload});
                if (room.relationships) {
                    if (!state.objects.floors[(room.relationships.floor.data as JSONAPIReference).id]) {
                        dispatch('fetchFloor', (room.relationships.floor.data as JSONAPIReference).id);
                    }
                    if (!state.objects.items[(room.relationships.sample.data as JSONAPIReference).id]) {
                        dispatch('fetchItem', (room.relationships.sample.data as JSONAPIReference).id);
                    }
                }
                return room;
            } else {
                return state.objects.rooms[payload];
            }
        },

        async fetchFloors({ state, dispatch }, payload: string[] | null) {
            const params = {type: 'floors'} as FetchObjectsPayload;
            if (payload) {
                params.query = '?filter[id]=' + payload.join(',');
            }
            const floors = await dispatch('fetchObjects', params) as JSONAPIItem[];
            floors.forEach((floor) => {
                if (floor.relationships) {
                    let missingIds = getMissingIds(state, floor.relationships.rooms.data as JSONAPIReference[])
                    if (missingIds.length > 0) {
                        dispatch('fetchRooms', missingIds);
                    }
                    missingIds = getMissingIds(state, floor.relationships.samples.data as JSONAPIReference[])
                    if (missingIds.length > 0) {
                        dispatch('fetchItems', missingIds);
                    }
                    missingIds = getMissingIds(state, floor.relationships.topics.data as JSONAPIReference[])
                    if (missingIds.length > 0) {
                        dispatch('fetchFloorTopics', missingIds);
                    }
                }
            })
            return floors;
        },

        async fetchFloor({ state, dispatch }, payload: string) {
            if (!state.objects.floors[payload]) {
                const floor = await dispatch('fetchObject', {type: 'floors', id: payload});
                if (floor.relationships) {
                    let missingIds = getMissingIds(state, floor.relationships.rooms.data as JSONAPIReference[])
                    if (missingIds.length > 0) {
                        dispatch('fetchRooms', missingIds);
                    }
                    missingIds = getMissingIds(state, floor.relationships.samples.data as JSONAPIReference[])
                    if (missingIds.length > 0) {
                        dispatch('fetchItems', missingIds);
                    }
                    missingIds = getMissingIds(state, floor.relationships.topics.data as JSONAPIReference[])
                    if (missingIds.length > 0) {
                        dispatch('fetchFloorTopics', missingIds);
                    }
                }
                return floor;
            } else {
                return state.objects.floors[payload];
            }
        },

        async fetchItems({ dispatch }, payload: string[]) {
            const params = {type: 'items'} as FetchObjectsPayload;
            if (payload) {
                params.query = '?filter[id]=' + payload.join(',');
            }
            return await dispatch('fetchObjects', params);
        },

        async fetchItem({ state, dispatch }, payload: string) {
            if (!state.objects.items[payload]) {
                const item = await dispatch('fetchObject', {type: 'items', id: payload});
                return item;
            } else {
                return state.objects.items[payload];
            }
        },

        async fetchFloorTopics({ dispatch }, payload: string[]) {
            const params = {type: 'floor-topics'} as FetchObjectsPayload;
            if (payload) {
                params.query = '?filter[id]=' + payload.join(',');
            }
            return await dispatch('fetchObjects', params);
        },

        async fetchItemPicks({ commit }, payload: string) {
            commit('startLoading');
            const url = '/api/picks/' + payload;
            const response = await fetch(url);
            if (response.status === 200 || response.status === 304) {
                const objects = (await response.json()).data;
                objects.forEach((object: JSONAPIItem) => {
                    commit('storeObject', object);
                });
                commit('completedLoading');
                return objects;
            }
            commit('completedLoading');
        },
    },
    modules: {
    }
});
