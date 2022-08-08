<template>
  <div class="no-results text-center md:text-left">
    <h1 class="break-words text-4xl md:text-6xl">
      {{ $t('no-results.heading', { query: query.q }) }}
    </h1>
    <h2
      class="mt-10 text-base font-normal md:mt-16 md:text-3xl md:font-semibold"
    >
      {{ $t('no-results.alternatives') }}
    </h2>
    <VMetaSourceList class="mt-4 md:mt-6" :type="type" :query="query" />
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from '@nuxtjs/composition-api'

import type { MediaType } from '~/constants/media'
import type { ApiQueryParams } from '~/utils/search-query-transform'

import VMetaSourceList from '~/components/VMetaSearch/VMetaSourceList.vue'

export default defineComponent({
  name: 'VNoResults',
  components: { VMetaSourceList },
  props: {
    type: {
      type: String as PropType<MediaType>,
    },
    query: {
      type: Object as PropType<ApiQueryParams>,
    },
  },
})
</script>
