<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { formatDateTime } from '@/utils'
import defaultCover from '@/assets/img/banner.webp'
import { getConfig, getLanguageLabel, getDeliveryLabel } from '@/config/index'
import { useProductStore } from '@/stores/product'

const productStore = useProductStore()

const products = computed(() => productStore.products)
const selectedLanguage = ref('全部语言')
const searchQuery = ref('')

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
    const matchesSearch = product.project_name.includes(searchQuery.value)
    return matchesLanguage && matchesSearch
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

const languageOptions = getConfig('languageOptions')
const deliveryOptions = getConfig('deliveryOptions')
const scriptCategories = [
  { key: 'opening', label: '开场白', sort: 10 },
  { key: 'selling', label: '产品卖点', sort: 20 },
  { key: 'brand', label: '品牌背景和实力', sort: 30 },
  { key: 'scenario', label: '场景和价值塑造', sort: 40 },
  { key: 'testimonials', label: '客户见证和案例', sort: 50 },
  { key: 'service', label: '交互与服务流程', sort: 60 },
  { key: 'social', label: '社交功能引导', sort: 70 },
  { key: 'qa', label: '常见问答', sort: 80 },
  { key: 'end', label: '结束语', sort: 90 }
]

const columns = [
  {
    title: '项目封面',
    dataIndex: 'cover_image_url',
    slotName: 'cover',
    width: 140,
    align: 'center'
  },
  { title: '项目名称', dataIndex: 'project_name', slotName: 'project_name', width: 120 },
  { title: '交付类型', dataIndex: 'delivery_type', slotName: 'delivery_type', width: 120 },
  { title: '语种', dataIndex: 'language', slotName: 'language', width: 120, align: 'center' },
  { title: '创建时间', dataIndex: 'create_at', slotName: 'create_at', width: 200, align: 'center' },
  { title: '操作', dataIndex: 'actions', slotName: 'actions', width: 200, align: 'center' }
]

const drawerVisible = ref(false)
const drawerMode = ref('create')
const activeTab = ref('basic')
const activeScriptCategory = ref('all')
const formRef = ref()
const scriptsLoading = ref(false)
const generatingCategory = ref('')
const scriptsDirty = ref(false)
const scriptsLoaded = ref(false)
const currentProjectId = ref(null)
const fileInputRef = ref(null)

const createDefaultForm = () => ({
  id: null,
  project_name: '',
  language: '',
  price_info: '',
  selling_points: '',
  specifications: '',
  delivery_type: '',
  shipping_location: '',
  shipping_cost: '',
  courier_company: '',
  shipping_time: '',
  cover_image_url: ''
})

const formModel = reactive(createDefaultForm())
const basicSnapshot = ref(createDefaultForm())

const requiredFields = new Set([
  'project_name',
  'language',
  'price_info',
  'selling_points',
  'specifications',
  'delivery_type'
])

const formRules = {
  project_name: [{ required: true, message: '请输入项目名称' }],
  language: [{ required: true, message: '请选择语种' }],
  price_info: [{ required: true, message: '请输入价格信息' }],
  selling_points: [
    { required: true, message: '请输入卖点信息' },
    { maxLength: 600, message: '卖点信息不能超过600个字符' }
  ],
  specifications: [
    { required: true, message: '请输入详细规格' },
    { maxLength: 300, message: '规格信息不能超过300个字符' }
  ],
  delivery_type: [{ required: true, message: '请选择交付类型' }]
}

const createScriptsRecord = () => {
  const record = {}
  scriptCategories.forEach(({ label, sort }) => {
    record[label] = {
      id: null,
      category: label,
      contents: [],
      sort_order: sort,
      status: 1
    }
  })
  return record
}

const scriptsState = reactive(createScriptsRecord())
const scriptsSnapshot = ref(createScriptsRecord())

const cloneRecord = record => JSON.parse(JSON.stringify(record || createScriptsRecord()))

