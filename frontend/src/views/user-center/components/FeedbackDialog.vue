<template>
  <a-modal
    :visible="visible"
    @cancel="handleCancel"
    :footer="null"
    :closable="false"
    width="540px"
    class="rounded-2xl shadow-2xl"
    centered
  >
    <div class="flex flex-col items-center py-2 px-2">
      <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-2">
        <icon-material-symbols:feedback class="text-3xl text-green-600" />
      </div>

      <div class="text-2xl font-bold mb-2">反馈建议</div>
      <div class="text-gray-500 text-sm mb-2 text-center">
        欢迎扫描下方二维码添加微信，向我们提出宝贵建议
      </div>

      <!-- 微信二维码 -->
      <div
        class="w-48 h-46 bg-gray-100 flex items-center justify-center rounded-2xl mb-2 border-2 border-dashed border-gray-300"
      >
        <img
          src="@/assets/img/qrcode_xiaoai.webp"
          alt="个人微信二维码"
          class="w-full h-full object-contain rounded-2xl"
        />
      </div>

      <!-- 联系方式说明 -->
      <div class="w-full bg-blue-50 rounded-xl p-4 mb-2">
        <div class="text-sm font-medium text-blue-800 mb-2 flex items-center">
          <icon-material-symbols:info class="mr-2" />
          联系方式
        </div>
        <div class="space-y-2 text-sm text-blue-700">
          <div class="flex items-center">
            <icon-ic:baseline-wechat class="mr-2 text-green-500" />
            <span>微信: 扫码添加好友</span>
          </div>
          <div class="flex items-center">
            <icon-material-symbols:schedule class="mr-2 text-orange-500" />
            <span>回复时间: 工作日 9:00-21:00</span>
          </div>
        </div>
      </div>

      <!-- 常见问题类型 -->
      <div class="w-full mb-2">
        <div class="text-sm font-medium text-gray-700 mb-2">您可以向我们反馈：</div>
        <div class="grid grid-cols-4 gap-2">
          <div class="bg-gray-50 rounded-lg p-3 text-center">
            <icon-material-symbols:bug-report class="text-red-500 text-xl mb-1" />
            <div class="text-xs text-gray-600">功能问题</div>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 text-center">
            <icon-material-symbols:lightbulb class="text-yellow-500 text-xl mb-1" />
            <div class="text-xs text-gray-600">功能建议</div>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 text-center">
            <icon-material-symbols:design-services class="text-blue-500 text-xl mb-1" />
            <div class="text-xs text-gray-600">界面优化</div>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 text-center">
            <icon-material-symbols:help class="text-purple-500 text-xl mb-1" />
            <div class="text-xs text-gray-600">使用帮助</div>
          </div>
        </div>
      </div>

      <!-- 快速反馈表单 -->
      <div class="w-full">
        <div class="text-sm font-medium text-gray-700 mb-2">或者在此快速留言：</div>
        <a-form :model="feedbackForm" @submit="handleSubmit">
          <a-form-item hide-label>
            <a-select
              v-model="feedbackForm.type"
              placeholder="选择反馈类型"
              size="large"
              class="w-full"
            >
              <a-option value="bug">功能问题</a-option>
              <a-option value="suggestion">功能建议</a-option>
              <a-option value="ui">界面优化</a-option>
              <a-option value="help">使用帮助</a-option>
              <a-option value="other">其他</a-option>
            </a-select>
          </a-form-item>

          <a-form-item hide-label>
            <a-textarea
              v-model="feedbackForm.content"
              placeholder="请详细描述您的问题或建议..."
              :rows="4"
              :max-length="500"
              show-word-limit
              class="w-full"
            />
          </a-form-item>

          <div class="flex space-x-3">
            <a-button type="outline" @click="handleCancel" class="flex-1 h-10"> 关闭 </a-button>
            <a-button
              type="primary"
              html-type="submit"
              :loading="loading"
              :disabled="!feedbackForm.content.trim()"
              class="flex-1 h-10"
            >
              提交反馈
            </a-button>
          </div>
        </a-form>
      </div>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const props = defineProps({
  visible: Boolean
})

const emit = defineEmits(['update:visible'])

const loading = ref(false)

const feedbackForm = ref({
  type: '',
  content: ''
})

// 监听对话框显示状态，重置表单
watch(
  () => props.visible,
  val => {
    if (val) {
      feedbackForm.value = {
        type: '',
        content: ''
      }
    }
  }
)

// 处理表单提交
const handleSubmit = async () => {
  if (!feedbackForm.value.content.trim()) {
    AMessage.warning('请输入反馈内容')
    return
  }

  loading.value = true

  try {
    // 这里可以调用反馈API
    await api.submitFeedback({
      user_id: userStore.userId,
      feed_type: feedbackForm.value.type,
      summary: feedbackForm.value.content
    })

    AMessage.success('反馈提交成功，我们会尽快处理您的建议！')
    handleCancel()
  } catch (error) {
    console.error(error)
    AMessage.error('提交失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 处理取消
const handleCancel = () => {
  emit('update:visible', false)
}
</script>

<style scoped>
/* 自定义样式 */
:deep(.arco-select-view-single) {
  border-radius: 8px;
}

:deep(.arco-textarea-wrapper) {
  border-radius: 8px;
}

:deep(.arco-btn) {
  border-radius: 8px;
}

/* 二维码容器样式 */
.qr-container {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
</style>
