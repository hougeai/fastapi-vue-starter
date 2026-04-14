<template>
  <a-modal
    :visible="visible"
    @cancel="handleCancel"
    :footer="null"
    :mask-closable="false"
    width="600px"
    class="rounded-2xl shadow-2xl"
    centered
  >
    <template #title>
      <div class="flex items-center justify-between pr-2">
        <icon-material-symbols:auto-detect-voice
          class="text-[var(--color-primary-light-4)] text-xl mr-1"
        />
        <div class="text-2xl font-bold">AI语音克隆 - 全球多语言支持</div>
      </div>
    </template>
    <!-- 顶部提示文本 -->
    <div class="text-center text-[var(--color-text-3)] mb-2">简单3步，创建您的专属AI语音</div>
    <!-- 步骤条 -->
    <div class="flex justify-center mb-6">
      <div class="flex items-center space-x-4">
        <div
          :class="[
            'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold',
            step >= 1 ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-500'
          ]"
        >
          1
        </div>
        <span class="text-gray-500">导入音频</span>
        <div
          :class="[
            'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold',
            step >= 2 ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-500'
          ]"
        >
          2
        </div>
        <span class="text-gray-500">识别和校对</span>
        <div
          :class="[
            'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold',
            step >= 3 ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-500'
          ]"
        >
          3
        </div>
        <span class="text-gray-500">克隆和保存</span>
      </div>
    </div>

    <!-- 内容区域 -->
    <div v-if="step === 1" class="space-y-2">
      <div class="flex items-center">
        <span class="text-base whitespace-nowrap">选择语种：</span>
        <a-select v-model="language" placeholder="请选择语种" style="width: 100%">
          <a-option
            v-for="option in props.languageOptions"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </a-option>
        </a-select>
      </div>

      <div class="text-red-500 text-sm">* 所选语言无法更改，请确保样本与所选语言一致。</div>

      <div class="mt-6">
        <!-- 选择输入方式 -->
        <div class="mb-4">
          <a-radio-group v-model="inputMethod" type="button">
            <a-radio value="upload">上传音频文件</a-radio>
            <a-radio value="record">麦克风录音</a-radio>
          </a-radio-group>
        </div>

        <!-- 上传音频 -->
        <div
          v-if="inputMethod === 'upload'"
          class="border-2 border-dashed border-[var(--color-primary-light-4)] rounded-lg p-4 text-center"
        >
          <a-upload
            :file-list="audioFileList"
            :show-file-list="true"
            :auto-upload="false"
            accept=".wav"
            :limit="1"
            @change="handleAudioFileChange"
            class="w-full mt-8"
          >
            <template #upload-button>
              <a-button type="outline" size="small" class="w-full">
                <template #icon>
                  <icon-material-symbols:cloud-upload />
                </template>
                选择音频文件
              </a-button>
            </template>
          </a-upload>
          <div class="ml-4 text-xs text-left text-[var(--color-text-3)]">
            <p>1.支持wav格式文件</p>
            <p>2.样本需包含连续不停顿、清晰的人声</p>
            <p>3.样本时长建议30秒以内，不宜过长</p>
          </div>
        </div>

        <!-- 麦克风录音 -->
        <div
          v-else
          class="border-2 border-dashed border-[var(--color-primary-light-4)] rounded-lg p-4 text-center"
        >
          <!-- 录音界面 -->
          <div
            class="flex flex-col items-center justify-center bg-white bg-opacity-95 transition-all duration-200"
          >
            <!-- 录音前 -->
            <div v-if="!isRecording && !recordedBlobUrl">
              <!-- 计时器 -->
              <div class="text-center text-xl font-mono mb-4">
                {{ recordingTime }}
              </div>

              <!-- 开始录音按钮 -->
              <a-button
                type="primary"
                size="large"
                style="border-radius: 0.5rem"
                @click="startRecording"
              >
                <template #icon><icon-material-symbols:mic /></template>
                开始录音
              </a-button>
            </div>

            <!-- 录音中 -->
            <div v-else-if="isRecording">
              <!-- 计时器 -->
              <div class="text-center text-xl font-mono mb-4">
                {{ recordingTime }}
              </div>

              <!-- 停止录音按钮 -->
              <a-button
                type="primary"
                size="large"
                style="border-radius: 0.5rem"
                @click="stopRecording"
              >
                <template #icon><icon-material-symbols:stop /></template>
                停止录音
              </a-button>
            </div>

            <!-- 录音完成后显示的音频播放界面 -->
            <div v-else-if="recordedBlobUrl">
              <!-- 音频播放器 -->
              <div class="text-center mb-4">
                <div class="text-xl font-mono">{{ recordingTime }}</div>
                <div class="flex items-center mt-2 justify-center">
                  <audio
                    ref="recordedAudioRef"
                    :src="recordedBlobUrl"
                    @ended="isPlaying = false"
                  ></audio>
                  <button
                    @click="isPlaying ? handleAudioPause() : handleAudioPlay()"
                    class="w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center"
                  >
                    <icon-material-symbols:play-arrow v-if="!isPlaying" />
                    <icon-material-symbols:pause v-else />
                  </button>
                </div>
              </div>

              <!-- 控制按钮 -->
              <div class="flex space-x-4 justify-center">
                <a-button @click="resetRecording">重置</a-button>
                <a-button type="primary" @click="confirmUseRecorded">确认使用</a-button>
              </div>
            </div>
          </div>
          <!-- 提示文本 -->
          <div class="text-center text-xs text-[var(--color-text-3)]">
            <p>1.用主播的语气和节奏读一段口播内容</p>
            <p>2.请确保您朗读的内容与设置语种一致</p>
            <p>3.避免环境嘈杂</p>
          </div>
        </div>
      </div>

      <div v-if="uploadedAudio" class="mt-4 text-green-600">
        已上传音频：{{ uploadedAudio.name }}
      </div>
    </div>

    <div v-else-if="step === 2">
      <!-- 识别结果展示 + 校对 -->
      <div class="mb-6">
        <p class="text-sm text-gray-500 mb-2">原始音频样本</p>
        <audio
          :src="`${getConfig('ossUrl')}/${refAudio}`"
          controls
          controlsList="nodownload"
          preload="none"
          class="w-full max-w-xs h-10"
          @contextmenu.prevent
        ></audio>
      </div>

      <!-- 识别结果 -->
      <div class="bg-gray-50 p-2 rounded-lg">
        <p>识别结果（请仔细校对，若与语音样本不一致，请手动修改。）</p>
        <textarea
          v-model="refText"
          class="w-96 h-32 p-3 border border-gray-300 rounded-lg"
          placeholder="请输入识别的文本内容..."
        ></textarea>
      </div>
    </div>
    <!-- 第三步：试听与配置 -->
    <div v-else-if="step === 3">
      <div class="mb-6">
        <p class="text-sm text-[var(--color-text-3)] mb-2">克隆完成（试听音频）：</p>
        <audio
          :src="`${getConfig('ossUrl')}/${audAudio}`"
          controls
          controlsList="nodownload"
          preload="none"
          class="w-full max-w-xs h-10"
          @contextmenu.prevent
        ></audio>
      </div>

      <div class="mb-4 text-sm text-[var(--color-text-3)]">试听文本：{{ audText }}</div>

      <!-- 表单：样本名称、性别、备注 -->
      <a-form
        :model="form"
        :rules="rules"
        ref="formRef"
        layout="horizontal"
        :label-col-props="{ span: 4 }"
        :label-align="left"
      >
        <a-form-item field="voiceName" label="名称" required>
          <a-input v-model="form.voiceName" placeholder="请输入音色名称" class="max-w-xs" />
        </a-form-item>

        <a-form-item field="gender" label="性别" required>
          <a-radio-group v-model="form.gender">
            <a-radio value="female">女性</a-radio>
            <a-radio value="male">男性</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item field="note" label="备注">
          <a-input v-model="form.note" placeholder="请输入备注(可选)" class="max-w-xs" />
        </a-form-item>
      </a-form>
    </div>
    <!-- 第四步：成功提示 -->
    <div v-else-if="step === 4">
      <div class="text-center mb-4">
        <icon-material-symbols:check-circle class="text-4xl text-green-500 mx-auto mb-2" />
        <p class="text-xl font-bold">语音克隆成功！</p>
      </div>
      <div class="text-center text-gray-500">已为您创建专属 AI 语音模型，可在音色管理中查看。</div>
      <div class="mt-6 text-right">
        <a-button type="primary" @click="finish">完成</a-button>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div v-if="step < 4" class="flex justify-end space-x-3 mt-6">
      <a-button v-if="step > 1" @click="prevStep">上一步</a-button>
      <a-button type="primary" @click="nextStep" :loading="loadingNext">
        {{ step === 3 ? '保存' : '下一步' }}
      </a-button>
    </div>
  </a-modal>