const applyScriptsRecord = record => {
  const base = createScriptsRecord()
  const source = record || base
  Object.keys(base).forEach(key => {
    const origin = source[key] ?? base[key]
    scriptsState[key] = {
      id: origin.id ?? null,
      category: key,
      contents: Array.isArray(origin.contents) ? [...origin.contents] : [],
      sort_order: origin.sort_order ?? base[key].sort_order,
      status: origin.status ?? 1
    }
  })
}

const resetScriptsState = () => {
  const base = createScriptsRecord()
  applyScriptsRecord(base)
  scriptsSnapshot.value = cloneRecord(base)
  scriptsDirty.value = false
  scriptsLoaded.value = false
}

const scriptList = computed(() =>
  scriptCategories.map(({ label }) => ({
    ...scriptsState[label],
    category: label
  }))
)

const scriptMenuOptions = computed(() => {
  const items = scriptCategories.map(({ label }) => ({
    key: label,
    label,
    count: scriptsState[label]?.contents?.length ?? 0
  }))
  const total = items.reduce((sum, item) => sum + item.count, 0)
  return [{ key: 'all', label: '全部话术', count: total }, ...items]
})

const handlePageChange = current => {
  pagination.current = current
}

const handlePageSizeChange = size => {
  pagination.pageSize = size
  pagination.current = 1
}

