<template>
  <span class="typewriter">
    <!-- 占位，保证宽度稳定 -->
    <span class="placeholder">{{ longestText }}</span>

    <!-- 动态文字 + 光标（光标随文字尾部移动） -->
    <span class="overlay">
      <span class="text" :class="textClass">{{ displayedText }}</span>
      <span v-if="showCaret" class="caret"></span>
    </span>
  </span>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  texts: { type: Array, required: true }, // 必传，多条字符串循环播放
  speed: { type: Number, default: 200 }, // 每字符打/删的间隔(ms)
  pause: { type: Number, default: 1000 }, // 打完/删完的停顿(ms)
  caretBlink: { type: Number, default: 500 }, // 光标闪烁间隔(ms)
  textClass: { type: String, default: '' }
})

const displayedText = ref('')
const showCaret = ref(true)
const currentIndex = ref(0) // texts 的当前索引

let charCount = 0 // 当前已显示字符数（0..len）
let forward = true // true = 打字(从左到右)，false = 删除(从右到左)
let typingTimer = null
let caretTimer = null

const currentText = computed(() =>
  props.texts && props.texts.length ? props.texts[currentIndex.value] : ''
)
const longestText = computed(() => {
  if (!props.texts || props.texts.length === 0) return ''
  return props.texts.reduce((a, b) => (a.length >= b.length ? a : b), '')
})

function clearTypingTimer() {
  if (typingTimer) {
    clearTimeout(typingTimer)
    typingTimer = null
  }
}

function tick() {
  const text = currentText.value || ''
  if (forward) {
    // 打字阶段：仍有字符要打
    if (charCount < text.length) {
      charCount += 1
      displayedText.value = text.slice(0, charCount)
      typingTimer = setTimeout(tick, props.speed)
    } else {
      // 完整打完：停顿后切换为删除
      typingTimer = setTimeout(() => {
        forward = false
        tick()
      }, props.pause)
    }
  } else {
    // 删除阶段
    if (charCount > 0) {
      charCount -= 1
      displayedText.value = text.slice(0, charCount)
      typingTimer = setTimeout(tick, props.speed)
    } else {
      // 删除完毕：停顿后切换到下一条并开始打印
      typingTimer = setTimeout(() => {
        currentIndex.value = (currentIndex.value + 1) % props.texts.length
        forward = true
        // 注意：charCount 保持为 0，这是关键！
        tick()
      }, props.pause)
    }
  }
}

function start() {
  clearTypingTimer()
  currentIndex.value = 0
  forward = true
  charCount = 0
  displayedText.value = ''
  tick()
}

onMounted(() => {
  start()
  caretTimer = setInterval(() => {
    showCaret.value = !showCaret.value
  }, props.caretBlink)
})

onBeforeUnmount(() => {
  clearTypingTimer()
  if (caretTimer) {
    clearInterval(caretTimer)
    caretTimer = null
  }
})

// 如果外部替换了 texts 数组（或 props 被替换），重置动画
watch(
  () => props.texts,
  () => {
    start()
  }
)
</script>

<style scoped>
.typewriter {
  position: relative;
  display: inline-block;
  line-height: 1;
}
/* 隐藏但占位，避免容器宽度塌掉 */
.placeholder {
  visibility: hidden;
  white-space: nowrap;
  line-height: 1;
}
/* 叠在占位上显示逐字文字 */
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  white-space: nowrap;
  line-height: 1;
}
/* 光标跟在文字里，删除时会随文字一起左移 */
.caret {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: currentColor;
  vertical-align: bottom;
  margin-left: 0.06em;
}
</style>
