<script setup>
defineProps({
  showDashboard: {
    type: Boolean,
    default: true
  }
})
</script>

<template>
  <div class="w-full h-full flex px-20px box-border">
    <div class="h-full flex">
      <slot name="left">
        <Logo />
      </slot>
    </div>
    <div class="h-full flex-1 flex justify-center items-center ml-30">
      <slot name="center">
        <Docs />
        <Software />
      </slot>
    </div>
    <div class="h-full flex flex-shrink-0 items-center">
      <div class="flex items-center space-x-1">
        <slot name="right">
          <ToDashboard v-if="showDashboard" />
          <Notification />
          <SwitchMode />
          <WeChat />
          <GitHub />
          <Profile />
        </slot>
      </div>
    </div>
  </div>
</template>
