<template>
  <div class="no-results text-center md:text-left">
    <h5 class="text-5xl break-words">
      {{ $t('no-results.heading', { query: query.q }) }}
    </h5>
    <h6 class="text-3xl font-normal md:font-bold mt-10 md:mt-16">
      {{ $t('no-results.alternatives') }}
    </h6>
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
