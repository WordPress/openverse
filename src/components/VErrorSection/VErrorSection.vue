<template>
  <div class="error-section mx-auto flex max-w-screen-xl flex-row items-center">
    <div class="image-pane hidden max-w-[432px] flex-grow md:block">
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
