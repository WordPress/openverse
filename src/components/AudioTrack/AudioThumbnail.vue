<template>
  <!-- Should be wrapped by a fixed-width parent -->
  <div class="h-0 w-full pt-full bg-yellow">&nbsp;</div>
</template>

<script>
export default {
  name: 'AudioThumbnail',
  props: {
    audio: {
      type: Object,
      required: true,
    },
  },
}
</script>
