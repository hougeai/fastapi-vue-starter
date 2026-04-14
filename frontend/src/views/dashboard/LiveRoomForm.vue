<script setup>
import { useRoomStore } from '@/stores/room'
import { useProductStore } from '@/stores/product'
import { useRoute, useRouter } from 'vue-router'
import { getConfig, getLanguageLabel, getDeliveryLabel } from '@/config/index'
import { formatPercentage } from '@/utils/common'

const route = useRoute()
const router = useRouter()

// 从路由参数中获取房间ID（用于编辑模式）
const roomId = ref(route.params.id || null)

const roomStore = useRoomStore()
const productStore = useProductStore()

const allProjects = computed(() => productStore.products)

// 直播间名称
const name = ref('')
const editingName = ref(false)

// 项目相关
const projects = ref([])
const projectIds = ref([])
const selectedProjectId = ref(null)
const showAddProjectDialog = ref(false)
watch(projectIds, async newVal => {
  projects.value = allProjects.value.filter(project => newVal.includes(project.id))
})

const selectProject = id => {
  selectedProjectId.value = id
}

const removeProject = id => {
  // 如果该项目正在讲解，则不允许删除
  if (isLiveStarted.value && id === selectedProjectId.value) {
    AMessage.warning('无法删除正在讲解的项目')
    return
  }
  // 从项目列表中移除
  projects.value = projects.value.filter(project => project.id !== id)
  projectIds.value = projectIds.value.filter(projectId => projectId !== id)
}

// 直播目标和促销
const showTargetDialog = ref(false)
const showPromotionDialog = ref(false)
const liveTarget = ref('')
watch(liveTarget, async newVal => {
  liveTarget.value = newVal
})
const updateProjectsPromotion = async updatedProjects => {
  projects.value = updatedProjects
  // 给后端发请求，更新项目数据
  try {
    for (const project of updatedProjects) {
      await productStore.updateProduct({ id: project.id, promotion: project.promotion })
    }
    AMessage.success('项目促销信息更新成功')
  } catch (error) {
    console.error('更新项目促销信息失败:', error)
    AMessage.error('更新项目促销信息失败')
  }
}
const promotionDisplayText = computed(() => {
  if (!projects.value || projects.value.length === 0) {
    return '暂无促销信息'
  }
  // 获取第一个有促销信息的项目
  const projectWithPromotion = projects.value.find(project => project.promotion)
  if (projectWithPromotion && projectWithPromotion.promotion) {
    return projectWithPromotion.promotion
  }
  return '暂无促销信息'
})

// AI主播相关
const hostAgent = ref(null)
const hostAgentId = ref(null)
const showHostSelectDialog = ref(false)
const updateHostAgent = newHostAgent => {
  console.log('更新主播:', newHostAgent)
  hostAgent.value = newHostAgent
  hostAgentId.value = newHostAgent.id
}
const mode = ref('standard')
const model = ref('cloud')

// AI行为系统
const aiSettings = ref({
  publicControl: true,
  operationDecision: true,
  emotionalInjection: true,
  longTermMemory: true
})

const interactionRate = ref(25)
const contentStrategies = ref([
  { value: 'auto', label: '自动' },
  { value: 'hot', label: '预热引流' },
  { value: 'product', label: '产品详解' },
  { value: 'qa', label: '答疑解惑' },
  { value: 'interactive', label: '互动活跃' },
  { value: 'promotion', label: '促销转化' },
  { value: 'brand', label: '品牌塑造' }
])
const contentStrategy = ref('auto')
const toggleStrategy = strategy => {
  contentStrategy.value = strategy.value
}
const activeInteraction = ref('')
const enhanceExplanation = ref('')
const refreshActiveInteraction = () => {
  console.log('刷新活跃互动：', activeInteraction.value)
}
const refreshEnhanceExplanation = () => {
  console.log('刷新强化解说：', enhanceExplanation.value)
}

