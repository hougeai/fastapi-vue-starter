<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLedgerStore } from '@/stores/ledger'
import { useTransactionStore } from '@/stores/transaction'
import api from '@/api'
import dayjs from 'dayjs'

const router = useRouter()
const ledgerStore = useLedgerStore()
const transactionStore = useTransactionStore()

const loading = ref(false)
const showLedgerDropdown = ref(false)

// 当前输入模式：text | voice | image
const inputMode = ref('text')

// ---- 文本输入 ----
const textInput = ref('')
const textLoading = ref(false)

// ---- 语音输入 ----
const isRecording = ref(false)
const voiceLoading = ref(false)
const voiceTranscript = ref('')
let mediaRecorder = null
let audioChunks = []

// ---- 图片输入 ----
const imageFile = ref(null)
const imagePreview = ref('')
const imageLoading = ref(false)

// ---- AI 解析结果 ----
const parsedResult = ref(null)
const parseError = ref('')

// ---- 确认表单 ----
const confirmVisible = ref(false)
const confirmForm = ref({
  tx_type: 2,
  amount: 0,
  category: '',
  remark: '',
  tx_date: ''
})

const currentLedger = computed(() => ledgerStore.currentLedger)
const ledgers = computed(() => ledgerStore.ledgers)

// 金额格式化
const formatMoney = (amount) => {
  return amount != null ? Number(amount).toFixed(2) : '0.00'
}

// 切换账本
const switchLedger = (ledger) => {
  ledgerStore.setCurrentLedger(ledger)
  showLedgerDropdown.value = false
}

// ======== 文本解析 ========
const handleTextParse = async () => {
  if (!textInput.value.trim() || !currentLedger.value) return
  textLoading.value = true
  parseError.value = ''
  parsedResult.value = null
  try {
    const res = await api.aiParseText({
      text: textInput.value.trim(),
      ledger_id: currentLedger.value.id
    })
    if (res.code === 200 && res.data) {
      parsedResult.value = res.data
      fillConfirmForm(res.data)
      confirmVisible.value = true
    } else {
      parseError.value = res.msg || '无法识别交易信息，请手动输入'
    }
  } catch (e) {
    parseError.value = '解析失败，请稍后重试或手动输入'
  } finally {
    textLoading.value = false
  }
}

// ======== 语音录制 ========
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    audioChunks = []
    mediaRecorder.ondataavailable = (e) => {
      audioChunks.push(e.data)
    }
    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' })
      stream.getTracks().forEach(t => t.stop())
      await handleVoiceParse(blob)
    }
    mediaRecorder.start()
    isRecording.value = true
  } catch (e) {
    parseError.value = '无法访问麦克风，请检查权限设置'
  }
}

const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  isRecording.value = false
}

const handleVoiceParse = async (blob) => {
  if (!currentLedger.value) return
  voiceLoading.value = true
  parseError.value = ''
  parsedResult.value = null
  try {
    const formData = new FormData()
    formData.append('file', blob)
    formData.append('ledger_id', currentLedger.value.id)
    const res = await api.aiParseVoice(formData)
    if (res.code === 200 && res.data) {
      voiceTranscript.value = res.data.transcript || ''
      if (res.data.parsed) {
        parsedResult.value = res.data.parsed
        fillConfirmForm(res.data.parsed)
        confirmVisible.value = true
      } else {
        parseError.value = '语音识别成功但无法解析为交易记录'
      }
    } else {
      parseError.value = res.msg || '语音识别失败'
    }
  } catch (e) {
    parseError.value = '语音解析失败，请稍后重试'
  } finally {
    voiceLoading.value = false
  }
}

// ======== 图片上传 ========
const handleImageSelect = (file) => {
  if (file && file.file) {
    imageFile.value = file.file
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file.file)
    // 自动解析
    handleImageParse(file.file)
  }
  return false
}

const clearImage = () => {
  imageFile.value = null
  imagePreview.value = ''
  parsedResult.value = null
  parseError.value = ''
}

