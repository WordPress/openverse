<template>
  <div class="error-section flex flex-row items-center max-w-screen-xl mx-auto">
    <div class="image-pane hidden md:block flex-grow max-w-[432px]">
      <!-- @slot Error image goes here -->
      <slot name="image" />
    </div>
    <div class="flex-grow p-4 md:p-20">
      <!-- @slot Main content goes here -->
      <slot />
    </div>
  </div>
</template>

<script>
/**
 * This component sets the layout for showing error messages.
 */
export default {
  name: 'VErrorSection',
}
</script>