</template>

<script setup>
import { useVoiceStore } from '@/stores/voice'
import { getConfig } from '@/config/index'

const voiceStore = useVoiceStore()
const loadingNext = computed(() => voiceStore.loadingNext)
// Props
const props = defineProps({
  visible: Boolean,
  languageOptions: {
    type: Array,
    default: () => [
      { label: '英语', value: '英语' },
      { label: '中文', value: '中文' }
    ]
  }
})

const emit = defineEmits(['update:visible'])

// 监听对话框显示状态，重置数据
watch(
  () => props.visible,
  newVal => {
    if (newVal) {
      // 重置表单数据
      step.value = 1
      language.value = ''
      audioFileList.value = []
      uploadedAudio.value = null
      recordedBlobUrl.value = null
      isRecording.value = false
      isPlaying.value = false
      recordingTime.value = ''
      recordingStartTime.value = 0
      recordingElapsedTime.value = 0
      recordingTimer.value = null
      refText.value = ''
      refAudio.value = ''
      audAudio.value = ''
      audText.value = ''
      form.value = {
        voiceName: '',
        gender: '',
        note: ''
      }
      formRef.value?.clearValidate()
    }
  }
)

// 对话框控制
const step = ref(1)
const language = ref('')
const inputMethod = ref('upload')
const audioFileList = ref([])
const uploadedAudio = ref(null)
const recordedBlobUrl = ref(null)
const recordedAudioRef = ref(null)
const isRecording = ref(false)
const isPlaying = ref(false)