const handleImageParse = async (file) => {
  if (!currentLedger.value) return
  imageLoading.value = true
  parseError.value = ''
  parsedResult.value = null
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('ledger_id', currentLedger.value.id)
    const res = await api.aiParseImage(formData)
    if (res.code === 200 && res.data?.parsed) {
      parsedResult.value = res.data.parsed
      fillConfirmForm(res.data.parsed)
      confirmVisible.value = true
    } else {
      parseError.value = res.msg || '无法识别图片中的交易信息'
    }
  } catch (e) {
    parseError.value = '图片解析失败，请稍后重试'
  } finally {
    imageLoading.value = false
  }
}

// ======== 确认表单 ========
const fillConfirmForm = (data) => {
  confirmForm.value = {
    tx_type: data.tx_type || 2,
    amount: data.amount || 0,
    category: data.category || '',
    remark: data.remark || '',
    tx_date: data.tx_date || dayjs().format('YYYY-MM-DD')
  }
}

// 确认保存
const handleConfirmSave = async () => {
  if (!currentLedger.value) return
  loading.value = true
  try {
    const data = {
      ledger_id: currentLedger.value.id,
      tx_type: confirmForm.value.tx_type,
      amount: confirmForm.value.amount,
      remark: confirmForm.value.remark,
      tx_date: confirmForm.value.tx_date
    }
    // 如果有类别名称，尝试匹配类别ID（后端处理）
    if (confirmForm.value.category) {
      data.category_name = confirmForm.value.category
    }
    const res = await api.createTransaction(data)
    if (res.code === 200) {
      confirmVisible.value = false
      // 重置
      textInput.value = ''
      voiceTranscript.value = ''
      imageFile.value = null
      imagePreview.value = ''
      parsedResult.value = null
      parseError.value = ''
      // 刷新交易列表
      await transactionStore.fetchTransactions({ ledgerId: currentLedger.value.id, pageSize: 20 })
    }
  } finally {
    loading.value = false
  }
}

// 初始化
onMounted(async () => {
  if (!ledgerStore.ledgers.length) {
    await ledgerStore.fetchLedgerList()
  }
  if (!currentLedger.value && ledgerStore.ledgers.length) {
    ledgerStore.currentLedger = ledgerStore.ledgers.find(l => l.is_default) || ledgerStore.ledgers[0]
  }
})
</script>

