<template>
  <!-- Should be wrapped by a fixed-width parent -->
  <div :class="{ 'h-0 w-full bg-yellow': true, 'pt-full': !audio.thumbnail }">
    <img
      v-if="audio.thumbnail"
      :src="audio.thumbnail"
      :alt="audio.title"
      width="110"
      height="110"
    />
  </div>
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