// 实时爬虫数据概览
const stats = ref({
  // 卡片1
  viewers: 0,
  maxViewers: 0,
  // 卡片2
  online: 0,
  onlineAdd: 0,
  // 卡片3
  interactionRate: 0,
  interactionRateAdd: 0,
  // 卡片4
  voicePool: 0,
  totalVoice: 0,
  // 卡片5
  danmakuCount: 0,
  danmakuAdd: 0,
  // 卡片6
  starCount: 0,
  starAdd: 0,
  // 卡片7
  newFollows: 0,
  followRate: 0,
  // 卡片8
  cousumption: 0
})

// 初始化
const initializeForm = async () => {
  if (roomId.value) {
    const room = await roomStore.getRoom(roomId.value)
    // 获取名称
    name.value = room.name
    // 获取项目
    if (room.project_ids) {
      projectIds.value = room.project_ids
      projects.value = allProjects.value.filter(project => room.project_ids.includes(project.id))
    }
    if (room.select_project_id) {
      selectedProjectId.value = room.select_project_id
    }
    // 获取直播目标
    if (room.target) {
      liveTarget.value = room.target
    }
    // 获取主播
    if (room.host_agent_id) {
      hostAgent.value = room.host_agent
      hostAgentId.value = room.host_agent_id
    }
    // 获取AI行为系统
    aiSettings.value.publicControl = room.settings?.publicControl || true
    aiSettings.value.operationDecision = room.settings?.operationDecision || true
    aiSettings.value.emotionalInjection = room.settings?.emotionalInjection || true
    aiSettings.value.longTermMemory = room.settings?.longTermMemory || true
    interactionRate.value = room.interaction_rate || 25
    contentStrategy.value = room.content_strategy || 'auto'
    // 获取直播平台
    platform.value = room.platform || 'tiktok'
    url.value = room.url || ''
  }
}

onMounted(async () => {
  // 需要先加载 项目数据
  await productStore.fetchProducts()
  await initializeForm()
})

// 监听路由变化，当路由参数改变时重新初始化表单
watch(
  () => route.params.id,
  async newId => {
    roomId.value = newId || null
    await initializeForm()
  }
)

const handleSaveConfig = async () => {
  const data = {
    name: name.value,
    project_ids: projectIds.value,
    select_project_id: selectedProjectId.value,
    host_agent_id: hostAgentId.value,
    target: liveTarget.value,
    mode: mode.value,
    model: model.value,
    settings: aiSettings.value,
    interaction_rate: interactionRate.value,
    content_strategy: contentStrategy.value,
    platform: platform.value,
    url: url.value
  }
  // 判断name是否填写
  if (!name.value) {
    AMessage.error('请填写直播间名称')
    return
  }
  // 判断project_ids是否填写
  if (!projectIds.value || projectIds.value.length === 0) {
    AMessage.error('请选择项目')
    return
  }
  // 判断主播是否填写
  if (!hostAgent.value) {
    AMessage.error('请选择主播')
    return
  }
  // 如果没有roomId，则创建新的直播间
  if (!roomId.value) {
    try {
      const response = await roomStore.createRoom(data)
      // 创建成功后跳转到编辑页面
      if (response && response.id) {
        router.push(`/dashboard/live-room/edit/${response.id}`)
      }
    } catch (error) {
      console.error('创建直播间失败:', error)
      AMessage.error('创建直播间失败')
    }
  } else {
    // 如果有roomId，则更新现有的直播间
    try {
      data.id = roomId.value
      await roomStore.updateRoom(data)
    } catch (error) {
      console.error('更新直播间失败:', error)
    }
  }
}

// 开始直播：计时
const isLiveStarted = ref(false)
const startTime = ref(null)
const elapsedTime = ref(0) // 单位为秒
let timer = null
// WebSocket连接
let websocket = null
// 接收和播放音频
const audioQueue = []
let isPlaying = false

const formattedTime = computed(() => {
  const totalSeconds = Math.floor(elapsedTime.value)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})
