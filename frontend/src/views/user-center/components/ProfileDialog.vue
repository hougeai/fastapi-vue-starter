<template>
  <a-modal
    :visible="visible"
    @cancel="handleEditCancel"
    :footer="null"
    :closable="false"
    width="480px"
    class="rounded-2xl shadow-2xl"
    centered
  >
    <div class="flex flex-col items-center py-8 px-2">
      <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
        <icon-material-symbols:person class="text-3xl text-green-600" />
      </div>

      <div class="text-2xl font-bold mb-2">编辑资料</div>
      <div class="text-gray-500 text-16px mb-6 text-center">完善您的个人信息</div>

      <!-- 头像预览 -->
      <div class="flex flex-col items-center mb-6">
        <img
          :src="profileForm.avatar || userStore.avatar"
          class="w-20 h-20 rounded-full object-cover border-4 border-white shadow-lg mb-2"
        />
        <span class="text-14px text-gray-500">头像预览</span>
      </div>

      <a-form
        :model="profileForm"
        layout="vertical"
        @submit="handleEditProfile"
        class="w-full"
        ref="formRef"
      >
        <a-form-item field="avatar" :rules="avatarRules" class="mb-4" label="头像URL：">
          <a-input
            v-model="profileForm.avatar"
            placeholder="头像URL地址"
            allow-clear
            size="large"
            class="h-12 text-16px"
          />
        </a-form-item>

        <a-form-item field="userName" :rules="userNameRules" class="mb-6" label="昵称：">
          <a-input
            v-model="profileForm.userName"
            placeholder="请输入用户昵称"
            allow-clear
            size="large"
            class="h-12 text-16px"
            :maxlength="20"
          />
        </a-form-item>

        <!-- 用户名要求提示 -->
        <div class="mb-6 p-3 bg-gray-50 rounded-lg">
          <div class="text-sm font-medium text-gray-700 mb-2">昵称要求：</div>
          <div class="space-y-1 text-xs text-gray-600">
            <div class="flex items-center">
              <icon-material-symbols:check-circle
                :class="profileForm.userName.length >= 1 ? 'text-green-500' : 'text-gray-400'"
                class="mr-2"
              />
              至少1个字符
            </div>
            <div class="flex items-center">
              <icon-material-symbols:check-circle
                :class="profileForm.userName.length <= 20 ? 'text-green-500' : 'text-gray-400'"
                class="mr-2"
              />
              不超过20个字符
            </div>
          </div>
        </div>

        <div class="flex space-x-3">
          <a-button type="outline" @click="handleEditCancel" class="flex-1 h-12 text-16px">
            取消
          </a-button>
          <a-button
            type="primary"
            html-type="submit"
            :loading="loading"
            class="flex-1 h-12 text-16px font-bold"
          >
            保存修改
          </a-button>
        </div>
      </a-form>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, watch, reactive } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const props = defineProps({
  visible: Boolean
})

const emit = defineEmits(['update:visible'])

const loading = ref(false)
const formRef = ref()

// 编辑资料表单
const profileForm = reactive({
  avatar: '',
  userName: userStore.userName
})

// URL验证函数
const isValidUrl = string => {
  try {
    new URL(string)
    return true
  } catch (e) {
    console.log('无效的URL:', e)
    return false
  }
}

// 头像验证规则
const avatarRules = [
  {
    validator: (value, callback) => {
      if (value && !isValidUrl(value)) {
        callback('请输入有效的图片URL地址')
        return
      }
      callback()
    }
  }
]

// 用户名验证规则
const userNameRules = [
  { required: true, message: '请输入用户昵称' },
  { min: 1, message: '昵称至少需要1个字符' },
  { max: 20, message: '昵称不能超过20个字符' }
]

// 监听对话框显示状态，重置表单
watch(
  () => props.visible,
  val => {
    if (val) {
      profileForm.userName = userStore.userName
      profileForm.avatar = userStore.avatar
      // 清除表单验证状态
      if (formRef.value) {
        formRef.value.clearValidate()
      }
    }
  }
)

// 处理表单提交
const handleEditProfile = async () => {
  try {
    // 验证表单
    const errors = await formRef.value.validate()
    if (errors) return

    loading.value = true

    const updateData = {
      user_id: userStore.userId
    }

    // 只有当值发生变化时才添加到更新数据中
    if (profileForm.userName !== userStore.userName) {
      updateData.user_name = profileForm.userName
    }
    if (profileForm.avatar && profileForm.avatar !== userStore.avatar) {
      updateData.avatar = profileForm.avatar
    }

    if (Object.keys(updateData).length === 1) {
      AMessage.info('没有需要更新的信息')
      emit('update:visible', false)
      return
    }

    const res = await userStore.updateUserInfo(updateData)
    if (res.success) {
      AMessage.success('个人资料更新成功')
      emit('update:visible', false)
    } else {
      AMessage.error(res.error || '个人资料更新失败')
    }
  } catch (error) {
    AMessage.error(error?.message || '个人资料更新失败')
  } finally {
    loading.value = false
  }
}

// 处理取消
const handleEditCancel = () => {
  // 重置表单
  profileForm.userName = userStore.userName
  profileForm.avatar = userStore.avatar
  emit('update:visible', false)
}
</script>

<style scoped>
/* 自定义样式 */
:deep(.arco-input-wrapper) {
  border-radius: 8px;
}

:deep(.arco-btn) {
  border-radius: 8px;
}
</style>
