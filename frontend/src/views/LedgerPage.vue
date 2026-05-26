<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLedgerStore } from '@/stores/ledger'
import { Message } from '@arco-design/web-vue'

const router = useRouter()
const ledgerStore = useLedgerStore()

const loading = computed(() => ledgerStore.loading)
const ledgers = computed(() => ledgerStore.ledgers)
const templates = computed(() => ledgerStore.templates)

// 弹窗相关
const showCreateModal = ref(false)
const showTemplateModal = ref(false)
const showEditModal = ref(false)
const createFormRef = ref()
const editFormRef = ref()
const submitLoading = ref(false)

// 创建表单
const createForm = ref({
  name: '',
  description: ''
})

const createRules = {
  name: [{ required: true, message: '请输入账本名称' }]
}

// 编辑表单
const editForm = ref({
  id: null,
  name: '',
  description: ''
})

const editRules = {
  name: [{ required: true, message: '请输入账本名称' }]
}

// 模板创建表单
const templateFormRef = ref()
const selectedTemplateId = ref(null)
const templateForm = ref({
  name: '',
  description: ''
})

const templateRules = {
  name: [{ required: true, message: '请输入账本名称' }]
}

// 打开创建弹窗
const openCreateModal = () => {
  createForm.value = { name: '', description: '' }
  showCreateModal.value = true
}

// 提交创建
const handleCreate = async () => {
  try {
    const errors = await createFormRef.value?.validate()
    if (errors) return
    submitLoading.value = true
    const res = await ledgerStore.createLedger(createForm.value)
    if (res.code === 200) {
      Message.success('创建成功')
      showCreateModal.value = false
    } else {
      Message.error(res.msg || '创建失败')
    }
  } catch (e) {
    Message.error(e?.message || '创建失败')
  } finally {
    submitLoading.value = false
  }
}

// 打开编辑弹窗
const openEditModal = (ledger) => {
  editForm.value = { id: ledger.id, name: ledger.name, description: ledger.description || '' }
  showEditModal.value = true
}

// 提交编辑
const handleEdit = async () => {
  try {
    const errors = await editFormRef.value?.validate()
    if (errors) return
    submitLoading.value = true
    const { id, ...data } = editForm.value
    const res = await ledgerStore.updateLedger(id, data)
    if (res.code === 200) {
      Message.success('更新成功')
      showEditModal.value = false
    } else {
      Message.error(res.msg || '更新失败')
    }
  } catch (e) {
    Message.error(e?.message || '更新失败')
  } finally {
    submitLoading.value = false
  }
}

// 删除账本
const handleDelete = (ledger) => {
  AModal.confirm({
    title: '删除账本',
    content: `确定要删除账本「${ledger.name}」吗？此操作不可恢复。`,
    okText: '删除',
    cancelText: '取消',
    okButtonProps: { status: 'danger' },
    onOk: async () => {
      const res = await ledgerStore.deleteLedger(ledger.id)
      if (res.code === 200) {
        Message.success('删除成功')
      } else {
        Message.error(res.msg || '删除失败')
      }
    }
  })
}

// 设为默认
const handleSetDefault = async (ledger) => {
  const res = await ledgerStore.setDefaultLedger(ledger.id)
  if (res.code === 200) {
    Message.success('已设为默认账本')
  } else {
    Message.error(res.msg || '设置失败')
  }
}

// 打开模板创建弹窗
const openTemplateModal = async () => {
  selectedTemplateId.value = null
  templateForm.value = { name: '', description: '' }
  await ledgerStore.fetchTemplates()
  showTemplateModal.value = true
}

// 从模板创建
const handleTemplateCreate = async () => {
  try {
    if (!selectedTemplateId.value) {
      Message.warning('请选择一个模板')
      return
    }
    const errors = await templateFormRef.value?.validate()
    if (errors) return
    submitLoading.value = true
    const res = await ledgerStore.createFromTemplate(
      selectedTemplateId.value,
      templateForm.value.name,
      templateForm.value.description
    )
    if (res.code === 200) {
      Message.success('从模板创建成功')
      showTemplateModal.value = false
    } else {
      Message.error(res.msg || '创建失败')
    }
  } catch (e) {
    Message.error(e?.message || '创建失败')
  } finally {
    submitLoading.value = false
  }
}

