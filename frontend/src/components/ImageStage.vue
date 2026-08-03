<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import type { DetectedObject } from '../types/api'
import { buildObjectDisplayNameMap, objectDisplayName } from '../utils/objectDisplayNames'

const props = defineProps<{
  imageUrl: string
  objects: DetectedObject[]
  loading: boolean
}>()

const objectNames = computed(() => buildObjectDisplayNameMap(props.objects))
const imageFailed = ref(false)
watch(() => props.imageUrl, () => { imageFailed.value = false })

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
    <img v-if="!imageFailed" :src="imageUrl" alt="待分析场景" @error="imageFailed = true" />
    <div v-else class="image-stage-fallback" role="img" aria-label="场景图片加载失败"><strong>图片证据暂不可用</strong><small>请检查后端图片存储后重试。</small></div>
    <div
      v-for="item in imageFailed ? [] : objects"
      :key="item.id"
      class="bbox"
      :style="boxStyle(item.bbox)"
    >
      <span>{{ objectDisplayName(objectNames, item.id) }} {{ Math.round(item.confidence * 100) }}%</span>
    </div>
    <div v-if="loading" class="scan-line"></div>
    <div v-if="loading" class="analyzing-overlay">
      <strong>正在构建空间表征</strong>
      <small>读取图像 · 定位物体 · 生成结构化结果</small>
    </div>
  </div>
</template>
