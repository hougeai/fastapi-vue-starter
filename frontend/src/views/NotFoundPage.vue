<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.go(-1)
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="not-found-page">
    <div class="content">
      <h1>404</h1>
      <p>抱歉，您访问的页面不存在</p>
      <div class="actions">
        <a-button @click="goBack" type="outline">返回上一页</a-button>
        <a-button @click="goHome" type="primary">回到首页</a-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
}

.content {
  text-align: center;
}

h1 {
  font-size: 72px;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--color-text-1);
}

p {
  font-size: 20px;
  margin-bottom: 32px;
  color: var(--color-text-2);
}

.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}
</style>