const openCreateDrawer = () => {
  drawerMode.value = 'create'
  activeTab.value = 'basic'
  activeScriptCategory.value = 'all'
  currentProjectId.value = null
  Object.assign(formModel, createDefaultForm())
  basicSnapshot.value = createDefaultForm()
  resetScriptsState()
  drawerVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

const openEditDrawer = record => {
  if (record.cover_image_url) {
    record.cover_image_url = `${getConfig('ossUrl')}/${record.cover_image_url}`
  }
  drawerMode.value = 'edit'
  activeTab.value = 'basic'
  activeScriptCategory.value = 'all'
  currentProjectId.value = record.id
  Object.assign(formModel, createDefaultForm(), record)
  basicSnapshot.value = JSON.parse(JSON.stringify(record))
  resetScriptsState()
  drawerVisible.value = true
  nextTick(async () => {
    formRef.value?.clearValidate()
    await loadProjectScripts(record.id)
  })
}

const buildPayload = () => {
  const payload = {}
  Object.entries(formModel).forEach(([key, value]) => {
    if (key === 'id' && drawerMode.value === 'create') return
    if (typeof value === 'string') {
      const trimmed = value.trim()
      if (trimmed || requiredFields.has(key)) {
        payload[key] = trimmed
      }
    } else if (value !== null && value !== undefined) {
      payload[key] = value
    }
    const ossUrl = getConfig('ossUrl')
    if (key === 'cover_image_url' && value) {
      payload[key] = value.substring(ossUrl.length + 1)
    }
  })
  if (drawerMode.value === 'edit') {
    payload.id = formModel.id
  }
  return payload
}

const handleBasicSave = async () => {
  try {
    const errors = await formRef.value?.validate()
    if (errors) return
    const payload = buildPayload()
    if (drawerMode.value === 'create') {
      const res = await productStore.createProduct(payload)
      const newId = res.id
      if (!newId) {
        throw new Error('未获取到项目ID，无法继续编辑话术')
      }
      currentProjectId.value = newId
      drawerMode.value = 'edit'
      AMessage.success('创建成功')
    } else {
      await productStore.updateProduct(payload)
      AMessage.success('更新成功')
    }
    basicSnapshot.value = JSON.parse(JSON.stringify(formModel))
  } catch (error) {
    console.error('保存基本信息失败:', error)
    AMessage.error(error?.message || '保存失败')
  }
}

const transformScriptsToRecord = scripts => {
  const base = createScriptsRecord()
  scripts.forEach(item => {
    const category = item.category
    if (base[category]) {
      base[category] = {
        id: item.id ?? null,
        category,
        contents: Array.isArray(item.contents) ? item.contents : [],
        sort_order:
          typeof item.sort_order === 'number' ? item.sort_order : base[category].sort_order,
        status: typeof item.status === 'number' ? item.status : 1
      }
    }
  })
  return base
}

const loadProjectScripts = async projectId => {
  try {
    const res = await productStore.getProjectScripts(projectId)
    const record = transformScriptsToRecord(res?.scripts || [])
    applyScriptsRecord(record)
    scriptsSnapshot.value = cloneRecord(record)
    scriptsDirty.value = false
    scriptsLoaded.value = true
  } catch (error) {
    console.error('加载项目话术失败:', error)
    AMessage.error(error?.message || '加载话术失败')
  }
}

const markScriptsDirty = () => {
  scriptsDirty.value = true
}

const handleAddScript = category => {
  if (scriptsState[category].contents.length >= 5) {
    AMessage.warning('每个分类最多添加 5 条话术')
    return
  }
  scriptsState[category].contents.push('')
  markScriptsDirty()
}

const handleRemoveScript = (category, index) => {
  scriptsState[category].contents.splice(index, 1)
  markScriptsDirty()
}

const handleScriptsSave = async () => {
  if (!currentProjectId.value) {
    AMessage.warning('请先保存基本信息后再编辑参考话术')
    return
  }
  try {
    const scripts = scriptCategories.map(({ label }) => {
      const state = scriptsState[label]
      const contents = state.contents
        .map(item => item.trim())
        .filter(Boolean)
        .slice(0, 5)
      return {
        category: label,
        contents,
        sort_order: Number(state.sort_order ?? 0),
        status: 1
      }
    })
    const res = await productStore.saveProjectScripts({
      project_id: currentProjectId.value,
      scripts
    })
    const record = transformScriptsToRecord(res?.scripts || [])
    applyScriptsRecord(record)
    scriptsSnapshot.value = cloneRecord(record)
    scriptsDirty.value = false
    scriptsLoaded.value = true
    AMessage.success('参考话术已保存')
  } catch (error) {
    console.error('保存话术失败:', error)
    AMessage.error(error?.message || '保存话术失败')
  }
}

const handleGenerateScripts = async () => {
  if (!currentProjectId.value) {
    AMessage.warning('请先保存基本信息后再生成话术')
    return
  }
  generatingCategory.value = 'all'
  try {
    // 不传 categories 参数，生成所有分类的话术
    const res = await productStore.generateProjectScripts({
      project_id: currentProjectId.value
    })
    if (res?.scripts) {
      // 更新所有分类的话术内容
      res.scripts.forEach(item => {
        if (scriptsState[item.category]) {
          scriptsState[item.category].contents = Array.isArray(item.contents)
            ? item.contents.slice(0, 5)
            : []
        }
      })
      markScriptsDirty()
      AMessage.success('已生成所有分类话术')
    }
  } catch (error) {
    console.error('生成话术失败:', error)
    AMessage.error(error?.message || '生成话术失败')
  } finally {
    generatingCategory.value = ''
  }
}

const handleCoverError = event => {
  event.target.src = defaultCover
}

const handleCoverUploadTrigger = () => {
  fileInputRef.value?.click()
}

const handleCoverFileChange = async event => {
  const [file] = event.target.files || []
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await productStore.uploadFile(formData)
    if (res?.url) {
      formModel.cover_image_url = `${getConfig('ossUrl')}/${res?.url}`
      AMessage.success('图片上传成功')
    } else {
      throw new Error('未获取到图片地址')
    }
  } catch (error) {
    console.error('封面上传失败:', error)
    AMessage.error(error?.message || '图片上传失败')
  } finally {
    if (event.target) {
      event.target.value = ''
    }
  }
}

const handleDelete = async record => {
  AModal.confirm({
    title: '删除主播',
    content: '确定要删除当前项目吗？此操作不可恢复。',
    okText: '删除',
    cancelText: '取消',
    okButtonProps: { status: 'danger' },
    onOk: async () => {
      await productStore.deleteProduct(record.id)
      AMessage.success('删除成功')
      if (products.value.length === 1 && pagination.current > 1) {
        pagination.current -= 1
      }
    }
  })
}

