<script setup lang="ts">
import type { DetectedObject } from '../types/api'

defineProps<{
  imageUrl: string
  objects: DetectedObject[]
  loading: boolean
}>()

function boxStyle(bbox: [number, number, number, number]) {
  const [x1, y1, x2, y2] = bbox
  return {
    left: `${x1 * 100}%`,
    top: `${y1 * 100}%`,
    width: `${(x2 - x1) * 100}%`,
    height: `${(y2 - y1) * 100}%`,
  }
}
</script>

<template>
  <div class="image-stage">
    <img :src="imageUrl" alt="待分析场景" />
    <div
      v-for="item in objects"
      :key="item.id"
      class="bbox"
      :style="boxStyle(item.bbox)"
    >
      <span>{{ item.display_name }} {{ Math.round(item.confidence * 100) }}%</span>
    </div>
    <div v-if="loading" class="scan-line"></div>
    <div v-if="loading" class="analyzing-overlay">
      <strong>正在构建空间表征</strong>
      <small>读取图像 · 定位物体 · 生成结构化结果</small>
    </div>
  </div>
</template>
