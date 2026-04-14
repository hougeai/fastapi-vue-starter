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
        <div class="text-xl font-bold">设置直播目标</div>
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
          为AI主播设定明确的直播目标，帮助其更好地引导观众互动和转化。设置目标后，AI主播将根据目标调整话术和互动方式。请选择一个最重要的目标，AI主播将重点围绕该目标展开直播。
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="mb-6">
      <label class="block text-sm font-bold mb-2">输入直播目标</label>
      <a-input
        v-model="target"
        placeholder="请输入直播目标"
        :max-length="30"
        show-word-limit
        allow-clear
        class="w-full"
      />
    </div>

    <!-- 目标示例和建议 -->
    <div class="mb-6">
      <h3 class="text-sm font-bold mb-3">目标示例和建议</h3>

      <div v-for="(category, index) in targetSuggestions" :key="index" class="mb-4">
        <span class="text-sm text-[var(--color-text-3)]">{{ category.title }}：</span>
        <div class="flex flex-wrap gap-2 mt-2">
          <a-button
            v-for="(item, i) in category.items"
            :key="i"
            type="default"
            shape="round"
            size="mini"
            class="border-dashed border-[var(--color-danger-light-1)] bg-[var(--color-fill-0)] text-[var(--color-danger-light-4)] hover:bg-[var(--color-danger-light-1)] px-4 py-1 rounded-full text-xs"
            @click="setTarget(item)"
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
// Props
const props = defineProps({
  visible: Boolean,
  liveTarget: String
})

const emit = defineEmits(['update:visible', 'update:liveTarget'])

const target = ref(props.liveTarget || '')
// 当传入的liveTarget发生变化时，更新target的值
watch(
  () => props.liveTarget,
  newVal => {
    target.value = newVal || ''
  }
)

// 目标建议分类数据（结构化）
const targetSuggestions = [
  {
    title: '销售转化',
    items: [
      '引导用户在直播间购物链接下单成交',
      '引导用户领取优惠券，然后返回直播间购物链接下单',
      '引导用户访问品牌独立站下单成交'
    ]
  },
  {
    title: '引流转化',
    items: [
      '引导用户关注主播账号',
      '引导用户加入粉丝群',
      '引导用户查看Tiktok账号主页，浏览主页内容'
    ]
  },
  {
    title: '其他',
    items: ['引导用户赠送tiktok直播间礼物', '引导用户熟悉和掌握项目知识']
  }
]

// 设置目标
const setTarget = value => {
  target.value = value
}

// 取消
const handleCancel = () => {
  emit('update:visible', false)
}

// 确定
const handleOk = () => {
  emit('update:liveTarget', target.value)
  emit('update:visible', false)
}
</script>
