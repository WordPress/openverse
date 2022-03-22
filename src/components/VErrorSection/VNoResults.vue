<template>
  <div class="no-results text-center md:text-left">
    <h5 class="text-5xl">
      {{ $t('no-results.heading', { query: query.q }) }}
    </h5>
    <h6 class="text-3xl font-normal md:font-bold mt-10 md:mt-16">
      {{ $t('no-results.alternatives') }}
    </h6>
    <VMetaSourceList class="mt-4 md:mt-6" :type="type" :query="query" />
  </div>
</template>

<script>
import { isValidSearchType } from '~/utils/prop-validators'

import VMetaSourceList from '~/components/VMetaSearch/VMetaSourceList.vue'

export default {
  name: 'VNoResults',
  components: { VMetaSourceList },
  props: {
    type: {
      type: String,
      validator: isValidSearchType,
    },
    query: {
      type: Object,
    },
  },
}
</script>
