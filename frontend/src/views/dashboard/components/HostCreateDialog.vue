<template>
  <a-modal
    :visible="visible"
    @cancel="handleCancel"
    :footer="null"
    :mask-closable="false"
    width="80%"
    class="rounded-2xl shadow-2xl"
    centered
  >
    <template #title>
      <div class="flex items-center justify-between pr-2">
        <icon-ri-user-line class="text-[var(--color-primary-light-4)] text-xl mr-1" />
        <div class="text-2xl font-bold">主播角色设定</div>
      </div>
    </template>

    <!-- 主体内容区域 -->
    <a-form :model="form" :rules="formRules" ref="formRef" layout="horizontal" :label-align="left">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 p-4">
        <!-- 左侧列：语种与语音样本 -->
        <div class="md:col-span-1">
          <div class="border-b">
            <h3 class="text-lg font-semibold mb-4">01 主播基本信息</h3>
            <div class="flex items-center justify-center mb-4">
              <img
                :src="getConfig('me.avatar')"
                alt="主播头像"
                class="w-16 h-16 rounded-full object-cover border-2 border-gray-300"
              />
            </div>
            <a-form-item field="language" label="主播语种">
              <a-select v-model="form.language" placeholder="请选择语种" style="width: 100%">
                <a-option
                  v-for="option in props.languageOptions"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </a-option>
              </a-select>
            </a-form-item>

            <a-form-item field="voiceSample" label="主播音色">
              <a-select v-model="form.voiceSample" placeholder="请选择音色样本" style="width: 100%">
                <a-option v-for="voice in voices" :key="voice.id" :value="voice.id">
                  {{ voice.name }}
                </a-option>
              </a-select>
            </a-form-item>
            <a-form-item field="hostName" label="主播名称">
              <a-input
                v-model="form.hostName"
                placeholder="请输入主播名称"
                :max-length="20"
                show-word-limit
                class="w-full"
              />
            </a-form-item>
            <a-form-item field="gender" label="主播性别">
              <a-radio-group v-model="form.gender">
                <a-radio value="male">男性</a-radio>
                <a-radio value="female">女性</a-radio>
              </a-radio-group>
            </a-form-item>
          </div>
          <!-- 警告提示 -->
          <div class="bg-[var(--color-fill-2)] p-3 rounded-xl">
            <div class="flex text-[var(--color-warning-light-4)]">
              <icon-material-symbols:error-outline class="w-4 h-4 mr-2 mt-1 flex-shrink-0" />
              <div>
                请认真选择主播使用的语种和音色，这将决定未来主播直播时所使用的语言。当主播语种和项目语种一致时，才能正常直播。变更主播语种可能导致一些历史数据丢失。
              </div>
            </div>
          </div>
        </div>

        <!-- 中间列：主播基本信息 -->
        <div class="md:col-span-1 space-y-6">
          <!-- 专业领域 -->
          <div class="border-b pb-4">
            <h3 class="text-lg font-semibold mb-4">02 主播专业领域</h3>
            <p class="text-xs text-[var(--color-warning-light-4)] mb-3">
              选择或添加AI主播擅长的专业领域知识偏向，这将影响后续角色设定的初始参数生成。最多选2类。
            </p>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-4">
              <template v-for="(category, index) in categories" :key="index">
                <a-button
                  :type="selectedCategories.includes(category.value) ? 'primary' : 'default'"
                  size="small"
                  class="border-dashed border-1.5 border-[var(--color-primary-light-4)]"
                  style="border-radius: 0.5rem"
                  @click="toggleCategory(category.value)"
                >
                  {{ category.label }}
                </a-button>
              </template>
              <div v-if="!showAddCategoryInput" class="flex justify-center items-center">
                <a-button
                  size="small"
                  class="border-dashed border-1.5 border-[var(--color-primary-light-4)] w-full h-full"
                  style="border-radius: 0.5rem"
                  @click="showAddCategoryInput = true"
                >
                  <icon-material-symbols:add class="text-lg" />
                </a-button>
              </div>
              <div v-else class="col-span-1">
                <a-input
                  v-model="newCategory"
                  size="small"
                  placeholder="输入新领域"
                  class="w-full"
                  @keydown.enter="addNewCategory"
                  @blur="cancelAddCategory"
                />
              </div>
            </div>
            <div class="flex justify-center">
              <a-button
                type="primary"
                shape="round"
                :loading="hostStore.loadingGenerate"
                @click="generateContent"
              >
                <icon-material-symbols:auto-mode class="mr-2" />一键生成主播背景与个性特征
              </a-button>
            </div>
          </div>
        </div>

        <!-- 右侧列：背景与个性特征 -->
        <div class="md:col-span-1 space-y-6">
          <div class="border-b pb-4">
            <h3 class="text-lg font-semibold mb-4">03 主播背景与个性特征</h3>
            <div class="flex flex-wrap gap-2 mb-4">
              <div>主播标签</div>
              <a-tag v-for="tag in tags" :key="tag" color="blue">{{ tag }}</a-tag>
            </div>
            <a-form-item field="background" label="主播背景">
              <a-textarea
                v-model="form.background"
                placeholder="请输入主播背景介绍..."
                :auto-size="{ minRows: 6, maxRows: 6 }"
                :max-length="300"
                show-word-limit
                allow-clear
                class="w-full"
              />
            </a-form-item>
            <a-form-item field="personality" label="个性特征">
              <a-textarea
                v-model="form.personality"
                placeholder="请输入主播个性特征..."
                :auto-size="{ minRows: 6, maxRows: 6 }"
                :max-length="300"
                show-word-limit
                class="w-full"
              />
            </a-form-item>
            <!-- 底部操作栏 -->
            <div class="flex justify-end space-x-4 mt-6 pl-6">
              <a-button @click="handleCancel">取消</a-button>
              <a-button type="primary" :loading="hostStore.loading" @click="saveAndUpdate">
                保存并更新
              </a-button>
            </div>
          </div>
        </div>
      </div>
    </a-form>
  </a-modal>
