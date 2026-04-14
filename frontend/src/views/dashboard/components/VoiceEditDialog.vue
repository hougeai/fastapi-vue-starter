NEW_FILE_CODE
<template>
  <a-modal
    :visible="visible"
    @cancel="handleCancel"
    @ok="handleOk"
    :mask-closable="false"
    width="500px"
    class="rounded-2xl shadow-2xl"
    centered
  >
    <template #title>
      <div class="flex items-center">
        <icon-material-symbols:contract-edit
          class="text-[var(--color-primary-light-4)] text-xl mr-1"
        />
        <div class="text-xl font-bold">编辑音色</div>
      </div>
    </template>

    <a-form :model="form" :rules="rules" ref="formRef" layout="vertical">
      <a-form-item field="name" label="音色名称" required>
        <a-input v-model="form.name" placeholder="请输入音色名称" />
      </a-form-item>

      <a-form-item field="lang" label="语种" required>
        <a-select v-model="form.lang" placeholder="请选择语种">
          <a-option
            v-for="option in props.languageOptions"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </a-option>
        </a-select>
      </a-form-item>

      <a-form-item field="gender" label="性别" required>
        <a-radio-group v-model="form.gender">
          <a-radio value="female">女性</a-radio>
          <a-radio value="male">男性</a-radio>
        </a-radio-group>
      </a-form-item>

      <a-form-item field="note" label="备注">
        <a-input v-model="form.note" placeholder="请输入备注(可选)" show-word-limit />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useVoiceStore } from '@/stores/voice'

const voiceStore = useVoiceStore()

// Props
const props = defineProps({
  visible: Boolean,
  languageOptions: {
    type: Array,
    default: () => [
      { label: '英语', value: '英语' },
      { label: '中文', value: '中文' }
    ]
  },
  voice: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:visible'])

// 表单相关
const formRef = ref()
const form = reactive({
  id: '',
  name: '',
  lang: '',
  gender: '',
  note: ''
})

const rules = {
  name: [
    { required: true, message: '请输入音色名称' },
    { min: 1, max: 12, message: '音色名称长度应在1-12个字符之间', trigger: 'blur' }
  ],
  lang: [{ required: true, message: '请选择语种' }],
  gender: [{ required: true, message: '请选择性别' }]
}

// 监听对话框显示状态，设置表单数据
watch(
  () => props.visible,
  newVal => {
    if (newVal && props.voice) {
      form.id = props.voice.id
      form.name = props.voice.name
      form.lang = props.voice.lang
      form.gender = props.voice.gender
      form.note = props.voice.note
    }
  }
)

const handleCancel = () => {
  emit('update:visible', false)
}

const handleOk = async () => {
  const errors = await formRef.value.validate()
  if (errors) return

  try {
    const data = {
      id: form.id,
      name: form.name,
      lang: form.lang,
      gender: form.gender,
      note: form.note
    }
    await voiceStore.updateVoice(data)
    emit('update:visible', false)
  } catch (error) {
    console.error(error)
  }
}
</script>
