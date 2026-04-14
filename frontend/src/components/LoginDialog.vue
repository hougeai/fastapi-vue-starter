<template>
  <a-modal
    :visible="visible"
    @cancel="handleCancel"
    :footer="null"
    :closable="false"
    width="480px"
    class="rounded-2xl shadow-2xl"
    centered
  >
    <div class="flex flex-col items-center py-8 px-2">
      <div class="text-32px font-extrabold mb-3">欢迎回来</div>
      <div class="text-gray-500 text-18px mb-7">
        登录您的账号开始使用{{ getConfig('projectName') }}
      </div>
      <a-tabs v-model:active-key="activeTab" type="line" class="w-full">
        <!-- 手机登录 -->
        <a-tab-pane key="phone" title="手机登录">
          <a-form
            ref="phoneFormRef"
            :model="phoneForm"
            :rules="phoneRules"
            layout="vertical"
            @submit="handlePhoneLogin"
            class="mt-4"
          >
            <a-form-item field="phone" class="mb-6" hide-label>
              <a-input
                v-model="phoneForm.phone"
                placeholder="手机号"
                allow-clear
                size="large"
                class="h-12 text-18px"
              />
            </a-form-item>
            <a-form-item field="password" class="mb-6" hide-label>
              <a-input-password
                v-model="phoneForm.password"
                placeholder="密码"
                allow-clear
                size="large"
                class="h-12 text-18px"
              />
            </a-form-item>
            <a-form-item class="mb-0">
              <a-checkbox v-model="phoneForm.remember">记住我</a-checkbox>
            </a-form-item>
            <a-form-item>
              <a-button
                type="primary"
                html-type="submit"
                long
                :loading="loading"
                class="h-12 text-18px font-bold mt-2 rounded-lg"
              >
                登录
              </a-button>
            </a-form-item>
          </a-form>
          <div class="flex justify-between text-16px mt-4 px-2">
            <a @click="activeTab = 'register'" class="text-blue-500 cursor-pointer underline"
              >没有账号？免费注册</a
            >
            <a @click="activeTab = 'forgot'" class="text-blue-500 cursor-pointer underline"
              >忘记密码？点击找回</a
            >
          </div>
        </a-tab-pane>

        <!-- 注册 -->
        <a-tab-pane key="register" title="注册">
          <a-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            layout="vertical"
            @submit="handleRegister"
            class="mt-4"
          >
            <a-form-item field="phone" class="mb-6" hide-label>
              <a-input
                v-model="registerForm.phone"
                placeholder="手机号"
                allow-clear
                size="large"
                class="h-12 text-18px"
              >
                <template #suffix>
                  <a-button
                    type="text"
                    @click="handleSendCode"
                    :disabled="isCodeButtonDisabled"
                    class="text-primary"
                  >
                    {{ codeButtonText }}
                  </a-button>
                </template>
              </a-input>
            </a-form-item>
            <a-form-item field="verificationCode" class="mb-6" hide-label>
              <a-input
                v-model="registerForm.verificationCode"
                placeholder="验证码"
                allow-clear
                size="large"
                class="h-12 text-18px"
              />
            </a-form-item>
            <a-form-item field="password" class="mb-6" hide-label>
              <a-input-password
                v-model="registerForm.password"
                placeholder="密码"
                allow-clear
                size="large"
                class="h-12 text-18px"
              />
            </a-form-item>
            <a-form-item field="confirmPassword" class="mb-6" hide-label>
              <a-input-password
                v-model="registerForm.confirmPassword"
                placeholder="确认密码"
                allow-clear
                size="large"
                class="h-12 text-18px"
              />
            </a-form-item>
            <a-form-item>
              <a-button
                type="primary"
                html-type="submit"
                long
                :loading="loading"
                class="h-12 text-18px font-bold mt-2 rounded-lg"
              >
                注册
              </a-button>
            </a-form-item>
          </a-form>
          <div class="flex justify-between text-16px mt-4 px-2">
            <a @click="activeTab = 'phone'" class="text-blue-500 cursor-pointer underline"
              >已有账号？去登录</a
            >
          </div>
        </a-tab-pane>

        <!-- 找回密码 -->
        <a-tab-pane key="forgot" title="找回密码">
          <a-form
            ref="forgotFormRef"
            :model="forgotForm"
            :rules="forgotRules"
            layout="vertical"
            @submit="handleForgotPassword"
            class="mt-4"
          >
            <a-form-item field="phone" class="mb-6" hide-label>
              <a-input
                v-model="forgotForm.phone"
                placeholder="手机号"
                allow-clear
                size="large"
                class="h-12 text-18px"
              />
            </a-form-item>
            <a-form-item>
              <a-button
                type="primary"
                html-type="submit"
                long
                :loading="loading"
                class="h-12 text-18px font-bold mt-2 rounded-lg"
              >
                发送重置链接
              </a-button>
            </a-form-item>
          </a-form>
          <div class="flex justify-between text-16px mt-4 px-2">
            <a @click="activeTab = 'email'" class="text-blue-500 cursor-pointer underline"
              >已有账号？去登录</a
            >
          </div>
        </a-tab-pane>
      </a-tabs>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/api'
import { setToken } from '@/utils'
import { getConfig } from '@/config'

