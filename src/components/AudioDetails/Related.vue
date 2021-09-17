<template>
  <aside :aria-label="$t('photo-details.aria.related')">
    <h4 class="b-header mb-6">
      {{ $t('audio-details.related-audios') }}
    </h4>
    <AudioTrack
      v-for="audio in relatedAudios"
      :key="audio.id"
      :audio="audio"
      :is-compact="true"
      class="mb-12"
    />
  </aside>
</template>

<script>
export default {
  name: 'RelatedAudios',
  props: {
    relatedAudios: {},
  },
}
</script>
