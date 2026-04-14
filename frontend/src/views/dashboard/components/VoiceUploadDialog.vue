<template>
  <a-modal
    :visible="visible"
    @cancel="handleCancel"
    :footer="null"
    :closable="false"
    width="520px"
    class="rounded-2xl shadow-2xl"
    centered
  >
    <div class="flex flex-col items-center py-6 px-2">
      <!-- 图标和标题 -->
      <div class="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mb-3">
        <icon-material-symbols:upload class="text-2xl text-green-600" />
      </div>
      <div class="text-xl font-extrabold mb-2">手动上传歌曲</div>
      <div class="text-gray-500 text-sm mb-4">上传您的音乐文件并添加到歌单</div>

      <!-- 上传表单 -->
      <a-form
        :model="uploadForm"
        layout="vertical"
        @submit="handleUpload"
        class="w-full mt-4"
        ref="formRef"
      >
        <!-- 基本信息 -->
        <div class="grid grid-cols-2 gap-4">
          <a-form-item field="song" :rules="songRules" class="mb-4" hide-label>
            <a-input
              v-model="uploadForm.song"
              placeholder="歌曲名 *"
              allow-clear
              size="large"
              class="h-10"
            />
          </a-form-item>

          <a-form-item field="singer" :rules="singerRules" class="mb-4" hide-label>
            <a-input
              v-model="uploadForm.singer"
              placeholder="歌手名 *"
              allow-clear
              size="large"
              class="h-10"
            />
          </a-form-item>
        </div>

        <!-- 文件上传区域 -->
        <div class="mb-3">
          <!-- 音频文件上传 -->
          <a-form-item field="audioFile" :rules="audioFileRules" hide-label>
            <div class="flex items-center space-x-3">
              <div class="text-sm text-gray-600 flex items-center min-w-0 flex-shrink-0">
                <icon-material-symbols:audio-file class="mr-1" />
                音频文件 (必填)：
              </div>
              <div class="flex-1">
                <a-upload
                  :file-list="audioFileList"
                  :show-file-list="true"
                  :auto-upload="false"
                  accept=".mp3"
                  :limit="1"
                  @change="handleAudioFileChange"
                  @remove="handleAudioFileRemove"
                  class="w-full"
                >
                  <template #upload-button>
                    <a-button type="outline" size="small" class="w-full">
                      <template #icon>
                        <icon-material-symbols:cloud-upload />
                      </template>
                      选择MP3文件 (≤5MB)
                    </a-button>
                  </template>
                </a-upload>
              </div>
            </div>
          </a-form-item>

          <!-- 封面图片上传 -->
          <a-form-item field="coverFile">
            <div class="flex items-center space-x-3">
              <div class="text-sm text-gray-600 flex items-center min-w-0 flex-shrink-0">
                <icon-material-symbols:image class="mr-1" />
                封面图片(可选)：
              </div>
              <div class="flex-1">
                <a-upload
                  :file-list="coverFileList"
                  :show-file-list="true"
                  :auto-upload="false"
                  accept="image/*"
                  :limit="1"
                  @change="handleCoverFileChange"
                  @remove="handleCoverFileRemove"
                  class="w-full"
                >
                  <template #upload-button>
                    <a-button type="outline" size="small" class="w-full">
                      <template #icon>
                        <icon-material-symbols:add-photo-alternate />
                      </template>
                      选择JPG图片 (≤1MB)
                    </a-button>
                  </template>
                </a-upload>
              </div>
            </div>
          </a-form-item>

          <!-- 歌词文件上传 -->
          <a-form-item field="lyricFile">
            <div class="flex items-center space-x-3">
              <div class="text-sm text-gray-600 flex items-center min-w-0 flex-shrink-0">
                <icon-material-symbols:lyrics class="mr-1" />
                歌词文件(可选)：
              </div>
              <div class="flex-1">
                <a-upload
                  :file-list="lyricFileList"
                  :show-file-list="true"
                  :auto-upload="false"
                  accept=".txt"
                  :limit="1"
                  @change="handleLyricFileChange"
                  @remove="handleLyricFileRemove"
                  class="w-full"
                >
                  <template #upload-button>
                    <a-button type="outline" size="small" class="w-full">
                      <template #icon>
                        <icon-material-symbols:text-snippet />
                      </template>
                      选择TXT文件 (≤10KB)
                    </a-button>
                  </template>
                </a-upload>
              </div>
            </div>
          </a-form-item>
        </div>

        <!-- 上传结果显示 -->
        <div
          v-if="uploadResult"
          class="mb-6 p-4 rounded-lg"
          :class="
            uploadResult.success
              ? 'bg-green-50 border border-green-200'
              : 'bg-red-50 border border-red-200'
          "
        >
          <div class="flex items-center mb-2">
            <icon-material-symbols:check-circle
              v-if="uploadResult.success"
              class="text-green-600 mr-2"
            />
            <icon-material-symbols:error v-else class="text-red-600 mr-2" />
            <span
              class="font-medium"
              :class="uploadResult.success ? 'text-green-800' : 'text-red-800'"
            >
              {{ uploadResult.success ? '上传成功！' : '上传失败' }}
            </span>
          </div>
          <div class="text-sm" :class="uploadResult.success ? 'text-green-700' : 'text-red-700'">
            {{ uploadResult.message }}
          </div>
          <div v-if="uploadResult.success && uploadResult.data" class="mt-2 text-sm text-green-700">
            <div>歌曲时长: {{ formatDuration(uploadResult.data.duration) }}</div>
          </div>
        </div>

        <!-- 设备选择器 -->
        <div class="w-full mb-6" v-if="uploadResult && uploadResult.success">
          <div class="text-sm text-gray-600 mb-2 flex items-center">
            <icon-material-symbols:devices class="mr-1" />
            选择要添加歌曲的设备
          </div>
          <a-select
            v-model="selectedDeviceIds"
            placeholder="请选择要添加歌曲的设备（可多选）"
            size="large"
            class="w-full"
            :loading="loadingDevices"
            allow-clear
            multiple
          >
            <a-option
              v-for="device in devices"
              :key="device.device_id"
              :value="device.device_id"
              :label="`${device.note} (${device.device_id})`"
            >
              <div class="flex items-center justify-between">
                <span>{{ device.note }}</span>
                <span class="text-xs text-gray-400 ml-1">{{ device.device_id }}</span>
              </div>
            </a-option>
          </a-select>

          <!-- 无设备提示 -->
          <div
            v-if="!loadingDevices && devices.length === 0"
            class="mt-2 text-sm text-orange-600 bg-orange-50 p-2 rounded"
          >
            <icon-material-symbols:warning class="mr-1" />
            暂无可用设备，请先前往首页添加设备后再操作
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex space-x-3">
          <a-button type="outline" @click="handleCancel" class="flex-1 h-12 text-16px">
            取消
          </a-button>

          <!-- 上传按钮 -->
          <a-button
            v-if="!uploadResult || !uploadResult.success"
            type="primary"
            html-type="submit"
            :loading="uploading"
            class="flex-1 h-12 text-16px font-bold"
          >
            <template #icon>
              <icon-material-symbols:upload />
            </template>
            上传歌曲
          </a-button>

          <!-- 添加到设备按钮 -->
          <a-button
            v-else
            type="primary"
            @click="handleAddToDevices"
            :loading="addingToDevices"
            :disabled="selectedDeviceIds.length === 0"
            class="flex-1 h-12 text-16px font-bold"
          >
            <template #icon>
              <icon-material-symbols:add />
            </template>
            添加到设备 ({{ selectedDeviceIds.length }})
          </a-button>
        </div>
      </a-form>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useMusicStore } from '@/stores/music'
