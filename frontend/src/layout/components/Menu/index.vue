<script setup>
import { menuRouterFormatList } from '@/router/menuRouter.js'

// 新增
const props = defineProps({
  mode: {
    type: String,
    default: 'vertical'
  }
})
// 菜单模式，horizontal 水平，vertical 垂直
const mode = toRef(props, 'mode')

// 菜单数据
const menuList = ref(menuRouterFormatList)

const router = useRouter()
// 子菜单点击事件
const onClickMenuItem = key => {
  router.push(key)
}

const route = useRoute()
// 当前选中菜单
const selectedKeys = computed(() => [route.path])
// 获取所有包含子菜单的菜单项的路径，用于默认展开
const defaultOpenKeys = computed(() => {
  return menuList.value
    .filter(menu => menu.children && menu.children.length > 0)
    .map(menu => menu.path)
})
</script>

<template>
  <a-menu
    class="menu"
    auto-open-selected
    :selected-keys="selectedKeys"
    :default-open-keys="defaultOpenKeys"
    @menuItemClick="onClickMenuItem"
    :mode="mode"
    :accordion="false"
  >
    <MenuItem v-for="menu of menuList" :key="menu.path" :menu="menu" />
  </a-menu>
</template>

<style scoped>
.menu {
  @apply bg-[var(--color-bg-3)] text-14px pt-4 pb-2;
  line-height: 1.5;
}
.menu :deep(.arco-menu-icon) {
  @apply mr-3 w-4 h-4 flex-none;
  line-height: 1;
}
/* 一级菜单项 */
.menu :deep(.arco-menu-item) {
  @apply mb-1 rounded-md font-medium;
  height: 40px;
  line-height: 40px;
  padding: 0 12px;
}

/* 一级菜单项 hover 状态 */
.menu :deep(.arco-menu-item):hover {
  @apply bg-[var(--color-fill-2)];
}

/* 一级菜单项选中状态 */
.menu :deep(.arco-menu-item-selected) {
  @apply bg-[var(--color-primary-light-1)] text-[var(--color-primary-6)];
}

/* 子菜单标题 */
.menu :deep(.arco-sub-menu) {
  @apply mb-4;
}

.menu :deep(.arco-sub-menu-title) {
  @apply mx-3 rounded-md font-medium;
  height: 40px;
  line-height: 40px;
  padding: 0 12px;
}

.menu :deep(.arco-sub-menu-title):hover {
  @apply bg-[var(--color-fill-2)];
}
</style>
