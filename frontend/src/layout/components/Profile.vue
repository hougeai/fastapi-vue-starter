<script setup>
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const router = useRouter()

const handleLogout = () => {
  AModal.confirm({
    title: '确认退出',
    content: '您确定要退出登录吗？',
    okText: '确认退出',
    cancelText: '取消',
    onOk: () => {
      userStore.logout()
      AMessage.success('已退出登录')
    }
  })
}

const handleToUserCenter = () => {
  router.push('/user-center')
}
</script>

<template>
  <div v-if="userStore.userId">
    <a-dropdown trigger="hover" :popup-max-height="false">
      <a-button type="text">
        <template #icon>
          <icon-material-symbols:account-circle class="text-[var(--color-text-1)] text-18px" />
        </template>
      </a-button>

      <template #content>
        <div class="w-200px px-4 py-3">
          <!-- 用户信息 -->
          <div class="px-3 py-2 flex items-center">
            <img :src="userStore.avatar" alt="avatar" class="w-15 h-15 rounded-full" />
            <div class="ml-3">
              <div class="font-bold text-gray-800">{{ userStore.userName }}</div>
              <div class="text-xs text-gray-500 mt-1">ID: {{ userStore.userId }}</div>
              <div
                :class="{
                  'bg-gradient-to-r from-rose-500 to-red-600': userStore.roleId === 1,
                  'bg-gradient-to-r from-violet-500 to-purple-600': userStore.roleId === 2,
                  'bg-gradient-to-r from-indigo-400 to-blue-500': userStore.roleId === 3,
                  'bg-gradient-to-r from-amber-400 to-orange-500': userStore.roleId === 4,
                  'bg-gradient-to-r from-indigo-500 to-pink-500': userStore.roleId === 5
                }"
                class="flex items-center inline-block mt-1 px-1 py-1 rounded-lg font-semibold text-xs text-white shadow-lg"
              >
                <icon-mingcute:vip-1-fill class="inline mr-1" />
                {{ userStore.roleName }}
              </div>
            </div>
          </div>

          <a-divider class="" />

          <!-- 菜单项 -->
          <a-doption @click="handleToUserCenter">
            <div class="flex items-center w-full">
              <div class="flex items-center">
                <icon-material-symbols:person class="mr-2 text-lg" />
                <span>个人中心</span>
              </div>
              <icon-material-symbols:arrow-forward class="text-sm absolute right-2" />
            </div>
          </a-doption>

          <a-doption @click="handleLogout">
            <div class="flex items-center w-full">
              <div class="flex items-center">
                <icon-material-symbols:logout class="mr-2 text-lg" />
                <span>退出登录</span>
              </div>
              <icon-material-symbols:arrow-forward class="text-sm absolute right-2" />
            </div>
          </a-doption>
        </div>
      </template>
    </a-dropdown>
  </div>
  <div v-else>
    <a-button type="text" @click="$router.push('/home')" class="login-button">
      <div class="flex items-center">
        <icon-material-symbols-login class="text-[var(--color-text-1)] text-16px" />
        <span class="ml-1">登录</span>
      </div>
    </a-button>
  </div>
</template>

<style scoped>
.login-button {
  @apply px-2 py-1 h-auto flex items-center text-16px font-700 text-shadow-sm cursor-pointer;
  @apply border border-solid rounded-lg;
  @apply border-[var(--color-border-2)] bg-transparent;
  @apply transition-all duration-200 ease-in-out;
  @apply hover:border-[var(--color-primary-light-4)] hover:bg-[var(--color-primary-light-1)];
  @apply hover:text-[var(--color-primary-6)] hover:shadow-sm;
}

.login-button:active {
  @apply transform scale-95;
}
</style>
