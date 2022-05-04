<template>
  <aside>
    <h3 class="text-2xl md:text-3xl mb-6">
      {{ $t('image-details.related-images') }}
    </h3>
    <VImageGrid
      :images="media"
      :show-load-more="false"
      :fetch-state="fetchState"
    />
  </aside>
</template>

<script>
import VImageGrid from '~/components/VImageGrid/VImageGrid.vue'

export default {
  name: 'VRelatedImages',
  components: { VImageGrid },
  props: {
    media: {
      type: Array,
      required: true,
    },
    fetchState: {
      type: Object,
      required: true,
    },
  },
}
</script>
