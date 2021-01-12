import { Vue } from 'vue-class-component';
import { Router } from 'vue-router';

import store from '@/store';

export class ComponentRoot extends Vue {
    $router!: Router;
    $store!: typeof store;
}