const handleStartLive = () => {
  // 判断是否已选择需要讲解的项目
  if (!selectedProjectId.value) {
    AMessage.error('请先选择需要讲解的项目')
    return
  }
  // 判断是否有直播源
  if (!url.value.startsWith('https://')) {
    AMessage.error('请填写正确的直播平台链接')
    return
  }
  isLiveStarted.value = true
  startTime.value = Date.now()
  elapsedTime.value = 0

  // 启动计时器
  timer = setInterval(() => {
    elapsedTime.value = Math.floor((Date.now() - startTime.value) / 1000)
  }, 1000)

  // 建立WebSocket连接
  try {
    websocket = new WebSocket(`${getConfig('wsUrl')}?roomId=${roomId.value}`)
    websocket.onopen = () => {
      console.log('WebSocket连接已建立')
      AMessage.success('已连接到直播服务器')
    }
    websocket.onmessage = event => {
      // 解析从后端接收到的消息
      const message = JSON.parse(event.data)

      // 根据消息类型处理数据
      switch (message.type) {
        case 'error':
          addToLiveQueue(message.content)
          break
        case 'system':
          addToLiveQueue(message.content)
          break
        case 'text':
          addToLiveQueue(message.content)
          break
        case 'audio':
          audioQueue.push(message)
          if (!isPlaying) {
            playNextAudio()
          }
          break
        default:
          console.warn('未知消息类型:', message.type)
      }
    }

    websocket.onerror = error => {
      console.error('WebSocket错误:', error)
      AMessage.error('与直播服务器连接出错')
    }

    websocket.onclose = () => {
      console.log('WebSocket连接已关闭')
      if (isLiveStarted.value) {
        AMessage.warning('与直播服务器的连接已断开')
      }
    }
  } catch (error) {
    console.error('WebSocket连接出错:', error)
    AMessage.error('无法连接到直播服务器')
  }
}

