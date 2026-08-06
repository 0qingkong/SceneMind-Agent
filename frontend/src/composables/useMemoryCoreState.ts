import { computed, toValue, type MaybeRefOrGetter } from 'vue'

export type MemoryCoreState = 'idle' | 'observing' | 'analyzing' | 'remembering' | 'retrieving' | 'target-found' | 'warning' | 'offline'

const stateCopy: Record<MemoryCoreState, { label: string; detail: string }> = {
  idle: { label: '记忆中枢待命', detail: '等待新的视觉观察' },
  observing: { label: '正在观察', detail: '仅处理已授权的视觉输入' },
  analyzing: { label: '正在理解场景', detail: '检测物体并推导二维关系' },
  remembering: { label: '正在形成记忆', detail: '保存图片、时间与空间证据' },
  retrieving: { label: '正在检索证据', detail: '从已保存观察中查找匹配项' },
  'target-found': { label: '已定位证据', detail: '可打开原始场景核验' },
  warning: { label: '需要注意', detail: '查看文字状态与恢复操作' },
  offline: { label: '服务离线', detail: '启动后端后即可恢复' },
}

export function useMemoryCoreState(state: MaybeRefOrGetter<MemoryCoreState>) {
  const copy = computed(() => stateCopy[toValue(state)])
  return { copy }
}
