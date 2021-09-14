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
 * Displays notices is a yellow strip. It on
 */
export default {
  name: 'NoticeBar',
}
</script>