const handleTabChange = async key => {
  if (
    key === 'scripts' &&
    drawerMode.value === 'edit' &&
    currentProjectId.value &&
    !scriptsLoaded.value
  ) {
    await loadProjectScripts(currentProjectId.value)
  }
}

const handleScriptCategoryChange = async key => {
  activeScriptCategory.value = key
}

const displayScriptList = computed(() => {
  if (activeScriptCategory.value === 'all') {
    return scriptList.value
  }
  if (!scriptsState[activeScriptCategory.value]) {
    return []
  }
  return [
    {
      ...scriptsState[activeScriptCategory.value],
      category: activeScriptCategory.value
    }
  ]
})

const resetDrawerState = () => {
  drawerMode.value = 'create'
  activeTab.value = 'basic'
  activeScriptCategory.value = 'all'
  currentProjectId.value = null
  Object.assign(formModel, createDefaultForm())
  basicSnapshot.value = createDefaultForm()
  resetScriptsState()
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
  nextTick(() => formRef.value?.clearValidate())
}

const handleDrawerClose = () => {
  drawerVisible.value = false
}

watch(drawerVisible, visible => {
  if (!visible) {
    resetDrawerState()
  }
})

onMounted(async () => {
  try {
    await productStore.fetchProducts()
  } catch (error) {
    console.error('获取产品数据失败:', error)
  }
})
// 刷新数据
const refreshData = async () => {
  try {
    await productStore.refreshProducts()
  } catch (error) {
    console.error('刷新音色数据失败:', error)
  }
}
</script>

