<template>
  <div
    class="font-heading font-semibold text-base text-center leading-tight bg-yellow text-dark-blue py-6"
  >
    <!-- @slot Content goes here -->
    <slot />
  </div>
</template>

<script>
/**
 * Displays notices is a yellow strip. The onus of positioning this bar is on
 * the parent component.
 */
export default {
  name: 'VNoticeBar',
}
</script>
