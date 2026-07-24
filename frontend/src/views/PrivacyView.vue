<script setup lang="ts">
import { ref } from 'vue'

import { exportData } from '../api/client'
import { loadPreferences, resetPreferences, savePreferences } from '../privacy/settings'

const preferences = ref(loadPreferences())
const message = ref('')
const exporting = ref(false)

function save() {
  preferences.value = savePreferences(preferences.value)
  message.value = '偏好已保存在当前浏览器。'
}

function reset() {
  preferences.value = resetPreferences()
  message.value = '已恢复默认偏好。'
}

async function downloadExport() {
  exporting.value = true
  try {
    const blob = await exportData()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `scenemind-export-${new Date().toISOString().slice(0, 10)}.json`
    link.click()
    URL.revokeObjectURL(url)
    message.value = 'JSON 元数据导出已生成；不包含图片字节。'
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">PRIVACY & SETTINGS</p><h1>隐私与采集偏好</h1></div>
      <span>Local preferences</span>
    </div>
    <div class="privacy-grid">
      <section class="privacy-card">
        <h2>连续采集</h2>
        <label>默认采样间隔（3–60 秒）<input v-model.number="preferences.defaultCaptureInterval" type="number" min="3" max="60" /></label>
        <label>自动保存策略<select v-model="preferences.autoSaveMode"><option value="manual">仅手动保存</option><option value="meaningful-change">有意义变化</option><option value="every-analyzed-sample">每个已分析样本</option></select></label>
        <label class="privacy-check"><input v-model="preferences.pauseAllContinuousCapture" type="checkbox" /> 暂停所有连续采集</label>
        <label class="privacy-check"><input v-model="preferences.alwaysShowCameraIndicator" type="checkbox" /> 始终显示摄像头使用指示</label>
      </section>
      <section class="privacy-card">
        <h2>记忆与界面</h2>
        <label>保留天数偏好<input v-model.number="preferences.retentionDays" type="number" min="1" max="3650" /></label>
        <p class="planned-note">规划中：自动按保留天数清理。目前此项只保存偏好，不会自动删除数据。</p>
        <label class="privacy-check"><input v-model="preferences.confirmBeforeDelete" type="checkbox" /> 删除会话前要求确认</label>
        <label class="privacy-check"><input v-model="preferences.showSimulatorLabels" type="checkbox" /> 模拟器显示物体标签</label>
      </section>
      <section class="privacy-card truth-card">
        <h2>当前实现边界</h2>
        <ul><li>摄像头只在明确连接后启用，不录制麦克风。</li><li>连续会话依赖前台页面，不承诺后台运行。</li><li>本项目没有实现加密或人脸模糊。</li><li>图片保存在配置的本地服务端目录。</li></ul>
      </section>
      <section class="privacy-card">
        <h2>数据可携带性</h2>
        <p>导出观察、物体、关系、会话和来源元数据。图片二进制不会嵌入 JSON。</p>
        <button class="secondary-button" :disabled="exporting" @click="downloadExport">{{ exporting ? '正在导出…' : '导出 JSON 数据' }}</button>
      </section>
    </div>
    <div class="privacy-actions"><button class="primary-button" @click="save">保存偏好</button><button class="secondary-button" @click="reset">恢复默认</button></div>
    <p v-if="message" class="success-message">{{ message }}</p>
  </section>
</template>
