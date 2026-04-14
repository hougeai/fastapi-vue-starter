import { getConfig } from '@/config/index'

export const useSystemStore = defineStore(
  'system',
  () => {
    // 模式列表
    const modeList = shallowRef([
      {
        name: 'light',
        title: '亮色模式'
      },
      {
        name: 'dark',
        title: '暗色模式'
      }
    ])
    // 当前模式
    const currentMode = shallowRef(null)
    const mode = useColorMode({
      attribute: 'arco-theme',
      emitAuto: true,
      selector: 'body',
      initialValue: currentMode.value?.name,
      storageKey: null
    })
    watchEffect(() => (mode.value = currentMode.value?.name))

    // 初始化模式
    const initMode = () => {
      if (!currentMode.value) {
        currentMode.value = modeList.value[0]
      } else {
        currentMode.value =
          modeList.value.find(item => item.name === currentMode.value.name) || modeList.value[0]
      }
    }

    return {
      currentMode,
      modeList,
      initMode
    }
  },
  {
    persist: {
      key: `${getConfig('appCode')}-system`,
      enabled: true,
      storage: window.localStorage, // 默认就是 localStorage
      pick: ['currentMode.name']
    }
  }
)
