import { createStore } from 'vuex';

export const NOT_READY = 0;
export const BUSY = 1;
export const READY = 2;

interface State {
    objects: JSONAPIStore;
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
    [x: string]: string;
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

export default createStore({
    state: {
        objects: {
            rooms: {},
            groups: {},
            floors: {},
            items: {},
        }
    } as State,

    mutations: {
        storeObject(state, payload: JSONAPIItem) {
            state.objects[payload.type][payload.id] = payload;
        },

        setItems(state, payload: JSONAPIItem[]) {
            const items = {} as JSONAPISet;
            payload.forEach((item) => {
                if (item.attributes && item.attributes.images && item.attributes.images.length > 0)  {
                    items[item.id] = item;
                }
            });
            state.objects.items = items;
        }
    },

    actions: {
        //async init({ dispatch }) {
            //dispatch('connect');
        //},

        async fetchObject({ state, commit }, payload: JSONAPIReference) {
            if (state.objects[payload.type] && state.objects[payload.type][payload.id]) {
                return state.objects[payload.type][payload.id];
            } else {
                const response = await fetch('/api/' + payload.type + '/' + payload.id);
                if (response.status === 200 || response.status === 304) {
                    const object = (await response.json()).data;
                    commit('storeObject', object);
                    return object;
                }
            }
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

        async fetchGroup({ state, dispatch }, payload: string) {
            if (!state.objects.groups[payload]) {
                const group = await dispatch('fetchObject', {type: 'groups', id: payload});
                return group;
            } else {
                return state.objects.groups[payload];
            }
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
            const room = await dispatch('fetchRoom', payload);
            const group = await dispatch('fetchGroup', room.relationships.group.data.id);
            const itemIds = (group.relationships.items.data as JSONAPIReference[]).map((ref) => {
                return ref.id;
            });
            const response = await fetch('/api/items?filter[id]=' + itemIds.join(','));
            const items = (await response.json()).data;
            commit('setItems', items);
        },
    },
    modules: {
    }
});