import { useUserStore } from '@/stores/user'
import { useDeviceStore } from '@/stores/device'
import { formatDuration } from '@/utils/common'

// Props
const props = defineProps({
  visible: Boolean
})

// Emits
const emit = defineEmits(['update:visible', 'upload-success'])

// Stores
const musicStore = useMusicStore()
const userStore = useUserStore()
const deviceStore = useDeviceStore()

// 响应式数据
const uploadForm = ref({
  song: '',
  singer: ''
})

const audioFileList = ref([])
const coverFileList = ref([])
const lyricFileList = ref([])

const uploading = ref(false)
const uploadResult = ref(null)
const addingToDevices = ref(false)
const selectedDeviceIds = ref([])
const devices = ref([])
const loadingDevices = ref(false)

// 表单引用
const formRef = ref()

// 计算属性
const userId = computed(() => userStore.userId)

// 验证规则
const songRules = [
  { required: true, message: '请输入歌曲名' },
  { min: 1, max: 100, message: '歌曲名长度应在1-100个字符之间' }
]

const singerRules = [
  { required: true, message: '请输入歌手名' },
  { min: 1, max: 50, message: '歌手名长度应在1-50个字符之间' }
]

const audioFileRules = [{ required: true, message: '请选择音频文件' }]

// 文件验证
const validateFileSize = (file, maxSize, unit = 'MB') => {
  const maxBytes = unit === 'KB' ? maxSize * 1024 : maxSize * 1024 * 1024
  return file.size <= maxBytes
}

