<script setup lang="ts">
import {
  PhAtom,
  PhBrain,
  PhCamera,
  PhCaretDoubleLeft,
  PhCaretDoubleRight,
  PhChartLineUp,
  PhClockCounterClockwise,
  PhDevices,
  PhHouse,
  PhImageSquare,
  PhPulse,
  PhSparkle,
  PhUserCircle,
} from '@phosphor-icons/vue'

defineProps<{ expanded: boolean }>()
defineEmits<{ toggle: [] }>()

const primaryItems = [
  { to: '/', label: '首页', caption: '记忆中枢', icon: PhHouse },
  { to: '/live', label: '实时镜头', caption: 'Live Lens', icon: PhCamera },
  { to: '/analyze', label: '场景分析', caption: '空间理解', icon: PhImageSquare },
  { to: '/memory', label: '空间记忆', caption: '证据时间线', icon: PhBrain },
  { to: '/agent', label: 'Agent', caption: '证据问答', icon: PhSparkle },
  { to: '/sessions', label: '观察会话', caption: '连续采集', icon: PhClockCounterClockwise },
  { to: '/devices', label: '设备中心', caption: '感知端口', icon: PhDevices },
  { to: '/insights', label: '洞察', caption: '真实统计', icon: PhChartLineUp },
  { to: '/me', label: '我的', caption: '设置与隐私', icon: PhUserCircle },
]
</script>

<template>
  <aside class="spatial-rail" :class="{ expanded }" aria-label="SceneMind 主导航">
    <RouterLink class="rail-brand" to="/" aria-label="SceneMind 首页">
      <span class="rail-brand-mark"><PhAtom :size="24" weight="duotone" /></span>
      <span class="rail-brand-copy"><strong>SceneMind</strong><small>SPATIAL OS</small></span>
    </RouterLink>

    <nav class="rail-navigation">
      <RouterLink v-for="item in primaryItems" :key="item.to" :to="item.to" :aria-label="item.label">
        <component :is="item.icon" :size="21" weight="duotone" aria-hidden="true" />
        <span><strong>{{ item.label }}</strong><small>{{ item.caption }}</small></span>
      </RouterLink>
    </nav>

    <div class="rail-footer">
      <RouterLink to="/system" aria-label="系统状态">
        <PhPulse :size="21" weight="duotone" aria-hidden="true" />
        <span><strong>系统状态</strong><small>v0.9.0-rc1</small></span>
      </RouterLink>
      <button type="button" :aria-label="expanded ? '收起导航' : '展开导航'" @click="$emit('toggle')">
        <PhCaretDoubleLeft v-if="expanded" :size="18" aria-hidden="true" />
        <PhCaretDoubleRight v-else :size="18" aria-hidden="true" />
        <span>{{ expanded ? '收起' : '展开' }}</span>
      </button>
    </div>
  </aside>
</template>
