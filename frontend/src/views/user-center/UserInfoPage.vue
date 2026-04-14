<template>
  <div class="w-full h-full flex flex-col">
    <!-- 页面标题 -->
    <div class="m-2">
      <h1 class="text-xl font-semibold">个人资料</h1>
    </div>
    <div class="flex-1 mx-2 mb-2 space-y-2">
      <!-- 用户基本信息卡片 -->
      <div class="bg-[var(--color-fill-2)] p-6 rounded-2xl">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <!-- 用户头像 -->
            <img
              :src="userStore.avatar"
              alt="用户头像"
              class="w-20 h-20 rounded-full object-cover border-4 border-white shadow-lg"
            />
            <!-- 用户信息 -->
            <div class="flex flex-col justify-center space-y-1">
              <div
                class="text-xl font-bold hover:text-[var(--color-primary-light-4)] cursor-pointer"
                @click="showEditProfileDialog = true"
              >
                {{ userStore.userName }}
              </div>
              <span class="text-[var(--color-text-3)]"> ID: {{ userStore.userId }} </span>
            </div>
          </div>

          <!-- 操作按钮区：刷新 + 退出登录 -->
          <div class="flex items-center space-x-2">
            <a-button
              type="outline"
              shape="round"
              :loading="refreshing"
              @click="handleManualRefresh"
              class="flex items-center space-x-2"
            >
              <icon-material-symbols:refresh class="text-lg" />
              <span>刷新</span>
            </a-button>

            <a-button
              type="outline"
              status="danger"
              @click="handleLogout"
              class="flex items-center space-x-2"
            >
              <icon-material-symbols:logout class="text-lg" />
              <span>退出登录</span>
            </a-button>
          </div>
        </div>
      </div>

      <!-- 用户等级卡片 -->
      <div class="bg-[var(--color-primary-light-1)] p-6 rounded-2xl">
        <div class="flex items-center justify-between p-3">
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-3">
              <div
                :class="{
                  'bg-gradient-to-r from-rose-500 to-red-600': userStore.roleId === 1,
                  'bg-gradient-to-r from-violet-500 to-purple-600': userStore.roleId === 2,
                  'bg-gradient-to-r from-indigo-400 to-blue-500': userStore.roleId === 3,
                  'bg-gradient-to-r from-amber-400 to-orange-500': userStore.roleId === 4,
                  'bg-gradient-to-r from-indigo-500 to-pink-500': userStore.roleId === 5
                }"
                class="flex items-center px-4 py-4 rounded-xl font-semibold text-lg text-white shadow-lg"
              >
                <icon-mingcute:vip-1-fill class="inline mr-1" />
                {{ userStore.roleName }}
              </div>
              <div>
                <div class="text-sm mb-1 text-[var(--color-text-2)]">当前用户等级权益：</div>
                <div class="text-xs text-[var(--color-text-3)]">{{ userStore.roleDesc }}</div>
                <div
                  class="inline-block px-2 py-1 bg-green-50 text-green-500 rounded-full cursor-pointer text-xs mt-1"
                >
                  到期时间：{{ userStore.roleExpire }}
                </div>
              </div>
            </div>
          </div>

          <a-button
            type="primary"
            size="large"
            status="success"
            @click="handleUpgrade"
            :disabled="userStore.roleId === 1"
            class="flex items-center space-x-2"
            style="border-radius: 0.5rem"
          >
            <icon-material-symbols:upgrade class="text-lg" />
            <span class="text-lg font-bold">升级</span>
          </a-button>
        </div>
      </div>

      <!-- 账号绑定设置 -->
      <div class="bg-[var(--color-fill-1)] p-6 pt-1 rounded-2xl">
        <h3 class="flex items-center text-xl">
          <icon-material-symbols:link class="mr-2" />
          账号绑定
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- 邮箱绑定 -->
          <div class="flex items-center justify-between p-3 bg-[var(--color-fill-2)] rounded-xl">
            <div class="flex items-center space-x-3">
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center bg-[var(--color-primary-light-2)]"
              >
                <icon-material-symbols:mail class="text-[var(--color-primary-light-4)] text-xl" />
              </div>
              <div>
                <div class="text-sm mb-1 text-[var(--color-text-2)]">邮箱绑定</div>
                <div class="text-xs text-[var(--color-text-3)]">
                  {{ userStore.email ? userStore.email : '未绑定邮箱' }}
                </div>
              </div>
            </div>
            <a-button
              :type="userStore.email ? 'outline' : 'primary'"
              @click="handleEmailBinding"
              size="small"
              style="border-radius: 0.25rem"
            >
              {{ userStore.email ? '解绑' : '绑定' }}
            </a-button>
          </div>

          <!-- 手机绑定 -->
          <div class="flex items-center justify-between p-3 bg-[var(--color-fill-2)] rounded-xl">
            <div class="flex items-center space-x-3">
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center bg-[var(--color-primary-light-2)]"
              >
                <icon-material-symbols:phone-iphone-outline
                  class="text-[var(--color-primary-light-4)] text-xl"
                />
              </div>
              <div>
                <div class="text-sm mb-1 text-[var(--color-text-2)]">手机绑定</div>
                <div class="text-xs text-[var(--color-text-3)]">
                  {{ userStore.phone ? maskPhone(userStore.phone) : '未绑定手机' }}
                </div>
              </div>
            </div>
            <a-button
              :type="userStore.phone ? 'outline' : 'primary'"
              @click="handlePhoneBinding"
              size="small"
              style="border-radius: 0.25rem"
            >
              {{ userStore.phone ? '解绑' : '绑定' }}
            </a-button>
          </div>

          <!-- 微信绑定 -->
          <div class="flex items-center justify-between p-3 bg-[var(--color-fill-2)] rounded-xl">
            <div class="flex items-center space-x-3">
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center bg-[var(--color-primary-light-2)]"
              >
                <icon-ic:baseline-wechat class="text-[var(--color-success-light-4)] text-xl" />
              </div>
              <div>
                <div class="text-sm mb-1 text-[var(--color-text-2)]">微信绑定</div>
                <div class="text-xs text-[var(--color-text-3)]">
                  {{ userStore.wxid ? `wxId: ${userStore.wxid}` : '未绑定微信' }}
                </div>
              </div>
            </div>
            <a-button
              :type="userStore.wxid ? 'outline' : 'primary'"
              @click="handleWechatBinding"
              size="small"
              style="border-radius: 0.25rem"
            >
              {{ userStore.wxid ? '解绑' : '绑定' }}
            </a-button>
          </div>
        </div>
      </div>

      <!-- 安全设置 -->
      <div class="bg-[var(--color-fill-1)] p-6 pt-1 rounded-2xl">
        <h3 class="flex items-center text-xl">
          <icon-material-symbols:security class="mr-2 text-[var(--color-danger-6)]" />
          安全设置
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- 修改密码 -->
          <a-button
            type="outline"
            @click="showPasswordDialog = true"
            class="action-button password-button"
          >
            <icon-material-symbols:lock class="text-2xl text-[var(--color-primary-light-6)]" />
            <div class="text-center">
              <div class="font-bold text-[var(--color-primary-light-6)]">修改密码</div>
              <div class="text-[var(--color-text-3)]">更改您的登录密码</div>
            </div>
          </a-button>

          <!-- 注销用户 -->
          <a-button type="outline" @click="handleDeleteAccount" class="action-button delete-button">
            <icon-material-symbols:person-remove
              class="text-2xl text-[var(--color-danger-light-4)]"
            />
            <div class="text-center">
              <div class="font-bold text-[var(--color-danger-light-4)]">注销用户</div>
              <div class="text-[var(--color-text-3)]">永久删除您的账户</div>
            </div>
          </a-button>

          <!-- 反馈建议 -->
          <a-button
            type="outline"
            @click="showFeedbackDialog = true"
            class="action-button feedback-button"
          >
            <icon-material-symbols:feedback class="text-2xl text-[var(--color-success-6)]" />
            <div class="text-center">
              <div class="font-bold text-[var(--color-primary-6)]">反馈建议</div>
              <div class="text-[var(--color-text-3)]">联系我们提出建议</div>
            </div>
          </a-button>
        </div>
      </div>
    </div>

    <!-- 反馈建议对话框 -->
    <FeedbackDialog v-model:visible="showFeedbackDialog" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
