import { writable } from 'svelte/store';

export interface NestedStorage {
    [x: string]: null | string | number | boolean | NestedStorage | string[];
}

function storeValue(storage: Storage, path: string, value: null | string | number | boolean | NestedStorage | string[]): NestedStorage {
    let obj = {} as NestedStorage;
    const data = storage.getItem('mmap:storage');
    if (data) {
        obj = JSON.parse(data);
    }
    const pathElements = path.split('.');
    let current = obj;
    for (let idx = 0; idx < pathElements.length; idx++) {
        const element = pathElements[idx];
        if (idx === pathElements.length - 1) {
            current[element] = value;
        } else {
            if (!current[element]) {
                current[element] = {};
            }
            current = current[element] as NestedStorage;
        }
    }
    storage.setItem('mmap:storage', JSON.stringify(obj));
    return obj;
}

function loadValue(storage: Storage, path: string, defaultValue: null | string | number | boolean | NestedStorage | string[]): null | string | number | boolean | NestedStorage | string[] {
    const data = storage.getItem('mmap:storage');
    if (data) {
        const obj = JSON.parse(data) as NestedStorage;
        const pathElements = path.split('.');
        let current = obj;
        for (let idx = 0; idx < pathElements.length; idx++) {
            const element = pathElements[idx];
            if (idx === pathElements.length - 1) {
                if (current[element] !== undefined) {
                    return current[element];
                } else {
                    return defaultValue;
                }
            } else {
                if (current[element]) {
                    current = current[element] as NestedStorage;
                } else {
                    return defaultValue;
                }
            }
        }
    }
    return defaultValue;
}

function deleteValue(storage: Storage, path: string): NestedStorage {
    let obj = {} as NestedStorage;
    const data = storage.getItem('mmap:storage');
    if (data) {
        obj = JSON.parse(data);
    }
    const pathElements = path.split('.');
    let current = obj;
    for (let idx = 0; idx < pathElements.length; idx++) {
        const element = pathElements[idx];
        if (idx === pathElements.length - 1) {
            delete current[element];
        } else {
            if (!current[element]) {
                break;
            }
            current = current[element] as NestedStorage;
        }
    }
    storage.setItem('mmap:storage', JSON.stringify(obj));
    return obj;
}

function createPreferencesStore(storage: Storage) {
    const { subscribe, set } = writable(loadValue(storage, 'preferences', {}) as NestedStorage);

    return {
        subscribe,
        setPreference(path: string, value: null | string | number | boolean | NestedStorage | string[]) {
            const updated = storeValue(storage, 'preferences.' + path, value);
            set((updated as NestedStorage).preferences as NestedStorage);
        },
        deletePreference(path: string) {
            const updated = deleteValue(storage, 'preferences.' + path);
            set((updated as NestedStorage).preferences as NestedStorage);
        },
    }
}

export const localPreferences = createPreferencesStore(localStorage);

export const sessionPreferences = createPreferencesStore(sessionStorage);
