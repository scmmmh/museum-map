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
}

interface FetchObjectsPayload {
    type: string;
    query?: string;
}

export default createStore({
    state: {
        objects: {
            rooms: {},
            groups: {},
            floors: {},
            items: {},
        },
        ui: {
            loadingCount: 0,
        }
    } as State,

    mutations: {
        storeObject(state, payload: JSONAPIItem) {
            state.objects[payload.type][payload.id] = payload;
        },

        setItems(state, payload: JSONAPIItem[]) {
            const items = {} as JSONAPISet;
            payload.forEach((item) => {
                if (item.attributes && item.attributes.images && (item.attributes.images as string[]).length > 0)  {
                    items[item.id] = item;
                }
            });
            state.objects.items = items;
        },

        startLoading(state) {
            state.ui.loadingCount = state.ui.loadingCount + 1;
        },

        completedLoading(state) {
            state.ui.loadingCount = state.ui.loadingCount - 1;
        }
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
                objects.forEach((object: JSONAPIItem) => {
                    commit('storeObject', object);
                });
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

        async fetchRooms({ dispatch }, payload: string[] | null) {
            const params = {type: 'rooms'} as FetchObjectsPayload;
            if (payload) {
                params.query = '?filter[id]=' + payload.join(',');
            }
            const rooms = await dispatch('fetchObjects', params);
            const groupIds = [] as string[];
            rooms.forEach((room: JSONAPIItem) => {
                if (room.relationships && room.relationships.group) {
                    groupIds.push((room.relationships.group.data as JSONAPIReference).id);
                }
            });
            await dispatch('fetchGroups', groupIds);
            return rooms;
        },

        async fetchRoom({ state, dispatch }, payload: string) {
            if (!state.objects.rooms[payload]) {
                const room = await dispatch('fetchObject', {type: 'rooms', id: payload});
                if (room.relationships) {
                    const promises = [
                        dispatch('fetchGroup', room.relationships.group.data.id),
                        dispatch('fetchFloor', room.relationships.floor.data.id)
                    ];
                    await Promise.all(promises);
                }
                return room;
            } else {
                return state.objects.rooms[payload];
            }
        },

        async fetchGroups({ dispatch }, payload: string[] | null) {
            const params = {type: 'groups'} as FetchObjectsPayload;
            if (payload) {
                params.query = '?filter[id]=' + payload.join(',');
            }
            return await dispatch('fetchObjects', params);
        },

        async fetchGroup({ state, dispatch }, payload: string) {
            if (!state.objects.groups[payload]) {
                const group = await dispatch('fetchObject', {type: 'groups', id: payload});
                return group;
            } else {
                return state.objects.groups[payload];
            }
        },

        async fetchFloors({ dispatch }, payload: string[] | null) {
            const params = {type: 'floors'} as FetchObjectsPayload;
            if (payload) {
                params.query = '?filter[id]=' + payload.join(',');
            }
            const floors = await dispatch('fetchObjects', params);
            const roomIds = [] as string[];
            floors.forEach((floor: JSONAPIItem) => {
                if (floor.relationships && floor.relationships.rooms) {
                    (floor.relationships.rooms.data as JSONAPIReference[]).forEach((ref) => {
                        roomIds.push(ref.id);
                    })
                }
            });
            await dispatch('fetchRooms', roomIds);
            return floors;
        },

        async fetchFloor({ state, dispatch }, payload: string) {
            if (!state.objects.floors[payload]) {
                const floor = await dispatch('fetchObject', {type: 'floors', id: payload});
                return floor;
            } else {
                return state.objects.floors[payload];
            }
        },

        async fetchRoomItems({ dispatch, commit }, payload: string) {
            commit('setItems', []);
            const room = await dispatch('fetchRoom', payload);
            const group = await dispatch('fetchGroup', room.relationships.group.data.id);
            const itemIds = (group.relationships.items.data as JSONAPIReference[]).map((ref) => {
                return ref.id;
            });
            const response = await fetch('/api/items?filter[id]=' + itemIds.join(','));
            const items = (await response.json()).data;
            commit('setItems', items);
        },

        async fetchItem({ state, dispatch }, payload: string) {
            if (!state.objects.items[payload]) {
                const item = await dispatch('fetchObject', {type: 'items', id: payload});
                return item;
            } else {
                return state.objects.items[payload];
            }
        },
    },
    modules: {
    }
});
