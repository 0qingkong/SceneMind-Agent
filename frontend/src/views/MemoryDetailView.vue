<script setup lang="ts">
import { onMounted, ref } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'

import { apiAssetUrl, deleteObservation, getObservation } from '../api/client'
import ImageStage from '../components/ImageStage.vue'
import ObjectList from '../components/ObjectList.vue'
import RelationList from '../components/RelationList.vue'
import type { ObservationDetail } from '../types/api'

const route = useRoute()
const router = useRouter()
const observation = ref<ObservationDetail | null>(null)
const loading = ref(true)
const deleting = ref(false)
const errorMessage = ref('')

async function loadObservation() {
  loading.value = true
  errorMessage.value = ''
  try {
    observation.value = await getObservation(String(route.params.id))
  } catch (error) {
    errorMessage.value = axios.isAxiosError(error) && error.response?.status === 404
      ? '这条场景记忆不存在或已被删除。'
      : '无法加载场景记忆。'
  } finally {
    loading.value = false
  }
}

async function handleDelete() {
  if (!observation.value || !window.confirm('确定删除这条场景记忆及其图片吗？')) return
  deleting.value = true
  try {
    await deleteObservation(observation.value.id)
    await router.push('/memory')
  } catch {
    errorMessage.value = '删除失败，请稍后重试。'
    deleting.value = false
  }
}

onMounted(loadObservation)
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">MEMORY DETAIL</p><h1>{{ observation?.title || '场景记忆详情' }}</h1></div>
      <RouterLink class="secondary-link" to="/memory">返回记忆</RouterLink>
    </div>
    <p v-if="loading" class="memory-status">正在加载场景记忆…</p>
    <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <div v-else-if="observation" class="workspace-grid">
      <section class="workspace-panel">
        <ImageStage
          :image-url="apiAssetUrl(observation.image_url)"
          :objects="observation.objects"
          :loading="false"
        />
        <div class="detail-metadata">
          <span v-if="observation.is_demo" class="demo-inline">演示数据</span>
          <span>{{ new Date(observation.created_at).toLocaleString('zh-CN') }}</span>
          <span v-if="observation.location">{{ observation.location }}</span>
          <span>{{ observation.image_width }}×{{ observation.image_height }}</span>
        </div>
        <button class="danger-button" :disabled="deleting" @click="handleDelete">
          {{ deleting ? '正在删除…' : '删除这条记忆' }}
        </button>
      </section>
      <section class="workspace-panel result-panel">
        <div class="summary-card">{{ observation.summary }}</div>
        <ObjectList :objects="observation.objects" />
        <RelationList :objects="observation.objects" :relations="observation.relations" />
        <p class="trace">Engine: {{ observation.engine }}<br />{{ observation.id }}</p>
      </section>
    </div>
  </section>
</template>
