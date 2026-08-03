<script setup lang="ts">
import { computed, ref } from 'vue'

import type { DetectedObject, DetectedRelation, RelationPredicate } from '../types/api'
import { buildObjectDisplayNameMap, objectDisplayName } from '../utils/objectDisplayNames'
import { collapseReciprocalRelations, predicateLabels } from '../utils/relationDisplay'

const props = defineProps<{ objects: DetectedObject[]; relations: DetectedRelation[] }>()
const showAll = ref(false)
const selectedObject = ref('')
const selectedPredicate = ref<'all' | RelationPredicate>('all')
const objectNames = computed(() => buildObjectDisplayNameMap(props.objects))
const collapsedRelations = computed(() => collapseReciprocalRelations(props.relations))
const filteredRelations = computed(() => collapsedRelations.value.filter((relation) => {
  const objectMatches = !selectedObject.value || relation.subject_id === selectedObject.value || relation.object_id === selectedObject.value
  const predicateMatches = selectedPredicate.value === 'all' || relation.predicate === selectedPredicate.value
  return objectMatches && predicateMatches
}))
const visibleRelations = computed(() => showAll.value ? filteredRelations.value : filteredRelations.value.slice(0, 8))
const predicates = computed(() => [...new Set(collapsedRelations.value.map((item) => item.predicate))])

function resolveName(objectId: string) { return objectDisplayName(objectNames.value, objectId) }
</script>

<template>
  <section class="relation-section">
    <div class="relation-heading"><h3>二维空间关系</h3><span>{{ filteredRelations.length }}</span></div>
    <p class="relation-explanation">空间关系由二维边界框几何规则推导，不代表真实深度或物理距离。</p>
    <div v-if="collapsedRelations.length" class="relation-filters">
      <label>相关物体
        <select v-model="selectedObject" @change="showAll = false">
          <option value="">全部物体</option>
          <option v-for="item in objects" :key="item.id" :value="item.id">{{ resolveName(item.id) }}</option>
        </select>
      </label>
      <label>关系类型
        <select v-model="selectedPredicate" @change="showAll = false">
          <option value="all">全部关系</option>
          <option v-for="predicate in predicates" :key="predicate" :value="predicate">{{ predicateLabels[predicate] }}</option>
        </select>
      </label>
    </div>
    <div v-if="visibleRelations.length" class="relation-list">
      <article v-for="relation in visibleRelations" :key="relation.id" class="relation-card">
        <div class="relation-statement"><strong>{{ resolveName(relation.subject_id) }}</strong><span>{{ predicateLabels[relation.predicate] }}</span><strong>{{ resolveName(relation.object_id) }}</strong></div>
        <small>几何强度 {{ Math.round(relation.score * 100) }}%</small>
      </article>
      <button v-if="filteredRelations.length > 8" class="text-button relation-toggle" @click="showAll = !showAll">{{ showAll ? '收起关系' : `查看全部 ${filteredRelations.length} 条` }}</button>
    </div>
    <p v-else class="relation-empty">{{ collapsedRelations.length ? '当前筛选条件下没有关系' : '没有足够清晰的空间关系' }}</p>
  </section>
</template>
