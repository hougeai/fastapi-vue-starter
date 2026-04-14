<template>
  <a-modal
    :visible="visible"
    @cancel="handleCancel"
    @ok="handleOk"
    :mask-closable="false"
    width="800px"
    class="rounded-2xl shadow-2xl"
    centered
  >
    <template #title>
      <div class="flex items-center -ml-18">
        <icon-material-symbols:settings-outline
          class="text-[var(--color-primary-light-4)] text-xl mr-1 ml-0"
        />
        <div class="text-xl font-bold">设置促销信息</div>
      </div>
    </template>

    <!-- 提示信息 -->
    <div class="mb-6 bg-[var(--color-warning-light-1)] p-4 rounded-lg">
      <div class="flex items-start">
        <icon-material-symbols:warning
          class="text-[var(--color-warning-light-4)] mt-0.5 mr-2"
          style="font-size: 1.2rem"
        />
        <div class="text-sm text-[var(--color-text-2)] leading-relaxed">
          设置直播间当前项目的促销信息，帮助AI主播更好地向观众传达优惠活动。设置后，AI主播将根据促销信息调整话术和引导方式。促销信息应包含优惠力度、时效性和参与方式。
        </div>
      </div>
    </div>

    <!-- 输入促销信息 -->
    <div class="mb-6">
      <div class="flex items-center space-x-4">
        <h3 class="text-sm font-bold mb-3">输入促销信息：</h3>
        <a-button type="dashed" shape="round" size="small" status="warning" @click="selectAll">
          <template #icon><icon-material-symbols:add-circle-outline /></template>
          一键设置
        </a-button>
      </div>
      <div class="space-y-2">
        <div v-for="project in localProjects" :key="project.id" class="flex items-center gap-2">
          <a-checkbox
            :model-value="selectedIds.includes(project.id)"
            @change="toggleSelection(project.id)"
            class="mr-2"
          />
          <div class="flex items-center gap-1">
            <img
              :src="
                project.cover_image_url
                  ? `${getConfig('ossUrl')}/${project.cover_image_url}`
                  : getConfig('me.avatar')
              "
              alt="Cover Image"
              class="w-6 h-6 object-cover rounded"
            />
            <div class="font-bold truncate min-w-8 max-w-16">{{ project.project_name }}</div>
          </div>
          <a-input
            v-model="project.promotion"
            placeholder="请输入促销文案"
            :max-length="30"
            show-word-limit
            allow-clear
          />
        </div>
      </div>
    </div>

    <!-- 促销示例和建议 -->
    <div class="mb-6">
      <h3 class="text-sm font-bold mb-3">促销示例和建议</h3>
      <div v-for="(category, index) in promotionSuggestions" :key="index" class="mb-4">
        <span class="text-sm text-[var(--color-text-3)]">{{ category.title }}：</span>
        <div class="flex flex-wrap gap-2 mt-2">
          <a-button
            v-for="(item, i) in category.items"
            :key="i"
            type="default"
            shape="round"
            size="mini"
            class="border-dashed border-[var(--color-danger-light-1)] bg-[var(--color-fill-0)] text-[var(--color-danger-light-4)] hover:bg-[var(--color-danger-light-1)] px-4 py-1 rounded-full text-xs"
            @click="setPromotion(item)"
          >
            {{ item }}
          </a-button>
        </div>
      </div>
    </div>

    <template #footer>
      <a-button type="outline" @click="handleCancel">取消</a-button>
      <a-button type="primary" @click="handleOk" class="bg-red-500 hover:bg-red-600 text-white">
        确定
      </a-button>
    </template>
  </a-modal>
</template>

<script setup>
import { getConfig } from '@/config/index'

// Props
const props = defineProps({
  visible: Boolean,
  projects: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'update:promotion'])

const localProjects = ref(props.projects || [])
const selectedIds = ref([])

watch(
  () => props.projects,
  newProjects => {
    // 深拷贝projects以避免直接修改props
    localProjects.value = JSON.parse(JSON.stringify(newProjects))
    // 默认选中所有项目
    selectedIds.value = localProjects.value.map(project => project.id)
  },
  { immediate: true }
)

// 切换项目选择状态
const toggleSelection = projectId => {
  const index = selectedIds.value.indexOf(projectId)
  if (index > -1) {
    // 已选中，移除
    selectedIds.value.splice(index, 1)
  } else {
    // 未选中，添加
    selectedIds.value.push(projectId)
  }
}

// 全选/取消全选
const selectAll = () => {
  if (selectedIds.value.length === localProjects.value.length) {
    // 当前全选状态，取消全选
    selectedIds.value = []
  } else {
    // 当前不是全选状态，执行全选
    selectedIds.value = localProjects.value.map(project => project.id)
  }
}

// 目标建议分类数据
const promotionSuggestions = [
  {
    title: '折扣优惠',
    items: [
      '全场8折,新品上市，首发9折优惠',
      '新品上市，首发9折优惠',
      '直播间专享100元无门槛优惠券',
      '关注店铺领取10美金优惠券'
    ]
  },
  {
    title: '满减活动',
    items: [
      '满100美金立减20美金，满500美金减150美金',
      '满999元免运费',
      '消费满300元赠送精美礼品一份，浏览主页内容'
    ]
  },
  {
    title: '限时活动',
    items: ['今日限时4小时，全场包邮', '前100名下单送精美礼品']
  }
]

// 设置促销信息（这里可以扩展为针对特定项目设置）
const setPromotion = item => {
  localProjects.value.forEach(project => {
    if (selectedIds.value.includes(project.id)) {
      project.promotion = item
    }
  })
}

// 取消
const handleCancel = () => {
  emit('update:visible', false)
}

// 确定
const handleOk = () => {
  emit('update:promotion', localProjects.value)
  emit('update:visible', false)
}
</script>
