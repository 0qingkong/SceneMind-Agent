<template>
  <section class="home-view">
    <p class="eyebrow">MULTIMODAL SPATIAL MEMORY</p>
    <h1>让 AI 记住<br />物品最后出现的位置</h1>
    <p class="hero-description">
      SceneMind 将场景图片转换为物体、位置与时间组成的结构化记忆，
      为物品追踪与未来的 AI 眼镜提供空间智能基础。
    </p>
    <div class="hero-actions">
      <RouterLink class="primary-link" to="/analyze">分析第一张图片</RouterLink>
      <RouterLink class="secondary-link" to="/memory">查看空间记忆</RouterLink>
    </div>

    <div class="capability-grid">
      <article><span>01</span><h2>场景感知</h2><p>识别物体并提供边界框证据。</p></article>
      <article><span>02</span><h2>空间关系</h2><p>理解上下、左右、包含和邻近。</p></article>
      <article><span>03</span><h2>长期记忆</h2><p>回答物品最后出现的时间和位置。</p></article>
    </div>
  </section>
</template>
