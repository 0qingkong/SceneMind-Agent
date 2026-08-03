<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{ src: string; alt: string }>()
const failed = ref(false)
watch(() => props.src, () => { failed.value = false })
</script>

<template>
  <figure class="safe-image" :class="{ failed }">
    <img v-if="!failed" :src="src" :alt="alt" @error="failed = true" />
    <div v-else role="img" :aria-label="`${alt}加载失败`"><strong>图片证据暂不可用</strong><small>记录元数据仍可查看，请稍后重试。</small></div>
  </figure>
</template>