</template>

<script setup>
import { useHostStore } from '@/stores/host'
import { useVoiceStore } from '@/stores/voice'
import { getConfig } from '@/config/index'

const hostStore = useHostStore()
const voiceStore = useVoiceStore()
// 计算属性
const voices = computed(() => voiceStore.voices)

// 对话框控制
const props = defineProps({
  visible: Boolean,
  mode: {
    type: String,
    default: 'create' // 'create' 或 'edit'
  },
  hostData: {
    type: Object,
    default: () => null
  },
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
      // 重置新增分类相关的状态
      showAddCategoryInput.value = false
      newCategory.value = ''
      // 根据模式设置表单数据
      if (props.mode === 'edit' && props.hostData) {
        const host = props.hostData
        form.value = {
          language: host.lang,
          voiceSample: host.voice_id,
          hostName: host.name,
          gender: host.gender,
          background: host.background,
          personality: host.personality
        }
        tags.value = host.tags ? host.tags.split('|') : []
        selectedCategories.value = host.categories ? host.categories.split('|') : []
      } else {
        // 重置表单数据
        form.value = {
          language: '',
          voiceSample: '',
          hostName: '',
          gender: '',
          background: '',
          personality: ''
        }
        tags.value = []
        selectedCategories.value = []
      }
      formRef.value?.clearValidate()
    }
  }
)

// 数据绑定
const formRef = ref(null)

// 表单数据模型
const form = ref({
  language: '',
  voiceSample: '',
  hostName: '',
  gender: '',
  background: '',
  personality: ''
})

// 表单验证规则
const formRules = {
  language: [
    {
      required: true,
      message: '请选择主播语种'
    }
  ],
  voiceSample: [
    {
      required: true,
      message: '请选择音色样本'
    }
  ],
  hostName: [
    {
      required: true,
      message: '请输入主播名称'
    }
  ],
  gender: [
    {
      required: true,
      message: '请选择主播性别'
    }
  ],
  background: [
    {
      required: true,
      message: '请输入角色背景'
    }
  ],
  personality: [
    {
      required: true,
      message: '请输入个性特征'
    }
  ]
}

const tags = ref([])

