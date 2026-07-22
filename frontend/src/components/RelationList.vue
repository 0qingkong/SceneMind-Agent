<script setup lang="ts">
import { computed } from 'vue'

import type {
  DetectedObject,
  DetectedRelation,
  RelationPredicate,
} from '../types/api'
import { buildObjectDisplayNameMap, objectDisplayName } from '../utils/objectDisplayNames'
import { collapseReciprocalRelations } from '../utils/relationDisplay'

const props = defineProps<{
  objects: DetectedObject[]
  relations: DetectedRelation[]
}>()

const predicateLabels: Record<RelationPredicate, string> = {
  left_of: '位于左侧',
  right_of: '位于右侧',
  above: '位于上方',
  below: '位于下方',
  near: '靠近',
  overlaps: '发生重叠',
  inside: '位于内部',
  contains: '包含',
}

const objectNames = computed(() => buildObjectDisplayNameMap(props.objects))
const visibleRelations = computed(() => collapseReciprocalRelations(props.relations))

function resolveName(objectId: string) {
  return objectDisplayName(objectNames.value, objectId)
}
</script>

<template>
  <section class="relation-section">
    <div class="relation-heading">
      <h3>二维空间关系</h3>
      <span>{{ visibleRelations.length }}</span>
    </div>
    <p class="relation-explanation">
      空间关系由二维边界框几何规则推导，不代表真实深度或物理距离。
    </p>

    <div v-if="visibleRelations.length" class="relation-list">
      <article v-for="relation in visibleRelations" :key="relation.id" class="relation-card">
        <div class="relation-statement">
          <strong>{{ resolveName(relation.subject_id) }}</strong>
          <span>{{ predicateLabels[relation.predicate] }}</span>
          <strong>{{ resolveName(relation.object_id) }}</strong>
        </div>
        <small>几何强度 {{ Math.round(relation.score * 100) }}%</small>
      </article>
    </div>
    <p v-else class="relation-empty">没有足够清晰的空间关系</p>
  </section>
</template>