// 父组件的 showLoginDialog 传递给子组件的 visible
const props = defineProps({
  visible: Boolean
})
// 通过 update:visible 事件来更新父组件的 showLoginDialog 值
const emit = defineEmits(['update:visible', 'cancel'])

const userStore = useUserStore()
const { query } = useRoute()
const router = useRouter()

const loading = ref(false)
const activeTab = ref('phone')

// 验证码相关状态
const isCodeButtonDisabled = ref(false)
const codeButtonText = ref('发送验证码')
let countdownTimer = null

const phoneForm = ref({
  phone: '',
  password: '',
  remember: false
})

const registerForm = ref({
  phone: '',
  password: '',
  confirmPassword: '',
  verificationCode: ''
})

const forgotForm = ref({
  phone: ''
})

// 表单 ref
const phoneFormRef = ref()
const registerFormRef = ref()
const forgotFormRef = ref()

// 统一的 rules（使用 async-validator 规则格式）
const phoneRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { match: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    {
      match: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/,
      message: '密码至少 8 位且需包含字母和数字',
      trigger: ['blur', 'change']
    },
    {
      validator: (value, cb) => {
        if (/\s/.test(value)) return cb('密码不能包含空格')
        cb()
      },
      trigger: ['blur', 'change']
    }
  ]
}

const registerRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { match: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: ['blur', 'change'] }
  ],
  verificationCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { match: /^\d{6}$/, message: '请输入 6 位数字验证码', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    {
      match: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/,
      message: '密码至少8个字符，包含字母和数字',
      trigger: ['blur', 'change']
    }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (value, cb) => {
        if (value !== registerForm.value.password) {
          cb('两次输入的密码不一致')
        } else {
          cb()
        }
      },
      trigger: ['blur', 'change']
    }
  ]
}

const forgotRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱', trigger: ['blur', 'change'] },
    {
      validator: (value, cb) => {
        if (value && value.length > 100) return cb('邮箱长度不能超过 100 个字符')
        if (/\s/.test(value)) return cb('邮箱不能包含空格')
        cb()
      },
      trigger: ['blur', 'change']
    }
  ]
}

watch(
  () => props.visible,
  val => {
    if (val) {
      activeTab.value = 'phone'
      phoneForm.value = { phone: '', password: '', remember: false }
      registerForm.value = {
        phone: '',
        password: '',
        confirmPassword: '',
        verificationCode: ''
      }
    }
  }
)

const handlePhoneLogin = async () => {
  const errors = await phoneFormRef.value.validate()
  if (errors) return
  loading.value = true
  try {
    const res = await api.phoneLogin({
      phone: phoneForm.value.phone,
      password: phoneForm.value.password.toString(),
      remember: phoneForm.value.remember
    })
    await handleLoginSuccess(res)
    AMessage.success('登录成功')
    emit('update:visible', false)
  } catch (e) {
    AMessage.error(e?.message || '登录失败')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  const errors = await registerFormRef.value.validate()
  if (errors) return
  loading.value = true
  try {
    const data = {
      phone: registerForm.value.phone.trim(),
      password: registerForm.value.password,
      verification_code: registerForm.value.verificationCode
    }
    if (query.i) {
      data.inviter_id = query.i
    }
    await api.phoneRegister(data)
    AMessage.success('注册成功，请登录')
    activeTab.value = 'phone'
    phoneForm.value.phone = registerForm.value.phone
    phoneForm.value.password = ''
  } catch (e) {
    AMessage.error(e?.message || '注册失败')
  } finally {
    loading.value = false
  }
}

const handleLoginSuccess = async res => {
  setToken(res.data.access_token) // 请求成功就要设置token
  const userInfoResult = await userStore.getUserInfo()
  if (!userInfoResult.success) {
    AMessage.error(userInfoResult.error || '获取用户信息失败')
    return
  }
  if (query.redirect) {
    const path = query.redirect
    Reflect.deleteProperty(query, 'redirect')
    router.push({ path, query })
  } else {
    router.push('/home')
  }
}

const handleForgotPassword = async () => {
  const errors = await forgotFormRef.value.validate()
  if (errors) return
  loading.value = true
  try {
    await api.forgotPassword({ email: forgotForm.value.phone })
    AMessage.success('重置链接已发送到您的邮箱，请注意查收')
    activeTab.value = 'phone'
  } catch (e) {
    AMessage.error(e?.message || '发送失败')
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  emit('update:visible', false)
  emit('cancel')
}

// 发送验证码函数
const handleSendCode = async () => {
  const errors = await registerFormRef.value.validateField('email')
  if (errors) return
  try {
    startCountdown()
    await api.sendVerifyCode({ email: registerForm.value.email })
    AMessage.success('验证码已发送')
  } catch (e) {
    AMessage.error(e?.message || '发送验证码失败')
    resetCodeButton()
  }
}

// 验证码倒计时功能
const startCountdown = () => {
  let count = 60
  isCodeButtonDisabled.value = true
  codeButtonText.value = `${count}秒后重发`

  countdownTimer = setInterval(() => {
    count--
    if (count > 0) {
      codeButtonText.value = `${count}秒后重发`
    } else {
      resetCodeButton()
    }
  }, 1000)
}

// 重置验证码按钮
const resetCodeButton = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  isCodeButtonDisabled.value = false
  codeButtonText.value = '发送验证码'
}
</script>
