import { createRouter, createWebHistory } from 'vue-router'

import AnalyzeView from '../views/AnalyzeView.vue'
import HomeView from '../views/HomeView.vue'
import MemoryView from '../views/MemoryView.vue'
import MemoryDetailView from '../views/MemoryDetailView.vue'
import AgentView from '../views/AgentView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/analyze', name: 'analyze', component: AnalyzeView },
    { path: '/memory', name: 'memory', component: MemoryView },
    { path: '/memory/:id', name: 'memory-detail', component: MemoryDetailView },
    { path: '/agent', name: 'agent', component: AgentView },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
