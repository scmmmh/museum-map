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
    [x: string]: string | number | string[] | boolean;
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

interface FetchObjectPayload {
    ref: JSONAPIReference;
    fetchRelationships: boolean;
}

interface FetchObjectsPayload {
    type: string;
    query?: string;
    fetchRelationships: boolean;
}

export default createStore({
    state: {
        objects: {
            rooms: {},
            floors: {},
            items: {},
            groups: {},
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
        async fetchRelationships({ state, dispatch }, payload: JSONAPIItem[]) {
            const toFetch = {} as {[x: string]: string[]}
            payload.forEach((object) => {
                if (object.relationships) {
                    Object.values(object.relationships as JSONAPIRelationships).forEach((relationship) => {
                        if ((relationship.data as JSONAPIReference[]).length) {
                            if ((relationship.data as JSONAPIReference[]).length > 0) {
                                const missingIds = (relationship.data as JSONAPIReference[]).map((ref) => {
                                    if (state.objects[ref.type][ref.id]) {
                                        return null;
                                    } else {
                                        if (!toFetch[ref.type] || toFetch[ref.type].indexOf(ref.id) < 0)  {
                                            return ref.id;
                                        } else {
                                            return null;
                                        }
                                    }
                                }).filter((id) => { return id !== null});
                                if (missingIds.length > 0) {
                                    if (toFetch[(relationship.data as JSONAPIReference[])[0].type]) {
                                        toFetch[(relationship.data as JSONAPIReference[])[0].type] = toFetch[(relationship.data as JSONAPIReference[])[0].type].concat(missingIds as string[]);
                                    } else {
                                        toFetch[(relationship.data as JSONAPIReference[])[0].type] = missingIds as string[];
                                    }
                                }
                            }
                        } else {
                            if (!state.objects[(relationship.data as JSONAPIReference).type][(relationship.data as JSONAPIReference).id]) {
                                if (!toFetch[(relationship.data as JSONAPIReference).type]) {
                                    toFetch[(relationship.data as JSONAPIReference).type] = [(relationship.data as JSONAPIReference).id]
                                } else if (toFetch[(relationship.data as JSONAPIReference).type].indexOf((relationship.data as JSONAPIReference).id) < 0) {
                                    toFetch[(relationship.data as JSONAPIReference).type].push((relationship.data as JSONAPIReference).id);
                                }
                            }
                        }
                    });
                }
            });
            Object.entries(toFetch).forEach(([type, ids]) => {
                dispatch('fetchObjects', {
                    type: type,
                    query: '?filter[id]=' + ids.join(','),
                    fetchRelationships: false,
                });
            });
        },

        async fetchObjects({ dispatch, commit }, payload: FetchObjectsPayload) {
            commit('startLoading');
            let url = '/api/' + payload.type;
            if (payload.query) {
                url = url + payload.query;
            }
            if (!payload.fetchRelationships) {
                if (url.indexOf('?') >= 0) {
                    url = url + '&relationships=false';
                } else {
                    url = url + '?relationships=false';
                }
            }
            const response = await fetch(url);
            if (response.status === 200 || response.status === 304) {
                const objects = (await response.json()).data as JSONAPIItem[];
                if (!payload.fetchRelationships) {
                    objects.forEach((obj) => {
                        if (obj.attributes) {
                            obj.attributes['_partial'] = true;
                        } else {
                            obj.attributes= {'_partial': true};
                        }
                    });
                }
                commit('storeObjects', objects);
                if (payload.fetchRelationships) {
                    dispatch('fetchRelationships', objects);
                }
                commit('completedLoading');
                return objects;
            }
            commit('completedLoading');
        },

        async fetchObject({ state, dispatch, commit }, payload: FetchObjectPayload) {
            if (state.objects[payload.ref.type] && state.objects[payload.ref.type][payload.ref.id] && (!state.objects[payload.ref.type][payload.ref.id].attributes || (!state.objects[payload.ref.type][payload.ref.id].attributes?._partial))) {
                if (payload.fetchRelationships) {
                    dispatch('fetchRelationships', [state.objects[payload.ref.type][payload.ref.id]]);
                }
                return state.objects[payload.ref.type][payload.ref.id];
            } else {
                commit('startLoading');
                let url = '/api/' + payload.ref.type + '/' + payload.ref.id;
                if (!payload.fetchRelationships) {
                    url = url + '?relationships=false';
                }
                const response = await fetch(url);
                if (response.status === 200 || response.status === 304) {
                    const object = (await response.json()).data;
                    commit('storeObject', object);
                    if (payload.fetchRelationships) {
                        dispatch('fetchRelationships', [object]);
                    }
                    commit('completedLoading');
                    return object;
                }
                commit('completedLoading');
            }
        },

        async fetchRooms({ dispatch }, payload: string[] | null) {
            const params = {
                type: 'rooms',
                fetchRelationships: true
            } as FetchObjectsPayload;
            if (payload) {
                params.query = '?filter[id]=' + payload.join(',');
            }
            return await dispatch('fetchObjects', params) as JSONAPIItem[];
        },

        async fetchRoom({ dispatch }, payload: string) {
            return await dispatch('fetchObject', {
                ref: {
                    type: 'rooms',
                    id: payload
                },
                fetchRelationships: true
            });
        },

        async fetchFloors({ dispatch }, payload: string[] | null) {
            const params = {
                type: 'floors',
                fetchRelationships: true
            } as FetchObjectsPayload;
            if (payload) {
                params.query = '?filter[id]=' + payload.join(',');
            }
            return await dispatch('fetchObjects', params) as JSONAPIItem[];
        },

        async fetchFloor({ dispatch }, payload: string) {
            return await dispatch('fetchObject', {
                ref: {
                    type: 'floors',
                    id: payload
                },
                fetchRelationships: true
            });
        },

        async fetchItems({ dispatch }, payload: string[]) {
            const params = {
                type: 'items',
                fetchRelationships: true
            } as FetchObjectsPayload;
            if (payload) {
                params.query = '?filter[id]=' + payload.join(',');
            }
            return await dispatch('fetchObjects', params);
        },

        async fetchItem({ dispatch }, payload: string) {
            const item = await dispatch('fetchObject', {
                ref: {
                    type: 'items',
                    id: payload},
                fetchRelationships: true
            });
            return item;
        },

        async fetchFloorTopics({ dispatch }, payload: string[]) {
            const params = {
                type: 'floor-topics',
                fetchRelationships: true
            } as FetchObjectsPayload;
            if (payload) {
                params.query = '?filter[id]=' + payload.join(',');
            }
            return await dispatch('fetchObjects', params) as JSONAPIItem[];
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
