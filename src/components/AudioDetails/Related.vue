<template>
  <aside :aria-label="$t('photo-details.aria.related')">
    <h4 class="b-header">
      {{ $t('audio-details.related-audios') }}
    </h4>
    <ClientOnly>
      <AudioTrack
        v-for="rAudio in relatedAudios"
        :key="rAudio.id"
        :audio="rAudio"
        :is-compact="true"
      />
    </ClientOnly>
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
