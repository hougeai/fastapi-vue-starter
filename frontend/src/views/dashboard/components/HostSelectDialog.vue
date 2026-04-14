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
        <div class="text-xl font-bold">选择主播</div>
      </div>
    </template>

    <!-- 主播选择区域 -->

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <!-- 创建虚拟主播卡片 -->
      <div
        class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-4 flex flex-col items-center justify-center cursor-pointer hover:bg-[var(--color-fill-2)] transition-colors"
        @click="createVirtualHost"
      >
        <div class="text-2xl mb-2">
          <icon-material-symbols:add-circle-outline class="text-gray-500" />
        </div>
        <div class="font-medium text-gray-700">创建虚拟主播</div>
      </div>

      <!-- 已有主播卡片 -->
      <div
        v-for="host in hosts"
        :key="host.id"
        class="border border-dashed border-[var(--color-fill-4)] rounded-lg p-4 flex flex-col items-center cursor-pointer hover:bg-[var(--color-fill-2)] transition-colors relative"
        :class="{ 'ring-2 ring-[var(--color-danger-light-4)]': selectHost?.id === host.id }"
        @click="selectHost = host"
      >
        <div class="absolute top-2 right-2">
          <a-checkbox :model-value="selectHost?.id === host.id" class="cursor-pointer" />
        </div>
        <img
          :src="host.avatar || getConfig('me.avatar')"
          alt="avatar"
          class="w-12 h-12 rounded-full object-cover mb-3"
        />
        <div class="font-medium">{{ host.name }}</div>
        <a-tag size="small" color="orange">
          {{ getLanguageLabel(host.lang) }}
        </a-tag>
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
import { useHostStore } from '@/stores/host'
import { getConfig, getLanguageLabel } from '@/config/index'
import { useRouter } from 'vue-router'

const router = useRouter()

// Props
const props = defineProps({
  visible: Boolean,
  hostAgent: Object
})

const emit = defineEmits(['update:visible', 'update:host'])

const hostStore = useHostStore()
const hosts = computed(() => hostStore.hosts)
const selectHost = ref(null)

watch(
  () => props.visible,
  newVisible => {
    if (newVisible) {
      // 如果传入了hostAgent，则将其设为当前选中的主播
      selectHost.value = props.hostAgent || null
    }
  }
)
const createVirtualHost = () => {
  router.push('/dashboard/host-agent')
}
// 取消
const handleCancel = () => {
  emit('update:visible', false)
}

// 确定
const handleOk = () => {
  if (!selectHost.value) {
    AMessage.warning('请选择一个主播')
    return
  }
  emit('update:host', selectHost.value)
  emit('update:visible', false)
}
</script>