// 录音相关
const mediaRecorder = ref(null)
const chunks = ref([])
const recordingStartTime = ref(0)
const recordingElapsedTime = ref(0)
const recordingTimer = ref(null)
const minRecordingTime = 2 // 最小录音时间10秒
const recordingTime = computed(() => {
  const totalSeconds = recordingElapsedTime.value
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const secs = totalSeconds % 60

  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
})

// 第二/三步相关
const refText = ref('')
const refAudio = ref('')
const audAudio = ref('')
const audText = ref('')
// 表单相关
const formRef = ref()
const form = reactive({
  voiceName: '',
  gender: '',
  note: ''
})

const rules = {
  voiceName: [
    { required: true, message: '请输入音色名称' },
    { min: 1, max: 12, message: '样本名称长度应在1-12个字符之间', trigger: 'blur' }
  ],
  gender: [{ required: true, message: '请选择性别' }]
}

const handleCancel = () => {
  emit('update:visible', false)
}

const finish = () => {
  emit('update:visible', false)
}

// 上传音频处理
const handleAudioFileChange = fileList => {
  if (fileList.length > 0) {
    const file = fileList[0].file
    if (!file.type.includes('audio')) {
      AMessage.error('请选择音频文件')
      return
    }
    uploadedAudio.value = file
    audioFileList.value = fileList
  } else {
    uploadedAudio.value = null
    audioFileList.value = []
  }
}

// 音频播放相关
const handleAudioPlay = () => {
  if (recordedAudioRef.value) {
    recordedAudioRef.value.play()
    isPlaying.value = true
  }
}

const handleAudioPause = () => {
  if (recordedAudioRef.value) {
    recordedAudioRef.value.pause()
    isPlaying.value = false
  }
}

