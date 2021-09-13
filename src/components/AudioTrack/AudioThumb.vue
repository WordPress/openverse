<template>
  <!-- Should have a fixed width -->
  <div>
    <div class="h-0 w-full pt-full bg-yellow">&nbsp;</div>
  </div>
</template>

<script>
export default {
  name: 'AudioThumb',
  props: {
    audio: {
      type: Object,
      required: true,
    },
  },
}
</script>