// 添加内容到口播队列
const addToLiveQueue = content => {
  const now = new Date()
  const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`

  liveQueue.value.push({
    content: content,
    time: timeString
  })
}

// 播放音频数据
let audioContext = null

const playNextAudio = async () => {
  if (audioQueue.length === 0) {
    isPlaying = false
    return
  }

  isPlaying = true
  const audioItem = audioQueue.shift()

  try {
    if (!audioContext) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)()
    }

    // base64 → arraybuffer
    const base64 = audioItem.content
    const binary = atob(base64)
    const len = binary.length
    const buffer = new Uint8Array(len)
    for (let i = 0; i < len; i++) {
      buffer[i] = binary.charCodeAt(i)
    }

    // 解码 WAV / PCM
    const audioBuffer = await audioContext.decodeAudioData(buffer.buffer)

    // 播放
    const source = audioContext.createBufferSource()
    source.buffer = audioBuffer
    source.connect(audioContext.destination)
    source.start(0)

    // 播放结束后继续下一段
    source.onended = () => {
      playNextAudio()
    }
  } catch (err) {
    console.error('音频播放失败', err)
    playNextAudio()
  }
}

const handleStopLive = () => {
  AModal.confirm({
    title: '停止直播',
    content: '确定要停止直播吗？此操作不可恢复。',
    okText: '停止',
    cancelText: '取消',
    okButtonProps: { status: 'danger' },
    onOk: async () => {
      isLiveStarted.value = false
      if (timer) {
        clearInterval(timer)
        timer = null
      }
      // 关闭WebSocket连接
      if (websocket) {
        websocket.close()
        websocket = null
      }
      console.log('直播时长:', formattedTime.value)
      AMessage.info('已停止直播')
      elapsedTime.value = 0
    }
  })
}

// 公屏信息
const platform = ref('tiktok')
const url = ref('')
const handleSavePlatform = () => {
  // 保存公屏信息
}
// 口播队列
const liveQueue = ref([])
const queueInput = ref('')
const handleAddToQueue = () => {
  // 添加到口播队列
  if (queueInput.value.trim()) {
    const now = new Date()
    const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`

    liveQueue.value.push({
      content: queueInput.value,
      time: timeString
    })

    queueInput.value = ''
  }
}

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<template>
  <div class="w-full p-3 pt-1 bg-[var(--color-fill-0)]">
    <!-- 上方按钮区 -->
    <div class="flex items-center justify-between">
      <a-button type="text" @click="router.back()">
        <template #icon><icon-material-symbols:arrow-back /></template>
        返回 / 我的直播间
      </a-button>

      <div class="flex items-center gap-3">
        <a-tooltip content="点击修改直播间名称">
          <div
            v-if="!editingName"
            class="flex items-center font-bold text-[var(--color-text-1)] cursor-pointer hover:text-blue-600 transition-colors"
            @click="editingName = true"
          >
            {{ name || '未命名直播间' }}
            <a-button type="text" size="tiny">
              <template #icon>
                <icon-material-symbols:edit />
              </template>
            </a-button>
          </div>
          <a-input
            v-else
            v-model="name"
            size="small"
            style="width: 200px"
            placeholder="请输入直播间名称"
            :max-length="30"
            show-word-limit
            @press-enter="editingName = false"
            @blur="editingName = false"
            auto-focus
          />
        </a-tooltip>
      </div>

      <div class="flex items-center pr-3">
        <div class="font-bold">直播间状态：</div>
        <a-tag :color="isLiveStarted ? 'green' : 'red'">
          {{ isLiveStarted ? '直播中' : '未开播' }}
        </a-tag>
        <div class="font-bold pl-4">直播间ID：</div>
        <div>{{ roomId }}</div>
      </div>
    </div>

    <!-- 中间内容区 - 三栏布局 -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-2 mx-2">
      <!-- 左边栏：我的项目列表 -->
      <div class="md:col-span-1">
        <div class="rounded-lg shadow-sm p-3 pt-1 bg-[var(--color-fill-1)]">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold">选择项目</h3>
            <a-button type="text" size="small" @click="showAddProjectDialog = true">
              <template #icon><icon-material-symbols:add-circle-outline /></template>
              添加
            </a-button>
          </div>
          <div class="text-xs text-gray-500 mb-3">
            将您要直播的商品或服务创建为项目，开播时可选择多个项目到直播间
          </div>
          <div class="h-[calc(100vh-16rem)] overflow-y-auto">
            <div class="space-y-2">
              <div
                v-for="project in projects"
                :key="project.id"
                class="bg-[var(--color-primary-light-1)] rounded-lg p-3 hover:bg-[var(--color-primary-light-2)] transition-colors relative"
              >
                <div
                  v-if="project.id === selectedProjectId"
                  class="absolute top-1 right-1 w-4 h-4 bg-[var(--color-danger-light-4)] rounded-full flex items-center justify-center text-white text-xs"
                >
                  ✓
                </div>
                <div class="flex items-center gap-2">
                  <img
                    :src="
                      project.cover_image_url
                        ? `${getConfig('ossUrl')}/${project.cover_image_url}`
                        : getConfig('me.avatar')
                    "
                    alt="project avatar"
                    class="w-8 h-8 rounded-full object-cover"
                  />
                  <div class="flex-1">
                    <div class="font-bold">{{ project.project_name || '—' }}</div>
                    <div class="text-xs text-gray-500">价格：{{ project.price_info || '—' }}</div>
                  </div>
                  <div class="flex flex-col items-center space-y-1">
                    <a-tag color="green" size="small">
                      {{ getLanguageLabel(project.language) }}
                    </a-tag>
                    <a-tag color="green" size="small">
                      {{ getDeliveryLabel(project.delivery_type) }}
                    </a-tag>
                  </div>
                </div>
                <div class="flex justify-center">
                  <div
                    v-if="project.id === selectedProjectId"
                    class="max-w-1/2 mt-2 px-3 py-1 bg-[var(--color-danger-light-3)] text-[var(--color-text-2)] rounded-xl"
                  >
                    正在讲解
                  </div>
                  <div
                    v-else
                    class="max-w-1/2 mt-2 px-3 py-1 bg-[var(--color-warning-light-2)] text-[var(--color-text-2)] rounded-xl shadow-sm cursor-pointer"
                    @click="selectProject(project.id)"
                  >
                    切换到此项目
                  </div>
                </div>
                <div class="absolute bottom-1 right-1">
                  <a-tooltip content="删除项目">
                    <a-button
                      type="text"
                      size="small"
                      status="danger"
                      shape="circle"
                      @click="removeProject(project.id)"
                    >
                      <template #icon><icon-material-symbols:delete-outline /></template>
                    </a-button>
                  </a-tooltip>
                </div>
              </div>

              <div
                class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-3 text-center cursor-pointer hover:bg-[var(--color-fill-2)] transition-colors"
                @click="showAddProjectDialog = true"
              >
                <div class="text-gray-400 mb-1">
                  <icon-ri-add-circle-line class="text-xl" />
                </div>
                <div class="text-gray-500">添加直播项目</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间栏：概览、洞察、AI主播控制 -->
      <div class="md:col-span-3">
        <!-- 概览卡片 -->
        <div class="rounded-lg shadow-sm p-3 pt-1 border mb-2 bg-[var(--color-fill-1)]">
          <h3 class="font-semibold mb-2">概览</h3>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-3">
              <div class="flex justify-between items-center">
                <div class="text-sm text-[var(--color-text-1)]">累计场观人数</div>
                <div class="text-lg font-bold">{{ stats.viewers || 0 }}</div>
              </div>
              <div class="text-xs text-[var(--color-text-3)]">
                近10场最高 {{ stats.maxViewers || 0 }}
              </div>
            </div>
            <div class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-3">
              <div class="flex justify-between items-center">
                <div class="text-sm text-[var(--color-text-1)]">当前在线人数</div>
                <div class="text-lg font-bold">{{ stats.online || 0 }}</div>
              </div>
              <div class="text-xs text-[var(--color-text-3)]">
                {{ stats.onlineAdd || '+0' }} vs 3分钟前
              </div>
            </div>
            <div class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-3">
              <div class="flex justify-between items-center">
                <div class="text-sm text-[var(--color-text-1)]">互动率</div>
                <div class="text-lg font-bold">{{ formatPercentage(stats.interactionRate) }}</div>
              </div>
              <div class="text-xs text-[var(--color-text-3)]">
                {{ formatPercentage(stats.interactionRateAdd) }} vs 3分钟前
              </div>
            </div>
            <div class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-3">
              <div class="flex justify-between items-center">
                <div class="text-sm text-[var(--color-text-1)]">直播语音池</div>
                <div class="text-lg font-bold">{{ stats.voicePool || 0 }}</div>
              </div>
              <div class="text-xs text-[var(--color-text-3)]">
                直播间总生成{{ stats.totalVoice || 0 }}条
              </div>
            </div>
            <div class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-3">
              <div class="flex justify-between items-center">
                <div class="text-sm text-[var(--color-text-1)]">弹幕数量</div>
                <div class="text-lg font-bold">{{ stats.danmakuCount || 0 }}</div>
              </div>
              <div class="text-xs text-[var(--color-text-3)]">
                {{ stats.danmakuAdd || +0 }} vs 3分钟前
              </div>
            </div>
            <div class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-3">
              <div class="flex justify-between items-center">
                <div class="text-sm text-[var(--color-text-1)]">累计点赞</div>
                <div class="text-lg font-bold">{{ stats.starCount || 0 }}</div>
              </div>
              <div class="text-xs text-[var(--color-text-3)]">
                {{ stats.starAdd || 0 }} vs 3分钟前
              </div>
            </div>
            <div class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-3">
              <div class="flex justify-between items-center">
                <div class="text-sm text-[var(--color-text-1)]">新增关注</div>
                <div class="text-lg font-bold">{{ stats.newFollows || 0 }}</div>
              </div>
              <div class="text-xs text-[var(--color-text-3)]">
                {{ formatPercentage(stats.followRate) }} 关注率
              </div>
            </div>
            <div class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-3">
              <div class="flex justify-between items-center">
                <div class="text-sm text-[var(--color-text-1)]">消耗算力</div>
                <div class="text-lg font-bold">{{ stats.cousumption || 0 }}</div>
              </div>
              <div class="text-xs text-[var(--color-text-3)]">预估消耗 35算力/小时</div>
            </div>
          </div>
          <div
            class="mt-2 border border-dashed border-[var(--color-danger-light-4)] bg-[var(--color-danger-light-1)] rounded-lg p-3 flex items-center justify-between"
          >
            <div class="flex items-start min-w-0">
              <icon-mingcute:target-fill class="text-red-500 text-2xl mr-3 mt-1" />
              <div class="flex flex-col min-w-0">
                <div class="font-bold text-[var(--color-text-1)] mb-1">直播目标与促销</div>
                <div class="text-xs text-[var(--color-text-2)] flex items-center">
                  <span class="mr-2 truncate max-w-1/4"
                    >目标：{{ liveTarget || '暂无直播目标' }}</span
                  >
                  <span class="mx-1">|</span>
                  <span class="ml-2 truncate max-w-1/4">促销：{{ promotionDisplayText }}</span>
                </div>
              </div>
            </div>
            <div class="flex gap-2 flex-shrink-0">
              <a-button
                type="outline"
                shape="round"
                status="danger"
                size="small"
                @click="showTargetDialog = true"
              >
                设置目标
              </a-button>
              <a-button
                type="outline"
                shape="round"
                status="danger"
                size="small"
                @click="showPromotionDialog = true"
              >
                设置促销
              </a-button>
            </div>
          </div>
        </div>

        <!-- 洞察卡片 -->
        <div class="rounded-lg shadow-sm p-3 border mb-2 bg-[var(--color-fill-1)]">
          <div class="grid grid-cols-3 gap-3">
            <!-- 互动洞察 -->
            <div class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-2">
              <div class="flex items-center justify-between mb-1">
                <div class="flex items-center gap-1">
                  <icon-material-symbols:chat-bubble-outline class="text-blue-500" />
                  <span class="text-sm font-medium">互动洞察</span>
                </div>
                <span class="text-xs px-2 py-1 bg-red-100 text-red-600 rounded-full">0条洞察</span>
              </div>
              <div class="text-xs text-gray-400">暂无信息</div>
            </div>

            <!-- 运营洞察 -->
            <div class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-2">
              <div class="flex items-center justify-between mb-1">
                <div class="flex items-center gap-2">
                  <icon-material-symbols:insights class="text-orange-500" />
                  <span class="text-sm font-medium">运营洞察</span>
                </div>
                <span class="text-xs px-2 py-1 bg-orange-100 text-orange-600 rounded-full"
                  >0条洞察</span
                >
              </div>
              <div class="text-xs text-gray-400">暂无信息</div>
            </div>

            <!-- 记忆洞察 -->
            <div class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-2">
              <div class="flex items-center justify-between mb-1">
                <div class="flex items-center gap-2">
                  <icon-material-symbols:memory class="text-purple-500" />
                  <span class="text-sm font-medium">记忆洞察</span>
                </div>
                <span class="text-xs px-2 py-1 bg-purple-100 text-purple-600 rounded-full"
                  >0条洞察</span
                >
              </div>
              <div class="text-xs text-gray-400">暂无信息</div>
            </div>
          </div>
        </div>

        <!-- AI主播控制卡片 -->
        <div class="rounded-lg shadow-sm p-3 pt-1 border bg-[var(--color-fill-1)]">
          <!-- 左右分栏布局 -->
          <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
            <!-- 左侧栏：主播信息 + 模式选择 -->
            <div class="lg:col-span-1 space-y-2">
              <h3 class="font-bold text-gray-800 mb-1">AI主播控制</h3>
              <!-- 主播头像区域 -->
              <div
                class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-1 border cursor-pointer flex flex-col justify-center"
                @click="showHostSelectDialog = true"
              >
                <img
                  :src="hostAgent?.avatar || getConfig('me.avatar')"
                  alt="avatar"
                  class="w-8 h-8 rounded-full object-cover mx-auto mb-2"
                />
                <div class="text-center">
                  <div>{{ hostAgent?.name || '未知主播' }}</div>
                  <a-tag size="small" color="orange">
                    {{ hostAgent ? getLanguageLabel(hostAgent.lang) : '-' }}
                  </a-tag>
                </div>
              </div>

              <!-- 直播模式 -->
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <span>直播模式</span>
                  <a-tooltip content="支持实时生成语音">
                    <icon-material-symbols:info-outline class="text-gray-400" />
                  </a-tooltip>
                </div>
                <a-select v-model="mode" placeholder="请选择直播模式" style="width: 100%">
                  <a-option value="standard">标准模式（实时生成语音）</a-option>
                </a-select>
              </div>

              <!-- 模型选择 -->
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <span>模型选择</span>
                  <a-tooltip content="支持云端模型">
                    <icon-material-symbols:info-outline class="text-gray-400" />
                  </a-tooltip>
                </div>
                <a-select v-model="model" placeholder="请选择模型" style="width: 100%">
                  <a-option value="cloud">云端模型 35 算力/小时</a-option>
                </a-select>
              </div>
            </div>

            <!-- 右侧栏：AI行为系统 + 内容策略 -->
            <div class="lg:col-span-4 space-y-2">
              <!-- AI行为系统 -->
              <div
                class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-2 space-y-1"
              >
                <div class="flex items-center gap-2">
                  <icon-material-symbols:settings class="text-blue-500" />
                  <span class="font-bold">AI行为系统</span>
                </div>

                <div class="grid grid-cols-2 gap-2">
                  <div class="bg-blue-50 rounded-lg p-3">
                    <div class="flex items-center justify-between">
                      <div class="text-sm text-gray-600">公屏控场能力</div>
                      <a-switch v-model="aiSettings.publicControl" size="small" />
                    </div>
                    <div class="text-xs text-gray-500 truncate">
                      自主回应观众进入直播间、点赞、关注、礼物、弹幕评论...
                    </div>
                  </div>
                  <div class="bg-green-50 rounded-lg p-3">
                    <div class="flex items-center justify-between">
                      <div class="text-sm text-gray-600">运营决策能力</div>
                      <a-switch v-model="aiSettings.operationDecision" size="small" />
                    </div>
                    <div class="text-xs text-gray-500 truncate">
                      根据主播经验和直播间数据自主决策当前直播内容策略
                    </div>
                  </div>
                  <div class="bg-purple-50 rounded-lg p-3">
                    <div class="flex items-center justify-between">
                      <div class="text-sm text-gray-600">情感注入能力</div>
                      <a-switch v-model="aiSettings.emotionalInjection" size="small" />
                    </div>
                    <div class="text-xs text-gray-500 truncate">
                      提供高级情感注入的能力，让主播的表达更具情绪感染力
                    </div>
                  </div>
                  <div class="bg-yellow-50 rounded-lg p-3">
                    <div class="flex items-center justify-between">
                      <div class="text-sm text-gray-600">长期记忆能力</div>
                      <a-switch v-model="aiSettings.longTermMemory" size="small" />
                    </div>
                    <div class="text-xs text-gray-500 truncate">
                      记录并分析观众行为和用户的决策习惯用于主播长期记忆...
                    </div>
                  </div>
                </div>
                <!-- 交互占比 -->
                <div class="flex items-center gap-2 mb-2 whitespace-nowrap">
                  <span>交互占比：</span>
                  <span class="text-sm text-gray-500">25%</span>
                  <a-slider
                    v-model:value="interactionRate"
                    :min="25"
                    :max="80"
                    :step="5"
                    style="flex-grow: 1"
                  />
                  <span class="text-sm text-gray-500">80%</span>
                </div>

                <!-- 内容策略 -->
                <div class="flex items-center gap-2 mb-4">
                  <span>内容策略：</span>
                  <div class="flex flex-wrap gap-1">
                    <a-button
                      v-for="strategy in contentStrategies"
                      :key="strategy.value"
                      :type="contentStrategy === strategy.value ? 'primary' : 'outline'"
                      size="mini"
                      @click="toggleStrategy(strategy)"
                    >
                      {{ strategy.label }}
                    </a-button>
                  </div>
                </div>

                <!-- 主动互动 & 强化解说 -->
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <span>主动互动：</span>
                    <a-input
                      v-model="activeInteraction"
                      size="small"
                      placeholder="暂无AI建议"
                      readonly
                      style="width: 150px"
                    />
                    <icon-material-symbols:refresh
                      @click="refreshActiveInteraction"
                      class="cursor-pointer text-gray-500 hover:text-blue-500"
                    />
                  </div>

                  <div class="flex items-center gap-2">
                    <span>强化解说：</span>
                    <a-input
                      v-model="enhanceExplanation"
                      size="small"
                      placeholder="暂无AI建议"
                      readonly
                      style="width: 150px"
                    />
                    <icon-material-symbols:refresh
                      @click="refreshEnhanceExplanation"
                      class="cursor-pointer text-gray-500 hover:text-blue-500"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右边栏：公屏信息和口播队列 -->
      <div class="md:col-span-1">
        <!-- 公屏信息卡片 -->
        <div class="rounded-lg shadow-sm p-3 pt-1 border mb-4 bg-[var(--color-fill-1)]">
          <div class="flex items-center justify-between">
            <h3 class="font-bold">公屏信息</h3>
          </div>
          <div class="flex items-center gap-2 mb-4">
            <span class="whitespace-nowrap">选择平台</span>
            <a-select v-model="platform">
              <a-option value="tiktok">TikTok</a-option>
              <a-option value="douyin">抖音</a-option>
            </a-select>
            <a-button type="primary" size="mini" @click="handleSavePlatform">
              <template #icon><icon-material-symbols:save /></template>
              保存
            </a-button>
          </div>

          <div class="flex items-center gap-2 mb-4">
            <span class="whitespace-nowrap">平台链接</span>
            <a-input v-model="url" placeholder="请输入平台链接" />
          </div>
        </div>

        <!-- 口播队列卡片 -->
        <div class="rounded-lg shadow-sm p-3 pt-1 border bg-[var(--color-fill-1)]">
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-bold">口播队列</h3>
          </div>

          <div class="bg-white rounded-lg border p-3 h-[calc(100vh-30rem)] overflow-y-auto mb-5">
            <div v-if="liveQueue.length === 0" class="text-gray-500 text-center py-4">
              <div class="text-sm">开播后，您将在此处看到 AI 主播的实时口播内容</div>
            </div>
            <div v-else class="space-y-2">
              <div v-for="(item, index) in liveQueue" :key="index">
                <div class="text-center text-xs text-[var(--color-text-3)]">
                  {{ item.time }}
                </div>
                <div
                  class="p-2 bg-[var(--color-fill-2)] text-[var(--color-text-1)] rounded text-xs"
                >
                  {{ item.content }}
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <a-input
              v-model="queueInput"
              placeholder="请输入内容，非主播语种会被自动翻译"
              style="flex-grow: 1"
            />
            <a-button type="primary" size="mini" @click="handleAddToQueue">
              <template #icon><icon-material-symbols:add-circle-outline /></template>
              插播
            </a-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 最下方按钮区 -->
    <div class="flex items-center justify-center gap-3 mt-2">
      <a-button type="primary" @click="handleSaveConfig" :loading="roomStore.loading">
        {{ roomId ? '保存配置' : '创建直播间' }}
      </a-button>
      <div class="bg-[var(--color-fill-2)] px-3 py-2 rounded">{{ formattedTime }}</div>
      <a-button v-if="!isLiveStarted" type="primary" @click="handleStartLive" :disabled="!roomId">
        <template #icon><icon-material-symbols:play-arrow /></template>
        开始直播
      </a-button>
      <a-button v-else type="primary" status="danger" @click="handleStopLive">
        <template #icon><icon-material-symbols:stop /></template>
        停止直播
      </a-button>
    </div>

    <!-- 添加项目对话框 -->
    <ProjectAddDialog v-model:visible="showAddProjectDialog" v-model:projectIds="projectIds" />
    <TargetSetDialog v-model:visible="showTargetDialog" v-model:liveTarget="liveTarget" />
    <PromotionSetDialog
      v-model:visible="showPromotionDialog"
      v-model:projects="projects"
      @update:promotion="updateProjectsPromotion"
    />
    <HostSelectDialog
      v-model:visible="showHostSelectDialog"
      v-model:host-agent="hostAgent"
      @update:host="updateHostAgent"
    />
  </div>
</template>