// 录音功能
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    chunks.value = []
    recordingStartTime.value = Date.now()
    recordingElapsedTime.value = 0
    // 启动计时器
    if (recordingTimer.value) {
      clearInterval(recordingTimer.value)
    }
    recordingTimer.value = setInterval(() => {
      recordingElapsedTime.value = Math.floor((Date.now() - recordingStartTime.value) / 1000)
    }, 1000)

    mediaRecorder.value.ondataavailable = e => {
      if (e.data.size > 0) {
        chunks.value.push(e.data)
      }
    }

    mediaRecorder.value.onstop = () => {
      // 停止计时器
      if (recordingTimer.value) {
        clearInterval(recordingTimer.value)
        recordingTimer.value = null
      }
      const blob = new Blob(chunks.value, { type: 'audio/wav' })
      recordedBlobUrl.value = URL.createObjectURL(blob)
      isRecording.value = false
    }

    mediaRecorder.value.start()
    isRecording.value = true
  } catch (error) {
    console.error(error)
    AMessage.error('无法访问麦克风，请检查权限')
    // 确保在出错时也清理计时器
    if (recordingTimer.value) {
      clearInterval(recordingTimer.value)
      recordingTimer.value = null
    }
    isRecording.value = false
  }
}

const stopRecording = () => {
  // 检查是否满足最小录音时间
  if (recordingElapsedTime.value < minRecordingTime) {
    AMessage.warning(`录音时间不能少于${minRecordingTime}秒`)
    return
  }
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    mediaRecorder.value.stream.getTracks().forEach(track => track.stop())
  }
}

const resetRecording = () => {
  // 停止播放
  if (recordedAudioRef.value) {
    recordedAudioRef.value.pause()
    isPlaying.value = false
  }

  // 重置录音状态
  isRecording.value = false
  recordingElapsedTime.value = 0
  chunks.value = []
  recordedBlobUrl.value = null
  isPlaying.value = false

  // 清理计时器
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value)
    recordingTimer.value = null
  }
}

const confirmUseRecorded = () => {
  // 将录制的音频转换为文件对象
  if (recordedBlobUrl.value) {
    const blob = new Blob(chunks.value, { type: 'audio/wav' })
    const file = new File([blob], 'recording.wav', { type: 'audio/wav' })
    uploadedAudio.value = file
    console.log('blob type', blob.type)
  }
}

// 下一步逻辑
const nextStep = async () => {
  if (!language.value) {
    AMessage.error('请选择语种')
    return
  }
  if (step.value === 1) {
    if (!uploadedAudio.value) {
      AMessage.error('请上传或录制一段语音')
      return
    }
    // 创建 FormData 对象，准备发送到后端
    const formData = new FormData()
    formData.append('audio_file', uploadedAudio.value)
    try {
      // 获取识别结果
      const result = await voiceStore.uploadAudio(formData)
      refAudio.value = result.ref_audio
      refText.value = result.ref_text
      step.value++
    } catch (error) {
      console.error(error)
    }
  } else if (step.value === 2) {
    // 创建 FormData 对象，准备发送到后端
    const formData = new FormData()
    formData.append('lang', language.value)
    formData.append('ref_audio', refAudio.value)
    try {
      const result = await voiceStore.cloneAudio(formData)
      audAudio.value = result.aud_audio
      audText.value = result.aud_text
      step.value++
    } catch (error) {
      console.error(error)
      AMessage.error('克隆失败，请重试')
    }
  } else if (step.value === 3) {
    const errors = await formRef.value.validate()
    if (errors) return
    const data = {
      name: form.voiceName,
      lang: language.value,
      gender: form.gender,
      ref_audio: refAudio.value,
      ref_text: refText.value,
      aud_audio: audAudio.value,
      aud_text: audText.value,
      note: form.note,
      source: 'user'
    }
    try {
      await voiceStore.createVoice(data)
      step.value++
    } catch (error) {
      console.error(error)
      AMessage.error('创建失败，请重试')
    }
  }
}

const prevStep = () => {
  if (step.value > 1) {
    step.value--
  }
}
</script>