const userStore = useUserStore()

onMounted(async () => {
  // 页面加载时获取用户信息
  await userStore.getUserInfo()
})

// 对话框状态
const showPasswordDialog = ref(false)
const showFeedbackDialog = ref(false)
const showEditProfileDialog = ref(false)
const showEmailBindingDialog = ref(false)
const showWechatBindingDialog = ref(false)
const showUpgradeDialog = ref(false)

// 手机号脱敏
const maskPhone = phone => {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

// 处理用户刷新
const refreshing = ref(false)
const handleManualRefresh = async () => {
  try {
    refreshing.value = true
    const res = await userStore.getUserInfo(true)
    if (res?.success) {
      AMessage.success('已刷新最新用户信息')
    } else {
      AMessage.error(res?.error || '刷新失败')
    }
  } finally {
    refreshing.value = false
  }
}

// 处理退出登录
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

// 处理注销用户
const handleDeleteAccount = () => {
  AModal.confirm({
    title: '确认注销',
    content: '您确定要注销账户吗？注销后您的账户将无法恢复，且所有数据将被清空。',
    okText: '确认注销',
    cancelText: '取消',
    onOk: async () => {
      try {
        const result = await userStore.deleteAccount()
        if (result.success) {
          AMessage.success('账户注销成功')
        } else {
          AMessage.error(result.error || '注销账户失败')
        }
      } catch (error) {
        console.error(error)
        AMessage.error('注销账户失败')
      }
    }
  })
}
/* 处理升级：打开升级会员对话框 */
const handleUpgrade = () => {
  showUpgradeDialog.value = true
}

// 处理邮箱绑定
const handleEmailBinding = () => {
  if (userStore.email) {
    AModal.confirm({
      title: '确认解绑',
      content: '您确定要解绑邮箱吗？解绑后将无法通过邮箱登录。',
      okText: '确认解绑',
      cancelText: '取消',
      onOk: async () => {
        const result = await userStore.unbindEmail()
        if (result.success) {
          AMessage.success('邮箱解绑成功')
        } else {
          AMessage.error(result.error || '邮箱解绑失败')
        }
      }
    })
  } else {
    // 显示邮箱绑定对话框：处理邮箱绑定
    showEmailBindingDialog.value = true
  }
}

// 处理手机绑定
const handlePhoneBinding = () => {
  if (userStore.phone) {
    AModal.confirm({
      title: '确认解绑',
      content: '您确定要解绑手机吗？解绑后将无法通过手机验证码登录。',
      okText: '确认解绑',
      cancelText: '取消',
      onOk: () => {
        AMessage.info('手机解绑功能开发中...')
      }
    })
  } else {
    AMessage.info('手机绑定功能开发中...')
  }
}

// 处理微信绑定
const handleWechatBinding = () => {
  if (userStore.wxid) {
    AModal.confirm({
      title: '确认解绑',
      content: '您确定要解绑微信吗？解绑后将无法通过微信登录。',
      okText: '确认解绑',
      cancelText: '取消',
      onOk: async () => {
        const result = await userStore.unbindWechat()
        if (result.success) {
          AMessage.success('微信解绑成功')
        } else {
          AMessage.error(result.error || '微信解绑失败')
        }
      }
    })
  } else {
    // 显示微信绑定对话框
    showWechatBindingDialog.value = true
  }
}
</script>

<style scoped>
/* 操作按钮样式 */
.action-button {
  height: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  border: 2px dashed var(--color-border-3);
  transition: all 0.2s;
}

.password-button:hover {
  border-color: var(--color-primary-light-4);
  background-color: var(--color-primary-light-1);
}

.delete-button:hover {
  border-color: var(--color-danger-light-4);
  background-color: var(--color-danger-light-1);
}

.feedback-button:hover {
  border-color: var(--color-success-light-4);
  background-color: var(--color-success-light-1);
}
</style>
