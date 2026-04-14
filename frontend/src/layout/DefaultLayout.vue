<template>
  <div>
    <div class="default-layout">
      <a-layout class="min-h-screen">
        <a-affix>
          <a-layout-header>
            <!-- 上方导航栏 -->
            <NavBar>
              <!-- left插槽使用默认内容，可以省略 -->
              <!-- 默认插槽和center插槽，默认插槽可不加template直接写内容，作用同center插槽 -->
              <!-- right插槽使用默认内容，可以省略 -->
            </NavBar>
          </a-layout-header>
        </a-affix>

        <a-layout-content>
          <router-view v-slot="{ Component }">
            <transition name="fade-x">
              <component :is="Component" />
            </transition>
          </router-view>
        </a-layout-content>

        <a-layout-footer>
          <Footer />
        </a-layout-footer>
      </a-layout>
    </div>
  </div>
</template>

<style scoped>
.default-layout :deep(.arco-layout-header),
.default-layout :deep(.arco-layout-footer),
.default-layout :deep(.arco-layout-content) {
  @apply text-[var(--color-text-1)] text-14px;
}

.default-layout :deep(.arco-layout-header) {
  @apply w-full h-58px overflow-hidden;
  @apply bg-[var(--color-bg-1)]  border-b-[var(--color-border-1)] border-b-solid border-b-width-1px box-border;
}
.default-layout :deep(.arco-layout-content) {
  @apply flex flex-col items-center;
  @apply bg-[var(--color-bg-1)] relative;
  @apply flex-grow;
}
.default-layout :deep(.arco-layout-footer) {
  @apply w-full h-60px flex justify-center items-center;
  @apply border-t-[var(--color-border-1)] border-t-solid border-t-width-1px box-border;
  @apply bg-[var(--color-bg-1)] text-[var(--color-text-1)] text-14px;
}
</style>