// 切换当前账本
const switchLedger = (ledger) => {
  ledgerStore.setCurrentLedger(ledger)
  Message.success(`已切换到「${ledger.name}」`)
}

// 初始化
onMounted(async () => {
  await ledgerStore.fetchLedgerList()
})
</script>

<template>
  <div class="w-full min-h-screen bg-[var(--color-fill-1)]">
    <!-- 顶部区域 -->
    <div class="bg-gradient-to-br from-green-50 via-emerald-50 to-white px-6 pt-6 pb-4">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-[var(--color-text-1)]">账本管理</h1>
          <p class="text-sm text-[var(--color-text-3)] mt-1">管理你的账本，或从模板快速创建</p>
        </div>
        <div class="flex gap-2">
          <a-button type="primary" @click="openCreateModal">
            <template #icon><icon-material-symbols:add /></template>
            创建账本
          </a-button>
          <a-button type="outline" @click="openTemplateModal">
            <template #icon><icon-material-symbols:dashboard-customize-outline /></template>
            从模板创建
          </a-button>
        </div>
      </div>
    </div>

    <!-- 账本列表 -->
    <div class="px-4 pt-4 pb-4">
      <a-spin :loading="loading" class="w-full">
        <!-- 有账本 -->
        <div v-if="ledgers.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="ledger in ledgers"
            :key="ledger.id"
            class="bg-[var(--color-bg-2)] rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-shadow"
          >
            <!-- 卡片头部 -->
            <div class="p-4">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                  <div class="w-9 h-9 rounded-full bg-green-100 flex items-center justify-center">
                    <icon-material-symbols:account-balance-wallet-outline class="text-lg text-green-500" />
                  </div>
                  <div>
                    <div class="font-medium text-[var(--color-text-1)]">{{ ledger.name }}</div>
                    <div class="text-xs text-[var(--color-text-3)]">{{ ledger.description || '暂无描述' }}</div>
                  </div>
                </div>
                <a-tag v-if="ledger.is_default" size="small" color="arcoblue">默认</a-tag>
              </div>

              <!-- 账本统计 -->
              <div class="grid grid-cols-3 gap-2 text-center">
                <div class="bg-[var(--color-fill-2)] rounded-lg py-2">
                  <div class="text-xs text-[var(--color-text-3)]">收入</div>
                  <div class="text-sm font-semibold text-green-500">{{ ledger.total_income || '0.00' }}</div>
                </div>
                <div class="bg-[var(--color-fill-2)] rounded-lg py-2">
                  <div class="text-xs text-[var(--color-text-3)]">支出</div>
                  <div class="text-sm font-semibold text-red-500">{{ ledger.total_expense || '0.00' }}</div>
                </div>
                <div class="bg-[var(--color-fill-2)] rounded-lg py-2">
                  <div class="text-xs text-[var(--color-text-3)]">笔数</div>
                  <div class="text-sm font-semibold text-[var(--color-text-1)]">{{ ledger.tx_count || 0 }}</div>
                </div>
              </div>
            </div>

            <!-- 卡片底部操作 -->
            <div class="flex items-center justify-between px-4 py-2 border-t border-[var(--color-border-1)]">
              <div class="text-xs text-[var(--color-text-3)]">
                创建于 {{ ledger.create_at?.split(' ')[0] || '-' }}
              </div>
              <div class="flex items-center gap-1">
                <a-tooltip content="切换使用">
                  <a-button
                    type="text"
                    size="mini"
                    :status="ledgerStore.currentLedger?.id === ledger.id ? 'success' : 'normal'"
                    @click="switchLedger(ledger)"
                  >
                    <template #icon>
                      <icon-material-symbols:swap-horiz v-if="ledgerStore.currentLedger?.id !== ledger.id" />
                      <icon-material-symbols:check-circle v-else />
                    </template>
                  </a-button>
                </a-tooltip>
                <a-tooltip v-if="!ledger.is_default" content="设为默认">
                  <a-button type="text" size="mini" @click="handleSetDefault(ledger)">
                    <template #icon><icon-material-symbols:star-outline /></template>
                  </a-button>
                </a-tooltip>
                <a-tooltip content="编辑">
                  <a-button type="text" size="mini" @click="openEditModal(ledger)">
                    <template #icon><icon-material-symbols:edit-outline /></template>
                  </a-button>
                </a-tooltip>
                <a-tooltip content="删除">
                  <a-button type="text" size="mini" status="danger" @click="handleDelete(ledger)">
                    <template #icon><icon-material-symbols:delete-outline /></template>
                  </a-button>
                </a-tooltip>
              </div>
            </div>
          </div>
        </div>

        <!-- 无账本 -->
        <div v-else class="bg-[var(--color-bg-2)] rounded-xl p-8 shadow-sm text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 flex items-center justify-center">
            <icon-material-symbols:book-2-outline class="text-3xl text-green-500" />
          </div>
          <h3 class="text-lg font-semibold text-[var(--color-text-1)] mb-2">还没有账本</h3>
          <p class="text-sm text-[var(--color-text-3)] mb-6">创建一个账本，开始记录你的收支吧</p>
          <div class="flex justify-center gap-3">
            <a-button type="primary" @click="openCreateModal">
              <template #icon><icon-material-symbols:add /></template>
              创建账本
            </a-button>
            <a-button type="outline" @click="openTemplateModal">
              <template #icon><icon-material-symbols:dashboard-customize-outline /></template>
              从模板创建
            </a-button>
          </div>
        </div>
      </a-spin>
    </div>

    <!-- 创建账本弹窗 -->
    <a-modal
      v-model:visible="showCreateModal"
      title="创建账本"
      :mask-closable="false"
      @ok="handleCreate"
      :ok-loading="submitLoading"
      ok-text="创建"
    >
      <a-form ref="createFormRef" :model="createForm" :rules="createRules" layout="vertical">
        <a-form-item field="name" label="账本名称">
          <a-input v-model="createForm.name" placeholder="请输入账本名称" :max-length="30" />
        </a-form-item>
        <a-form-item field="description" label="账本描述">
          <a-textarea v-model="createForm.description" placeholder="请输入账本描述（可选）" :max-length="200" :auto-size="{ minRows: 2, maxRows: 4 }" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 编辑账本弹窗 -->
    <a-modal
      v-model:visible="showEditModal"
      title="编辑账本"
      :mask-closable="false"
      @ok="handleEdit"
      :ok-loading="submitLoading"
      ok-text="保存"
    >
      <a-form ref="editFormRef" :model="editForm" :rules="editRules" layout="vertical">
        <a-form-item field="name" label="账本名称">
          <a-input v-model="editForm.name" placeholder="请输入账本名称" :max-length="30" />
        </a-form-item>
        <a-form-item field="description" label="账本描述">
          <a-textarea v-model="editForm.description" placeholder="请输入账本描述（可选）" :max-length="200" :auto-size="{ minRows: 2, maxRows: 4 }" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 从模板创建弹窗 -->
    <a-modal
      v-model:visible="showTemplateModal"
      title="从模板创建账本"
      :mask-closable="false"
      @ok="handleTemplateCreate"
      :ok-loading="submitLoading"
      ok-text="创建"
    >
      <a-form ref="templateFormRef" :model="templateForm" :rules="templateRules" layout="vertical">
        <a-form-item label="选择模板">
          <a-radio-group v-model="selectedTemplateId" direction="vertical">
            <a-radio v-for="tpl in templates" :key="tpl.id" :value="tpl.id">
              <div class="flex items-center gap-2">
                <span class="font-medium">{{ tpl.name }}</span>
                <span class="text-xs text-[var(--color-text-3)]">{{ tpl.description || '' }}</span>
              </div>
            </a-radio>
          </a-radio-group>
          <div v-if="!templates.length" class="text-sm text-[var(--color-text-3)] py-4 text-center">
            暂无可用模板
          </div>
        </a-form-item>
        <a-form-item field="name" label="账本名称">
          <a-input v-model="templateForm.name" placeholder="请输入账本名称" :max-length="30" />
        </a-form-item>
        <a-form-item field="description" label="账本描述">
          <a-textarea v-model="templateForm.description" placeholder="请输入账本描述（可选）" :max-length="200" :auto-size="{ minRows: 2, maxRows: 4 }" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>
