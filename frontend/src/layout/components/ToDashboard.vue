<template>
  <a-button type="text" @click="$router.push('/home')" class="dashboard-button">
    <div class="flex items-center">
      <icon-material-symbols-dashboard class="text-[var(--color-text-1)] text-16px" />
      <span class="ml-1">控制台</span>
    </div>
  </a-button>
</template>

<style scoped>
.dashboard-button {
  @apply px-2 py-1 h-auto flex items-center text-16px font-700 text-shadow-sm cursor-pointer;
  @apply border border-solid rounded-lg;
  @apply border-[var(--color-border-2)] bg-transparent;
  @apply transition-all duration-200 ease-in-out;
  @apply hover:border-[var(--color-primary-light-4)] hover:bg-[var(--color-primary-light-1)];
  @apply hover:text-[var(--color-primary-6)] hover:shadow-sm;
}

.dashboard-button:active {
  @apply transform scale-95;
}
</style>
