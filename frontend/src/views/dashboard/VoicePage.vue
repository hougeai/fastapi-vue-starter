<script setup>
import { ref, computed } from 'vue'
import { useVoiceStore } from '@/stores/voice'
import { getConfig, getLanguageLabel } from '@/config/index'

const voiceStore = useVoiceStore()

const showVoiceCloneDialog = ref(false)
const showVoiceEditDialog = ref(false)
const currentEditVoice = ref({})
const currentPlayingAudio = ref(null) // 确保只有一个音频播放

// 处理音频播放事件：暂停其他音频，记录当前播放实例
const handleAudioPlay = audioElement => {
  // 如果有正在播放的音频，先暂停它
  if (currentPlayingAudio.value && currentPlayingAudio.value !== audioElement) {
    currentPlayingAudio.value.pause()
  }
  // 更新当前播放的音频实例
  currentPlayingAudio.value = audioElement
}

// 处理音频暂停事件：清空当前播放实例（如果是当前播放的音频）
const handleAudioPause = audioElement => {
  if (currentPlayingAudio.value === audioElement) {
    currentPlayingAudio.value = null
  }
}
// 获取音色数据
onMounted(async () => {
  try {
    await voiceStore.fetchVoices()
  } catch (error) {
    console.error('获取音色数据失败:', error)
  }
})

// 刷新数据
const refreshData = async () => {
  try {
    await voiceStore.refreshVoices()
  } catch (error) {
    console.error('刷新音色数据失败:', error)
  }
}

// 语言选项
const languageOptions = getConfig('languageOptions')

// 性别选项
const genderOptions = [
  { label: '全部性别', value: '全部性别' },
  { label: '男性', value: 'male' },
  { label: '女性', value: 'female' }
]
// 性别显示映射
const getGenderLabel = genderValue => {
  const genderMap = {
    male: '男',
    female: '女'
  }
  return genderMap[genderValue] || genderValue
}

// 筛选条件
const selectedLanguage = ref('全部语言')
const selectedGender = ref('全部性别')
const searchQuery = ref('')

// 计算属性
const voices = computed(() => voiceStore.voices)
const loading = computed(() => voiceStore.loading)

// 过滤后的音色列表
const filteredVoices = computed(() => {
  return voices.value.filter(voice => {
    const matchesLanguage =
      selectedLanguage.value === '全部语言' || voice.lang === selectedLanguage.value
    const matchesGender =
      selectedGender.value === '全部性别' || voice.gender === selectedGender.value
    const matchesSearch =
      voice.name.includes(searchQuery.value) || voice.lang.includes(searchQuery.value)
    return matchesLanguage && matchesGender && matchesSearch
  })
})

// 克隆新语音
const cloneNewVoice = () => {
  showVoiceCloneDialog.value = true
}
// 编辑音色
const editVoice = voice => {
  currentEditVoice.value = voice
  showVoiceEditDialog.value = true
}

// 删除音色
const deleteVoice = async voiceId => {
  AModal.confirm({
    title: '删除音色',
    content: '确定要删除当前音色吗？此操作不可恢复。',
    okText: '删除',
    cancelText: '取消',
    okButtonProps: { status: 'danger' },
    onOk: async () => {
      await voiceStore.deleteVoice(voiceId)
    }
  })
}
</script>

<template>
  <div class="w-full p-6 bg-[var(--color-fill-0)]">
    <!-- 顶部操作区 -->
    <div class="flex flex-wrap items-center mb-6 px-6 space-x-4">
      <a-select
        v-model="selectedLanguage"
        :options="languageOptions"
        style="width: 120px"
        size="large"
      />

      <a-select
        v-model="selectedGender"
        :options="genderOptions"
        style="width: 120px"
        size="large"
      />

      <a-input-search
        v-model="searchQuery"
        placeholder="请输入音色名称检索"
        style="flex: 1; max-width: 200px"
        size="large"
      />

      <a-button type="primary" size="large" style="border-radius: 0.5rem" @click="cloneNewVoice">
        <template #icon><icon-ri-add-circle-line /></template>
        克隆新语音
      </a-button>

      <a-button type="outline" size="large" shape="round" :loading="loading" @click="refreshData">
        <template #icon>
          <icon-material-symbols:refresh />
        </template>
        刷新
      </a-button>
    </div>

    <!-- 音色卡片列表 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 px-6">
      <div
        v-for="voice in filteredVoices"
        :key="voice.id"
        class="flex-shrink-0 border px-3 py-3 rounded-lg duration-200 bg-gradient-to-br from-blue-50 to-purple-50/30 bg-blue-200 shadow-md cursor-pointer hover:shadow-xl transition-all duration-300"
      >
        <div class="flex items-center justify-between">
          <h3 class="text-base font-semibold">{{ voice.name }}</h3>
          <!-- 编辑和删除按钮，仅当source为'user'时显示 -->
          <div v-if="voice.source === 'user'" class="flex">
            <a-tooltip content="编辑音色">
              <a-button
                type="text"
                size="small"
                shape="circle"
                :loading="voiceStore.loadingEdit"
                @click.stop="editVoice(voice)"
              >
                <template #icon><icon-material-symbols:contract-edit /></template>
              </a-button>
            </a-tooltip>
            <a-tooltip content="删除音色">
              <a-button
                type="text"
                size="small"
                status="danger"
                shape="circle"
                :loading="voiceStore.loadingDelete"
                @click.stop="deleteVoice(voice.id)"
              >
                <template #icon><icon-material-symbols:delete-outline /></template>
              </a-button>
            </a-tooltip>
          </div>
          <a-tag v-else color="green">官方</a-tag>
        </div>

        <div class="space-y-2 text-sm text-[var(--color-text-3)]">
          <div>性别：{{ getGenderLabel(voice.gender) }}</div>
          <div>语种：{{ getLanguageLabel(voice.lang) }}</div>
          <div>创建时间：{{ voice.create_at }}</div>
          <div>备注：{{ voice.note }}</div>
        </div>

        <!-- 播放器 -->
        <div class="mt-4">
          <div v-if="voice.aud_audio" class="w-full">
            <audio
              :src="`${getConfig('ossUrl')}/${voice.aud_audio}`"
              controls
              controlsList="nodownload"
              preload="none"
              class="w-full max-w-xs h-8"
              @contextmenu.prevent
              @play="handleAudioPlay($event.target)"
              @pause="handleAudioPause($event.target)"
              @ended="handleAudioEnd($event.target)"
            >
              您的浏览器不支持音频播放
            </audio>
          </div>
          <span v-else class="text-gray-400">无播放链接</span>
        </div>
      </div>
    </div>

    <!-- 音色克隆对话框 -->
    <VoiceCloneDialog
      v-model:visible="showVoiceCloneDialog"
      :language-options="languageOptions.filter(opt => opt.value !== '全部语言')"
    />
    <!-- 音色编辑对话框 -->
    <VoiceEditDialog
      v-model:visible="showVoiceEditDialog"
      :language-options="languageOptions.filter(opt => opt.value !== '全部语言')"
      :voice="currentEditVoice"
    />
  </div>
</template>

<style scoped>
/* 添加一些样式优化 */
@media (max-width: 768px) {
  .grid-cols-5 {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
