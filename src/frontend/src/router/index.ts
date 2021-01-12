import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'
const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        name: 'lobby',
        component: () => import(/* webpackChunkName: "lobby" */ '../views/Lobby.vue')
    },
    {
        path: '/room/:rid',
        name: 'room',
        component: () => import(/* webpackChunkName: "room" */ '../views/Room.vue'),
        props: true,
    },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

export default router;
