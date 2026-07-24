import { createRouter, createWebHistory } from 'vue-router'

import AnalyzeView from '../views/AnalyzeView.vue'
import HomeView from '../views/HomeView.vue'
import MemoryView from '../views/MemoryView.vue'
import MemoryDetailView from '../views/MemoryDetailView.vue'
import AgentView from '../views/AgentView.vue'
import LiveView from '../views/LiveView.vue'
import SessionsView from '../views/SessionsView.vue'
import SessionDetailView from '../views/SessionDetailView.vue'
import DevicesView from '../views/DevicesView.vue'
import GlassesView from '../views/GlassesView.vue'
import InsightsView from '../views/InsightsView.vue'
import PrivacyView from '../views/PrivacyView.vue'
import MeView from '../views/MeView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/analyze', name: 'analyze', component: AnalyzeView },
    { path: '/memory', name: 'memory', component: MemoryView },
    { path: '/memory/:id', name: 'memory-detail', component: MemoryDetailView },
    { path: '/agent', name: 'agent', component: AgentView },
    { path: '/live', name: 'live', component: LiveView },
    { path: '/sessions', name: 'sessions', component: SessionsView },
    { path: '/sessions/:id', name: 'session-detail', component: SessionDetailView },
    { path: '/devices', name: 'devices', component: DevicesView },
    { path: '/glasses', name: 'glasses', component: GlassesView },
    { path: '/insights', name: 'insights', component: InsightsView },
    { path: '/privacy', name: 'privacy', component: PrivacyView },
    { path: '/me', name: 'me', component: MeView },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
