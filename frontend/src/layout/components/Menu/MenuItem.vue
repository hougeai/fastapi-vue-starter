<script setup>
const props = defineProps({
  menu: {
    type: Object,
    required: true
  }
})
const { menu } = toRefs(props)

// 检查菜单是否应该显示（有标题或者是包含有效子菜单的父级菜单）
const shouldShowMenu = menu => {
  // 如果有标题，则应该显示
  if (menu.title) {
    return true
  }
  // 如果是父级菜单且有子菜单，则检查是否有任何有效的子菜单
  if (menu.children && menu.children.length > 0) {
    return menu.children.some(child => shouldShowMenu(child))
  }
  // 其他情况不显示
  return false
}

// 过滤有效的子菜单
const validChildren = computed(() => {
  if (!menu.value.children) return []
  return menu.value.children.filter(child => shouldShowMenu(child))
})
</script>

<template>
  <template v-if="validChildren.length === 0">
    <a-menu-item :key="menu.path">
      <template #icon v-if="menu?.icon">
        <component :is="menu?.icon"></component>
      </template>
      {{ menu.title }}
    </a-menu-item>
  </template>

  <a-sub-menu v-else :key="menu.path" :title="menu.title">
    <template #icon v-if="menu?.icon">
      <component :is="menu?.icon"></component>
    </template>
    <MenuItem v-for="menuChild of validChildren" :key="menuChild.path" :menu="menuChild" />
  </a-sub-menu>
</template>

<style scoped></style>