// 专业领域选项
const categories = ref([
  { label: '护肤', value: '护肤' },
  { label: '时尚', value: '时尚' },
  { label: '手机数码', value: '手机数码' },
  { label: '美食', value: '美食' },
  { label: '旅游', value: '旅游' },
  { label: '娱乐', value: '娱乐' },
  { label: '家具', value: '家具' },
  { label: '鞋靴皮具', value: '鞋靴皮具' },
  { label: '儿童用品', value: '儿童用品' },
  { label: '家居家纺', value: '家居家纺' },
  { label: '食品生鲜', value: '食品生鲜' },
  { label: '影像音乐', value: '影像音乐' },
  { label: '健康', value: '健康' },
  { label: '游戏动漫', value: '游戏动漫' },
  { label: '教育', value: '教育' },
  { label: '珠宝首饰', value: '珠宝首饰' },
  { label: '汽车用品', value: '汽车用品' },
  { label: '宠物', value: '宠物' },
  { label: '服饰箱包', value: '服饰箱包' },
  { label: '运动户外', value: '运动户外' },
  { label: '母婴孕产', value: '母婴孕产' },
  { label: '美容医疗', value: '美容医疗' }
])

const selectedCategories = ref([])
const showAddCategoryInput = ref(false)
const newCategory = ref('')

const toggleCategory = value => {
  if (selectedCategories.value.includes(value)) {
    selectedCategories.value = selectedCategories.value.filter(item => item !== value)
  } else {
    if (selectedCategories.value.length >= 2) {
      AMessage.warning('最多选2个专业领域')
      return
    }
    selectedCategories.value = [...selectedCategories.value, value]
  }
}

const addNewCategory = () => {
  if (newCategory.value.trim() !== '') {
    // 检查是否已存在同名分类
    const isDuplicate = categories.value.some(
      category => category.label === newCategory.value.trim()
    )

    if (!isDuplicate) {
      // 添加新分类到列表
      categories.value.push({
        label: newCategory.value.trim(),
        value: newCategory.value.trim()
      })
      // 如果当前选择少于2个，则自动选中新添加的分类
      if (selectedCategories.value.length < 2) {
        selectedCategories.value.push(newCategory.value.trim())
      }
      AMessage.success('新领域添加成功')
    } else {
      AMessage.warning('该领域已存在')
    }
    newCategory.value = ''
  }

  showAddCategoryInput.value = false
  console.log(selectedCategories.value)
}

const cancelAddCategory = () => {
  newCategory.value = ''
  showAddCategoryInput.value = false
}

// 一键生成逻辑
const generateContent = async () => {
  const errors = await formRef.value.validateField(['language', 'hostName', 'gender'])
  if (errors) return
  if (!selectedCategories.value.length) {
    AMessage.warning('请先选择主播专业领域')
    return
  }
  try {
    const data = {
      lang: form.value.language,
      name: form.value.hostName,
      gender: form.value.gender,
      categories: selectedCategories.value.filter(cat => cat !== '').join('|')
    }
    const result = await hostStore.generateContent(data)
    tags.value = result?.tags ? result.tags.split('|') : []
    form.value.background = result?.background || ''
    form.value.personality = result?.personality || ''
  } catch (error) {
    console.error(error)
  }
}

// 保存并更新
const saveAndUpdate = async () => {
  const errors = await formRef.value.validate()
  if (errors) return
  if (!selectedCategories.value.length) {
    AMessage.warning('请先选择主播专业领域')
    return
  }
  try {
    const data = {
      lang: form.value.language,
      voice_id: form.value.voiceSample,
      name: form.value.hostName,
      gender: form.value.gender,
      categories: selectedCategories.value.filter(cat => cat !== '').join('|'),
      tags: tags.value.filter(tag => tag !== '').join('|'),
      background: form.value.background,
      personality: form.value.personality
    }
    if (props.mode === 'edit' && props.hostData) {
      await hostStore.updateHost({ id: props.hostData.id, ...data })
      AMessage.success('主播更新成功！')
    } else {
      await hostStore.createHost(data)
      AMessage.success('主播创建成功！')
    }
    emit('update:visible', false)
  } catch (error) {
    console.error(error)
    AMessage.error('创建失败，请重试')
  }
}

// 关闭对话框
const handleCancel = () => {
  emit('update:visible', false)
}
</script>

<style scoped>
/* 自定义样式 */
.ant-btn-primary {
  background-color: #ff4d4f;
  border-color: #ff4d4f;
}
.ant-btn-primary:hover {
  background-color: #e63939;
}

:deep(.arco-form-item-label) {
  white-space: nowrap;
}
</style>