<template>
  <div class="w-full h-full flex flex-col">
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 m-4">
      <div>
        <h2 class="text-xl font-semibold text-[var(--color-text-1)]">我的项目</h2>
        <p class="text-sm text-[var(--color-text-3)] mt-1">管理和维护用于直播的项目/产品</p>
      </div>
    </div>

    <div class="mx-4 mb-4">
      <a-card class="w-full">
        <div class="flex items-center gap-3">
          <a-input-search
            v-model="searchQuery"
            placeholder="请输入项目名称检索"
            style="flex: 1; max-width: 200px"
            size="large"
          />
          <a-select
            v-model="selectedLanguage"
            :options="languageOptions"
            style="width: 120px"
            size="large"
          />
          <a-button
            type="primary"
            size="large"
            style="border-radius: 0.5rem"
            @click="openCreateDrawer"
          >
            <template #icon>
              <icon-material-symbols:add-circle-outline />
            </template>
            创建项目
          </a-button>
          <a-button
            type="outline"
            size="large"
            shape="round"
            :loading="productStore.loading"
            @click="refreshData"
          >
            <template #icon>
              <icon-material-symbols:refresh />
            </template>
            刷新
          </a-button>
        </div>
      </a-card>
    </div>

    <div class="flex-1 mx-4 mb-4">
      <a-card class="h-full w-full">
        <template #title>
          <div class="flex items-center justify-between">
            <span class="text-lg font-semibold">项目列表</span>
            <span class="text-sm text-[var(--color-text-3)]">共 {{ pagination.total }} 条</span>
          </div>
        </template>

        <a-table
          :columns="columns"
          :data="paginatedProducts"
          :loading="productStore.loading"
          :bordered="true"
          :stripe="true"
          :pagination="false"
          row-key="id"
          size="large"
        >
          <template #cover="{ record }">
            <div class="flex justify-center">
              <img
                :src="
                  record.cover_image_url
                    ? `${getConfig('ossUrl')}/${record.cover_image_url}`
                    : defaultCover
                "
                class="w-16 h-16 rounded-xl object-cover border border-[var(--color-border-1)]"
                alt="封面"
                @error="handleCoverError"
              />
            </div>
          </template>

          <template #project_name="{ record }">
            <div class="flex flex-col gap-1">
              <span class="font-medium text-[var(--color-text-1)] text-base">
                {{ record.project_name }}
              </span>
              <span class="text-sm text-[var(--color-text-3)]">
                价格：{{ record.price_info || '—' }}
              </span>
            </div>
          </template>

          <template #delivery_type="{ record }">
            <span class="px-2 py-1 rounded-full bg-blue-50 text-blue-600 text-xs font-medium">
              {{ getDeliveryLabel(record.delivery_type) }}
            </span>
          </template>

          <template #language="{ record }">
            <span class="px-2 py-1 rounded-full bg-blue-50 text-blue-600 text-xs font-medium">
              {{ getLanguageLabel(record.language) }}
            </span>
          </template>

          <template #create_at="{ record }">
            {{ record.create_at ? formatDateTime(record.create_at) : '—' }}
          </template>

          <template #actions="{ record }">
            <a-button type="text" @click="openEditDrawer(record)">
              <icon-material-symbols:contract-edit />编辑项目
            </a-button>
            <a-button
              type="text"
              status="danger"
              :loading="productStore.loadingDelete"
              @click="handleDelete(record)"
            >
              <icon-material-symbols:delete-outline />删除
            </a-button>
          </template>

          <template #empty>
            <div class="text-center py-16">
              <div class="text-6xl text-[var(--color-text-4)] mb-4">
                <icon-material-symbols:production-quantity-limits />
              </div>
              <div class="text-[var(--color-text-3)]">暂无项目数据，请先创建项目</div>
            </div>
          </template>
        </a-table>

        <div class="flex justify-center mt-4" v-if="pagination.total > 0">
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
      </a-card>
    </div>

    <a-drawer
      :visible="drawerVisible"
      :width="980"
      :unmount-on-close="true"
      :footer="false"
      :mask-closable="false"
      @cancel="handleDrawerClose"
    >
      <template #title>
        {{ drawerMode === 'create' ? '创建项目' : '编辑项目' }}
      </template>
      <a-tabs v-model:active-key="activeTab" @change="handleTabChange">
        <a-tab-pane key="basic" title="基本信息">
          <a-form
            ref="formRef"
            :model="formModel"
            :rules="formRules"
            layout="horizontal"
            size="large"
          >
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- 左侧：项目基本信息 -->
              <div class="space-y-4">
                <a-form-item label="选择语种" field="language">
                  <a-select v-model="formModel.language" placeholder="请选择语种">
                    <a-option
                      v-for="item in languageOptions.filter(opt => opt.value !== '全部语言')"
                      :key="item.value"
                      :value="item.value"
                    >
                      {{ item.label }}
                    </a-option>
                  </a-select>
                </a-form-item>
                <a-form-item label="项目名称" field="project_name">
                  <a-input
                    v-model="formModel.project_name"
                    placeholder="请输入项目名称"
                    :max-length="30"
                    show-word-limit
                    allow-clear
                  />
                </a-form-item>
                <a-form-item label="价格信息" field="price_info">
                  <a-input
                    v-model="formModel.price_info"
                    placeholder="请输入产品价格"
                    :max-length="30"
                    show-word-limit
                    allow-clear
                  />
                </a-form-item>
                <a-form-item label="卖点信息" field="selling_points">
                  <a-textarea
                    v-model="formModel.selling_points"
                    placeholder="此项内容是主播深度学习和训练的重要信息，您只需逐点描述清晰，AI主播会在工作中自动生成话术。"
                    :auto-size="{ minRows: 5, maxRows: 5 }"
                    :max-length="600"
                    show-word-limit
                    allow-clear
                  />
                </a-form-item>
                <a-form-item label="详细规格" field="specifications">
                  <a-textarea
                    v-model="formModel.specifications"
                    placeholder="此项内容是主播深度学习和训练的重要信息，您只需逐点描述清晰，AI主播会在工作中自动生成话术。"
                    :auto-size="{ minRows: 5, maxRows: 5 }"
                    :max-length="300"
                    show-word-limit
                    allow-clear
                  />
                </a-form-item>
              </div>

              <!-- 右侧：物流与交付信息 -->
              <div class="space-y-4">
                <a-form-item label="交付类型" field="delivery_type">
                  <a-select v-model="formModel.delivery_type" placeholder="请选择交付类型">
                    <a-option v-for="item in deliveryOptions" :key="item.value" :value="item.value">
                      {{ item.label }}
                    </a-option>
                  </a-select>
                </a-form-item>
                <a-form-item label="发货地点" field="shipping_location">
                  <a-input
                    v-model="formModel.shipping_location"
                    placeholder="如：上海"
                    allow-clear
                  />
                </a-form-item>
                <a-form-item label="运输费用" field="shipping_cost">
                  <a-input
                    v-model="formModel.shipping_cost"
                    placeholder="如：包邮，退货包运费"
                    allow-clear
                  />
                </a-form-item>
                <a-form-item label="快递公司" field="courier_company">
                  <a-input
                    v-model="formModel.courier_company"
                    placeholder="如：顺丰速运"
                    allow-clear
                  />
                </a-form-item>
                <a-form-item label="发货时效" field="shipping_time">
                  <a-input
                    v-model="formModel.shipping_time"
                    placeholder="如：当天发货"
                    allow-clear
                  />
                </a-form-item>

                <!-- 上传项目封面 -->
                <a-form-item label="项目封面" field="cover_image_url">
                  <div
                    v-if="!formModel.cover_image_url"
                    class="border-2 border-dashed border-[var(--color-border-1)] rounded-lg p-2 text-center cursor-pointer hover:bg-[var(--color-fill-2)] transition-colors"
                    @click="handleCoverUploadTrigger"
                  >
                    <div class="flex flex-col items-center justify-center gap-1">
                      <icon-material-symbols:upload class="w-8 h-8 text-[var(--color-primary)]" />
                      <span class="text-sm font-medium text-[var(--color-primary)]"
                        >上传项目封面</span
                      >
                      <div class="text-xs text-[var(--color-text-3)]">
                        <p>1. 项目封面将便于用户快速识别项目</p>
                        <p>2. 仅限一张图片</p>
                      </div>
                    </div>
                  </div>
                  <div v-else class="flex flex-col items-center gap-2">
                    <img
                      :src="formModel.cover_image_url"
                      class="w-24 h-24 object-cover rounded-lg border border-[var(--color-border-1)]"
                      alt="封面预览"
                      @error="handleCoverError"
                    />
                    <a-button type="outline" size="small" @click="handleCoverUploadTrigger"
                      >更换图片</a-button
                    >
                  </div>
                  <input
                    ref="fileInputRef"
                    type="file"
                    accept="image/*"
                    class="hidden"
                    @change="handleCoverFileChange"
                  />
                </a-form-item>
              </div>
            </div>
          </a-form>

          <div class="flex justify-end gap-3 mt-6">
            <a-button type="primary" :loading="productStore.loading" @click="handleBasicSave">
              保存基本信息
            </a-button>
          </div>
        </a-tab-pane>
        <a-tab-pane key="scripts" title="参考话术">
          <a-spin :loading="scriptsLoading">
            <div v-if="!currentProjectId" class="py-20 text-center text-[var(--color-text-3)]">
              请先保存基本信息后，再编辑参考话术。
            </div>
            <template v-else>
              <div class="bg-[var(--color-fill-2)] p-3 rounded-xl mb-2">
                <div class="flex text-[var(--color-warning-light-4)]">
                  <icon-material-symbols:error-outline class="w-4 h-4 mr-2 mt-1 flex-shrink-0" />
                  <div>
                    参考话术库是AI主播的学习素材，而非完整的直播脚本。您无需录入大量话术，只需提供少量有代表性的内容，帮助AI主播理解您的风格和表达方式。AI会通过这些样本学习您的语气、节奏和专业知识，并在直播中自然延伸和变化。精选的几条高质量话术，往往比堆砌大量重复内容更有效。让AI主播模仿您的精华，而非局限于固定台词，这样才能打造既专业又灵活的直播体验。
                  </div>
                </div>
              </div>
              <div class="flex justify-end mb-2 space-x-4">
                <a-button
                  type="primary"
                  :loading="productStore.loadingScripts"
                  @click="handleGenerateScripts"
                >
                  <template #icon>
                    <icon-material-symbols:auto-awesome />
                  </template>
                  一键生成所有话术
                </a-button>
                <a-button
                  type="primary"
                  :loading="productStore.loadingScripts"
                  @click="handleScriptsSave"
                >
                  保存参考话术
                </a-button>
              </div>
              <div class="flex flex-col gap-4 md:flex-row">
                <a-card class="md:w-56 w-full h-fit" :bordered="true">
                  <template #title>
                    <span class="text-sm font-semibold">话术分类</span>
                  </template>
                  <a-menu
                    :selected-keys="[activeScriptCategory]"
                    @menu-item-click="handleScriptCategoryChange"
                    mode="vertical"
                  >
                    <a-menu-item
                      v-for="option in scriptMenuOptions"
                      :key="option.key"
                      :disabled="option.key !== 'all' && !scriptsState[option.key]"
                    >
                      <div class="flex justify-between items-center">
                        <span>{{ option.label }}</span>
                        <a-tag size="small" color="blue">{{ option.count ?? 0 }}</a-tag>
                      </div>
                    </a-menu-item>
                  </a-menu>
                </a-card>

                <div class="flex-1 overflow-y-auto -[calc(100vh-16rmax-hem)]">
                  <div class="space-y-4">
                    <template v-if="displayScriptList.length">
                      <a-card v-for="item in displayScriptList" :key="item.category">
                        <template #title>
                          <div
                            class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between"
                          >
                            <div class="flex items-center gap-2">
                              <span class="text-lg font-semibold">{{ item.category }}</span>
                            </div>
                            <div class="flex flex-wrap items-center gap-3">
                              <div class="flex items-center gap-2">
                                <span class="text-xs text-[var(--color-text-3)]">排序</span>
                                <a-input-number
                                  v-model="scriptsState[item.category].sort_order"
                                  disabled
                                />
                              </div>
                            </div>
                          </div>
                        </template>
                        <div class="space-y-4">
                          <div
                            v-for="(content, index) in scriptsState[item.category].contents"
                            :key="`${item.category}-${index}`"
                          >
                            <div class="flex items-center gap-2">
                              <a-textarea
                                v-model="scriptsState[item.category].contents[index]"
                                placeholder="请输入话术内容"
                                :auto-size="{ minRows: 2, maxRows: 2 }"
                                allow-clear
                                @input="markScriptsDirty"
                                :max-length="300"
                                show-word-limit
                              />
                              <a-button
                                type="text"
                                status="danger"
                                size="mini"
                                @click="handleRemoveScript(item.category, index)"
                              >
                                <template #icon>
                                  <icon-material-symbols:delete-outline />
                                </template>
                              </a-button>
                            </div>
                          </div>
                          <div
                            v-if="scriptsState[item.category].contents.length === 0"
                            class="text-sm text-[var(--color-text-3)]"
                          >
                            暂无话术内容，请点击下方按钮新增。
                          </div>
                          <a-button
                            type="outline"
                            size="small"
                            @click="handleAddScript(item.category)"
                            :disabled="scriptsState[item.category].contents.length >= 5"
                          >
                            新增话术
                          </a-button>
                        </div>
                      </a-card>
                    </template>
                  </div>
                </div>
              </div>
            </template>
          </a-spin>
        </a-tab-pane>
      </a-tabs>
    </a-drawer>
  </div>
</template>

<style scoped>
::deep(.arco-card-header) {
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-neutral-3);
}

::deep(.arco-card-body) {
  padding: 0;
}

::deep(.arco-table-td),
::deep(.arco-table-th .arco-table-cell) {
  text-align: center;
  justify-content: center;
}

::deep(.arco-drawer-header) {
  border-bottom: 1px solid var(--color-neutral-3);
}
</style>