<template>
  <div class="w-full min-h-screen bg-[var(--color-fill-1)]">
    <!-- 顶部区域 -->
    <div class="bg-gradient-to-br from-cyan-50 via-teal-50 to-white px-6 pt-6 pb-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-[var(--color-text-1)]">AI 记账</h1>
          <a-dropdown v-model:popup-visible="showLedgerDropdown" trigger="click" :disabled="ledgers.length === 0">
            <div class="flex items-center gap-1 cursor-pointer bg-white rounded-full px-3 py-1 shadow-sm border border-[var(--color-border-2)]">
              <icon-material-symbols:account-balance-wallet-outline class="text-sm text-cyan-500" />
              <span class="text-sm font-medium text-[var(--color-text-1)]">{{ currentLedger?.name || '请选择' }}</span>
              <icon-material-symbols:keyboard-arrow-down v-if="ledgers.length" class="text-sm text-[var(--color-text-3)]" />
            </div>
            <template #content>
              <a-doption
                v-for="ledger in ledgers"
                :key="ledger.id"
                @click="switchLedger(ledger)"
              >
                <div class="flex items-center justify-between w-full">
                  <span>{{ ledger.name }}</span>
                  <a-tag v-if="ledger.is_default" size="small" color="arcoblue">默认</a-tag>
                </div>
              </a-doption>
            </template>
          </a-dropdown>
        </div>
      </div>

      <!-- 输入模式切换 -->
      <div class="mt-4">
        <a-radio-group v-model="inputMode" type="button" size="small">
          <a-radio value="text"><icon-material-symbols:chat-outline class="align-middle" /> 文本</a-radio>
          <a-radio value="voice"><icon-material-symbols:mic-outline class="align-middle" /> 语音</a-radio>
          <a-radio value="image"><icon-material-symbols:image-outline class="align-middle" /> 图片</a-radio>
        </a-radio-group>
      </div>
    </div>

    <div class="px-4 pt-4 pb-4">
      <!-- 无账本提示 -->
      <div v-if="!currentLedger && !ledgers.length" class="bg-[var(--color-bg-2)] rounded-xl p-8 shadow-sm text-center">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-cyan-100 flex items-center justify-center">
          <icon-material-symbols:account-balance-wallet-outline class="text-3xl text-cyan-500" />
        </div>
        <h3 class="text-lg font-semibold text-[var(--color-text-1)] mb-2">请先选择账本</h3>
        <p class="text-sm text-[var(--color-text-3)] mb-4">选择一个账本后即可使用 AI 记账</p>
        <a-button type="primary" @click="router.push('/ledgers')">去管理账本</a-button>
      </div>

      <template v-else>
        <!-- ====== 文本输入模式 ====== -->
        <template v-if="inputMode === 'text'">
          <div class="bg-[var(--color-bg-2)] rounded-xl shadow-sm p-4">
            <div class="text-sm font-medium text-[var(--color-text-1)] mb-3">描述你的收支</div>
            <a-textarea
              v-model="textInput"
              placeholder="例如：今天午饭花了30元、6月工资到账15000、打车去公司25块..."
              :auto-size="{ minRows: 3, maxRows: 6 }"
              :disabled="textLoading"
            />
            <div class="flex justify-end mt-3">
              <a-button
                type="primary"
                :loading="textLoading"
                :disabled="!textInput.trim()"
                @click="handleTextParse"
              >
                <template #icon><icon-material-symbols:auto-awesome-outline /></template>
                AI 解析
              </a-button>
            </div>
            <!-- 快捷示例 -->
            <div class="mt-3">
              <div class="text-xs text-[var(--color-text-3)] mb-2">试试这些：</div>
              <div class="flex flex-wrap gap-2">
                <a-tag
                  v-for="example in ['今天午饭花了30元', '6月工资到账15000', '打车去公司25块', '超市购物花了188']"
                  :key="example"
                  color="cyan"
                  class="cursor-pointer"
                  @click="textInput = example"
                >
                  {{ example }}
                </a-tag>
              </div>
            </div>
          </div>
        </template>

        <!-- ====== 语音输入模式 ====== -->
        <template v-else-if="inputMode === 'voice'">
          <div class="bg-[var(--color-bg-2)] rounded-xl shadow-sm p-6">
            <div class="text-sm font-medium text-[var(--color-text-1)] mb-4 text-center">语音记账</div>
            <!-- 录音按钮 -->
            <div class="flex flex-col items-center">
              <div
                class="w-20 h-20 rounded-full flex items-center justify-center cursor-pointer transition-all shadow-lg"
                :class="isRecording ? 'bg-red-500 animate-pulse' : 'bg-cyan-500 hover:bg-cyan-600'"
                @click="isRecording ? stopRecording() : startRecording()"
              >
                <icon-material-symbols:mic v-if="!isRecording" class="text-3xl text-white" />
                <icon-material-symbols:stop v-else class="text-3xl text-white" />
              </div>
              <span class="mt-3 text-sm text-[var(--color-text-3)]">
                {{ isRecording ? '点击停止录音' : '点击开始录音' }}
              </span>
            </div>

            <!-- 语音识别结果 -->
            <div v-if="voiceTranscript" class="mt-4 bg-[var(--color-fill-2)] rounded-lg p-3">
              <div class="text-xs text-[var(--color-text-3)] mb-1">识别结果：</div>
              <div class="text-sm text-[var(--color-text-1)]">{{ voiceTranscript }}</div>
            </div>

            <!-- 加载中 -->
            <div v-if="voiceLoading" class="mt-4 text-center">
              <a-spin :loading="true" />
              <p class="text-sm text-[var(--color-text-3)] mt-2">正在识别语音...</p>
            </div>
          </div>
        </template>

        <!-- ====== 图片输入模式 ====== -->
        <template v-else-if="inputMode === 'image'">
          <div class="bg-[var(--color-bg-2)] rounded-xl shadow-sm p-4">
            <div class="text-sm font-medium text-[var(--color-text-1)] mb-3">上传小票/账单</div>

            <!-- 图片预览 -->
            <div v-if="imagePreview" class="relative mb-3">
              <img :src="imagePreview" class="w-full rounded-lg max-h-60 object-contain bg-[var(--color-fill-2)]" />
              <a-button
                type="primary"
                shape="circle"
                size="mini"
                status="danger"
                class="absolute top-2 right-2"
                @click="clearImage"
              >
                <template #icon><icon-material-symbols:close /></template>
              </a-button>
            </div>

            <!-- 上传区域 -->
            <a-upload
              v-if="!imagePreview"
              :auto-upload="false"
              :show-file-list="false"
              accept="image/jpeg,image/png,image/heic"
              @before-upload="handleImageSelect"
              draggable
            >
              <template #upload-button>
                <div class="flex flex-col items-center justify-center py-8 border-2 border-dashed border-[var(--color-border-2)] rounded-lg cursor-pointer hover:border-cyan-400 transition-colors">
                  <icon-material-symbols:add-photo-alternate-outline class="text-4xl text-[var(--color-text-4)] mb-2" />
                  <div class="text-sm text-[var(--color-text-3)]">点击或拖拽上传小票图片</div>
                  <div class="text-xs text-[var(--color-text-4)] mt-1">支持 JPEG/PNG/HEIC，不超过 10MB</div>
                </div>
              </template>
            </a-upload>

            <!-- 加载中 -->
            <div v-if="imageLoading" class="mt-3 text-center">
              <a-spin :loading="true" />
              <p class="text-sm text-[var(--color-text-3)] mt-2">正在识别图片...</p>
            </div>
          </div>
        </template>

        <!-- 解析错误提示 -->
        <div v-if="parseError" class="mt-4 bg-red-50 border border-red-200 rounded-xl p-4">
          <div class="flex items-start gap-2">
            <icon-material-symbols:error-outline class="text-lg text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <div class="text-sm font-medium text-red-600">解析失败</div>
              <div class="text-xs text-red-500 mt-1">{{ parseError }}</div>
              <a-button type="text" size="small" class="mt-2" @click="router.push('/transactions')">
                去手动记一笔 →
              </a-button>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- ====== 确认弹窗 ====== -->
    <a-modal
      v-model:visible="confirmVisible"
      title="确认交易信息"
      :mask-closable="false"
      @ok="handleConfirmSave"
      :ok-loading="loading"
      ok-text="确认保存"
      cancel-text="取消"
    >
      <div class="space-y-4">
        <!-- 交易类型 -->
        <div>
          <div class="text-xs text-[var(--color-text-3)] mb-1">交易类型</div>
          <a-radio-group v-model="confirmForm.tx_type" type="button" size="small">
            <a-radio :value="1">
              <span class="text-green-500">收入</span>
            </a-radio>
            <a-radio :value="2">
              <span class="text-red-500">支出</span>
            </a-radio>
          </a-radio-group>
        </div>

        <!-- 金额 -->
        <div>
          <div class="text-xs text-[var(--color-text-3)] mb-1">金额</div>
          <a-input-number
            v-model="confirmForm.amount"
            :precision="2"
            :min="0"
            :step="1"
            placeholder="请输入金额"
            class="w-full"
          >
            <template #prefix>¥</template>
          </a-input-number>
        </div>

        <!-- 类别 -->
        <div>
          <div class="text-xs text-[var(--color-text-3)] mb-1">类别</div>
          <a-input v-model="confirmForm.category" placeholder="AI 识别的类别" />
        </div>

        <!-- 备注 -->
        <div>
          <div class="text-xs text-[var(--color-text-3)] mb-1">备注</div>
          <a-input v-model="confirmForm.remark" placeholder="备注信息" />
        </div>

        <!-- 日期 -->
        <div>
          <div class="text-xs text-[var(--color-text-3)] mb-1">交易日期</div>
          <a-date-picker
            v-model="confirmForm.tx_date"
            class="w-full"
            format="YYYY-MM-DD"
          />
        </div>

        <!-- 目标账本 -->
        <div class="bg-[var(--color-fill-2)] rounded-lg p-3">
          <div class="flex items-center gap-2 text-xs text-[var(--color-text-3)]">
            <icon-material-symbols:account-balance-wallet-outline class="text-sm" />
            存入账本：<span class="text-[var(--color-text-1)] font-medium">{{ currentLedger?.name }}</span>
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>
