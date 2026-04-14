<template>
  <a-modal
    :visible="visible"
    @cancel="handleCancel"
    @ok="handleOk"
    :mask-closable="false"
    width="600px"
    class="rounded-2xl shadow-2xl"
    centered
  >
    <template #title>
      <div class="flex items-center -ml-18">
        <icon-material-symbols:contract-edit
          class="text-[var(--color-primary-light-4)] text-xl mr-1 ml-0"
        />
        <div class="text-xl font-bold">选择项目</div>
      </div>
      <div class="text-xs text-[var(--color-text-3)] ml-1 mt-2">
        将您要直播的商品或服务创建为项目，开播时可选择多个项目到直播间
      </div>
    </template>

    <!-- 顶部操作区 -->
    <div class="flex flex-wrap items-center justify-between mb-4">
      <a-select
        v-model="selectedLanguage"
        :options="languageOptions"
        style="width: 120px"
        size="large"
      />
      <span class="text-sm text-[var(--color-text-3)]">
        已选 {{ localSelectedIds.length }} 项
      </span>

      <a-button
        type="primary"
        size="large"
        style="border-radius: 0.5rem"
        @click="handleCreateProject"
      >
        <template #icon><icon-ri-add-circle-line /></template>
        创建新项目
      </a-button>
    </div>

    <!-- 项目列表 -->
    <div class="space-y-3 max-h-80 overflow-y-auto">
      <div
        v-for="project in paginatedProducts"
        :key="project.id"
        class="flex items-center justify-between p-3 border rounded-lg bg-[var(--color-fill-1)] hover:bg-[var(--color-fill-2)] transition-colors cursor-pointer"
        @click="selectProject(project.id)"
      >
        <div class="flex items-center gap-3">
          <a-checkbox :model-value="localSelectedIds.includes(project.id)" class="mr-2" />
          <img
            :src="
              project.cover_image_url
                ? `${getConfig('ossUrl')}/${project.cover_image_url}`
                : getConfig('me.avatar')
            "
            alt="project avatar"
            class="w-10 h-10 rounded-full object-cover"
          />
          <div>
            <div class="font-bold">{{ project.project_name || '—' }}</div>
            <div class="text-xs text-gray-500">价格：{{ project.price_info || '—' }}</div>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <a-tag color="green">
            {{ getLanguageLabel(project.language) }}
          </a-tag>
          <a-tag color="green">
            {{ getDeliveryLabel(project.delivery_type) }}
          </a-tag>
        </div>
      </div>
    </div>

    <!-- 分页器 -->
    <div class="flex items-center justify-center mt-4">
      <a-pagination
        v-model:current="pagination.current"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :show-total="pagination.showTotal"
        :show-page-size="pagination.showPageSize"
        @change="handlePageChange"
        @page-size-change="handlePageSizeChange"
      />
    </div>

    <template #footer>
      <a-button type="outline" @click="handleCancel">取消</a-button>
      <a-button type="primary" @click="handleOk">确定</a-button>
    </template>
  </a-modal>
</template>

<script setup>
import { useProductStore } from '@/stores/product'
import { getConfig, getLanguageLabel, getDeliveryLabel } from '@/config/index'

import { useRouter } from 'vue-router'
const productStore = useProductStore()
const router = useRouter()

// Props
const props = defineProps({
  visible: Boolean,
  projectIds: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'update:projectIds'])

// 1. 创建内部临时状态
const localSelectedIds = ref([])

// 2. 监听对话框打开，同步初始值
watch(
  () => props.visible,
  newVal => {
    if (newVal) {
      // 深拷贝，避免直接修改父组件数据
      localSelectedIds.value = [...props.projectIds]
    }
  },
  { immediate: true }
)

// 3. 修改选择逻辑，只操作临时状态
const selectProject = id => {
  const index = localSelectedIds.value.indexOf(id)
  if (index > -1) {
    localSelectedIds.value.splice(index, 1)
  } else {
    localSelectedIds.value.push(id)
  }
}

// 数据状态
const products = computed(() => productStore.products)
const selectedLanguage = ref('全部语言')

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: true,
  showPageSize: true
})

// 筛选后的产品列表
const filteredProducts = computed(() => {
  return products.value.filter(product => {
    const matchesLanguage =
      selectedLanguage.value === '全部语言' || product.language === selectedLanguage.value
    return matchesLanguage
  })
})

const paginatedProducts = computed(() => {
  const start = (pagination.current - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  const filtered = filteredProducts.value
  return filtered.slice(start, end)
})

// 当过滤后的列表变化时，更新分页总数
watch(
  () => filteredProducts.value,
  newFilteredProducts => {
    pagination.total = newFilteredProducts.length
  },
  { immediate: true }
)

// 页面切换
const handlePageChange = async current => {
  pagination.current = current
}

const handlePageSizeChange = size => {
  pagination.pageSize = size
  pagination.current = 1
}

const languageOptions = getConfig('languageOptions')

// 创建新项目
const handleCreateProject = () => {
  router.push('/dashboard/product')
}

// 取消
const handleCancel = () => {
  emit('update:visible', false)
}

// 确定
const handleOk = () => {
  emit('update:projectIds', localSelectedIds.value)
  emit('update:visible', false)
}
</script>