const validateFileType = (file, allowedTypes) => {
  return allowedTypes.some(type => {
    if (type.startsWith('.')) {
      return file.name.toLowerCase().endsWith(type.toLowerCase())
    }
    return file.type.startsWith(type)
  })
}

// 音频文件处理
const handleAudioFileChange = fileList => {
  if (fileList.length > 0) {
    const file = fileList[0].file

    // 验证文件类型
    if (!validateFileType(file, ['.mp3', 'audio/mp3', 'audio/mpeg'])) {
      AMessage.error('请选择MP3格式的音频文件')
      audioFileList.value = []
      return
    }

    // 验证文件大小
    if (!validateFileSize(file, 5, 'MB')) {
      AMessage.error('音频文件大小不能超过5MB')
      audioFileList.value = []
      return
    }

    audioFileList.value = fileList
    uploadForm.value.audioFile = file
  }
}

const handleAudioFileRemove = () => {
  audioFileList.value = []
  uploadForm.value.audioFile = null
}

// 封面图片处理
const handleCoverFileChange = fileList => {
  if (fileList.length > 0) {
    const file = fileList[0].file

    // 验证文件类型
    if (!validateFileType(file, ['image/'])) {
      AMessage.error('请选择图片文件')
      coverFileList.value = []
      return
    }

    // 验证文件大小
    if (!validateFileSize(file, 1, 'MB')) {
      AMessage.error('封面图片大小不能超过1MB')
      coverFileList.value = []
      return
    }

    coverFileList.value = fileList
    uploadForm.value.coverFile = file
  }
}

const handleCoverFileRemove = () => {
  coverFileList.value = []
  uploadForm.value.coverFile = null
}

// 歌词文件处理
const handleLyricFileChange = fileList => {
  if (fileList.length > 0) {
    const file = fileList[0].file

    // 验证文件类型
    if (!validateFileType(file, ['.txt', 'text/plain'])) {
      AMessage.error('请选择TXT格式的歌词文件')
      lyricFileList.value = []
      return
    }

    // 验证文件大小
    if (!validateFileSize(file, 10, 'KB')) {
      AMessage.error('歌词文件大小不能超过10KB')
      lyricFileList.value = []
      return
    }

    lyricFileList.value = fileList
    uploadForm.value.lyricFile = file
  }
}

const handleLyricFileRemove = () => {
  lyricFileList.value = []
  uploadForm.value.lyricFile = null
}

// 监听对话框显示状态，重置数据
watch(
  () => props.visible,
  async val => {
    if (val) {
      // 重置表单
      uploadForm.value = {
        song: '',
        singer: ''
      }

      // 重置文件列表
      audioFileList.value = []
      coverFileList.value = []
      lyricFileList.value = []

      // 重置状态
      uploading.value = false
      uploadResult.value = null
      addingToDevices.value = false
      selectedDeviceIds.value = []

      // 清除表单验证状态
      if (formRef.value) {
        formRef.value.clearValidate()
      }

      // 加载设备列表
      await loadDevices()
    }
  }
)

