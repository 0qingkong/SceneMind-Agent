<template>
  <section class="home-view">
    <p class="eyebrow">MULTIMODAL SPATIAL MEMORY</p>
    <h1>让 AI 记住<br />物品最后出现的位置</h1>
    <p class="hero-description">
      SceneMind 将场景图片转换为物体、位置与时间组成的结构化记忆，
      为物品追踪与未来的 AI 眼镜提供空间智能基础。
    </p>
    <div class="hero-actions">
      <RouterLink class="primary-link" to="/live">开启实时镜头</RouterLink>
      <RouterLink class="primary-link" to="/analyze">分析第一张图片</RouterLink>
      <RouterLink class="secondary-link" to="/memory">查看空间记忆</RouterLink>
      <RouterLink class="secondary-link" to="/agent">询问记忆 Agent</RouterLink>
    </div>

    <div class="capability-grid">
      <article><span>01</span><h2>看见场景</h2><p>真实检测物体并保留边界框证据。</p></article>
      <article><span>02</span><h2>理解关系</h2><p>从二维几何推导上下、左右、包含和邻近。</p></article>
      <article><span>03</span><h2>形成记忆</h2><p>保存场景、物体、关系、地点与时间。</p></article>
      <article><span>04</span><h2>自然语言检索</h2><p>通过 Agent 查询记忆并打开原始图片证据。</p></article>
    </div>
  </section>
</template>
