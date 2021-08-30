<template>
  <aside
    :aria-label="$t('photo-details.aria.related')"
    class="p-4 my-6 photo_related-images"
  >
    <h3 class="b-header">
      {{ $t('audio-details.related-audios') }}
    </h3>
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
  props: [
    'relatedAudios',
    'audiosCount',
    'query',
    'filter',
    'isPrimaryImageLoaded',
  ],
}
</script>