// 上传歌曲
const handleUpload = async () => {
  const errors = await formRef.value.validate()
  if (errors) return

  if (!uploadForm.value.audioFile) {
    AMessage.error('请选择音频文件')
    return
  }

  uploading.value = true
  uploadResult.value = null

  try {
    // 创建 FormData
    const formData = new FormData()
    formData.append('song', uploadForm.value.song.trim())
    formData.append('singer', uploadForm.value.singer.trim())
    formData.append('audioFile', uploadForm.value.audioFile)

    if (uploadForm.value.coverFile) {
      formData.append('coverFile', uploadForm.value.coverFile)
    }

    if (uploadForm.value.lyricFile) {
      formData.append('lyricFile', uploadForm.value.lyricFile)
    }

    // 调用上传接口
    const result = await musicStore.uploadMusic(formData)

    uploadResult.value = {
      success: true,
      message: '歌曲上传成功！您可以选择设备将其添加到歌单中。',
      data: result
    }
    AMessage.success('歌曲上传成功！')
  } catch (error) {
    console.error('上传失败:', error)
    uploadResult.value = {
      success: false,
      message: error.message || '上传失败，请重试'
    }
  } finally {
    uploading.value = false
  }
}

// 添加到设备
const handleAddToDevices = async () => {
  if (selectedDeviceIds.value.length === 0) {
    AMessage.warning('请先选择设备')
    return
  }

  if (!uploadResult.value?.data?.id) {
    AMessage.error('歌曲信息异常，请重新上传')
    return
  }

  addingToDevices.value = true
  try {
    // 为每个选中的设备添加歌曲
    const promises = selectedDeviceIds.value.map(deviceId =>
      musicStore.addToCollection({
        user_id: userId.value,
        device_id: deviceId,
        song_id: uploadResult.value.data.id
      })
    )

    await Promise.all(promises)

    AMessage.success(
      `《${uploadForm.value.song}》已添加到 ${selectedDeviceIds.value.length} 个设备的歌单`
    )

    // 通知父组件上传成功
    emit('upload-success')

    // 关闭对话框
    emit('update:visible', false)
  } catch (error) {
    console.error('添加到设备失败:', error)
    AMessage.error('添加到设备失败')
  } finally {
    addingToDevices.value = false
  }
}

// 关闭对话框
const handleCancel = () => {
  emit('update:visible', false)
}

// 加载设备列表
const loadDevices = async () => {
  if (!userId.value) return

  try {
    loadingDevices.value = true
    const deviceList = await deviceStore.fetchDevices(userId.value)
    devices.value = deviceList || []

    // 如果只有一个设备，自动选择
    if (devices.value.length === 1) {
      selectedDeviceIds.value = [devices.value[0].device_id]
    }
  } catch (error) {
    console.error('加载设备列表失败:', error)
    AMessage.error('加载设备列表失败')
  } finally {
    loadingDevices.value = false
  }
}
</script>

<style scoped>
:deep(.arco-input-wrapper) {
  border-radius: 8px;
}

:deep(.arco-btn) {
  border-radius: 8px;
}

:deep(.arco-upload-list-item) {
  border-radius: 6px;
}

:deep(.arco-upload-list-item-name) {
  font-size: 14px;
}

:deep(.arco-select-view-single) {
  border-radius: 8px;
}

/* 上传区域样式 */
:deep(.arco-upload-drag) {
  border-radius: 8px;
}

/* 文件列表样式 */
:deep(.arco-upload-list) {
  margin-top: 8px;
}

/* 结果显示区域动画 */
.upload-result-enter-active,
.upload-result-leave-active {
  transition: all 0.3s ease;
}

.upload-result-enter-from,
.upload-result-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
