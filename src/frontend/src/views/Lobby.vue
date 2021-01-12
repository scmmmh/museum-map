<template>
    <article class="lobby">
        <ol>
            <li v-for="floor in floors" :key="floor.id">
                <h2><button>{{ floor.floor.attributes.label }}</button></h2>
                <ul>
                    <li v-for="room in floor.rooms" :key="room.room.id"><router-link :to="'/room/' + room.room.id">{{ room.group.attributes.label }}</router-link></li>
                </ul>
            </li>
        </ol>
    </article>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '@/base';
import { JSONAPIItem, JSONAPIReference } from '@/store';

interface LobbyEntry {
    floor: JSONAPIItem;
    rooms: LobbyEntryRoom[];
}

interface LobbyEntryRoom {
    room: JSONAPIItem;
    group: JSONAPIItem;
}

@Options({
    components: {
    }
})
export default class Lobby extends ComponentRoot {
    public get floors() {
        if (this.$store.state.objects.floors) {
            let floors = Object.values(this.$store.state.objects.floors);
            floors = floors.sort((a, b) => {
                if (a.attributes && b.attributes) {
                    return (a.attributes.level as number) - (b.attributes.level as number);
                } else if (a.attributes) {
                    return -1;
                } else if (b.attributes) {
                    return 1;
                } else {
                    return 0;
                }
            });
            const structure = [] as LobbyEntry[];
            floors.forEach((floor) => {
                const entry = {
                    'floor': floor,
                    'rooms': []
                } as LobbyEntry;
                if (floor.relationships && floor.relationships.rooms) {
                    (floor.relationships.rooms.data as JSONAPIReference[]).forEach((ref) => {
                        if (this.$store.state.objects.rooms[ref.id]) {
                            const room = this.$store.state.objects.rooms[ref.id];
                            if (room.relationships && room.relationships.group) {
                                if (this.$store.state.objects.groups[(room.relationships.group.data as JSONAPIReference).id]) {
                                    const group = this.$store.state.objects.groups[(room.relationships.group.data as JSONAPIReference).id];
                                    entry.rooms.push({
                                        'room': room,
                                        'group': group,
                                    });
                                }
                            }
                        }
                    });
                }
                if (entry.rooms.length > 0) {
                    structure.push(entry);
                }
            });
            return structure;
        }
        return [];
    }
}
</script>
