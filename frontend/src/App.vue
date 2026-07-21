<template>
  <div class="application">
    <header class="topbar">
      <RouterLink class="brand" to="/">
        <span class="brand-mark">S</span>
        <span><strong>SceneMind</strong><small>Spatial Memory Agent</small></span>
      </RouterLink>
      <span class="version-chip">v0.3</span>
    </header>

    <main class="page-container">
      <RouterView />
    </main>

    <nav class="bottom-nav">
      <RouterLink to="/">首页</RouterLink>
      <RouterLink to="/analyze">分析</RouterLink>
      <RouterLink to="/memory">记忆</RouterLink>
    </nav>
  </div>
</template>
