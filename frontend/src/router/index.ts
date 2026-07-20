import { createRouter, createWebHistory } from 'vue-router'

import AnalyzeView from '../views/AnalyzeView.vue'
import HomeView from '../views/HomeView.vue'
import MemoryView from '../views/MemoryView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/analyze', name: 'analyze', component: AnalyzeView },
    { path: '/memory', name: 'memory', component: MemoryView },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
