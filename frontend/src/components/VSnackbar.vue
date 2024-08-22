<script setup lang="ts">
withDefaults(
  defineProps<{
    size?: "small" | "large"
    isVisible?: boolean
  }>(),
  {
    size: "small",
    isVisible: true,
  }
)
</script>

<template>
  <div
    :role="isVisible ? 'alert' : undefined"
    class="snackbar fixed bottom-4 z-snackbar rounded-sm bg-black text-over-dark transition-[opacity,transform] duration-500 motion-reduce:transition-opacity ltr:left-4 rtl:right-4"
    :class="[
      size === 'large'
        ? 'w-max max-w-[calc(100%_-_2_*_theme(spacing.4))] flex-row items-center px-6 py-4 text-sm'
        : 'w-2/3 flex-col items-start px-4 py-3 text-sr sm:w-2/5',
      isVisible
        ? 'translate-y-0 opacity-100'
        : 'translate-y-[4rem] opacity-0 motion-reduce:translate-y-0',
    ]"
  >
    <!-- @slot Your message or subcomponent goes passed here. -->
    <slot />
  </div>
</template>

<style scoped>
.snackbar {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}
</style>
