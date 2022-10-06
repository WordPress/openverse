<template>
  <VButton
    variant="primary"
    class="h-12 py-4 text-sm font-semibold ms-auto"
    @click="$emit('click')"
  >
    <span v-if="!isFetching">{{ $t('header.see-results') }}</span>
    <!-- TODO: add animation instead of 'Loading' text -->
    <span v-else>{{ $t('header.loading') }}</span>
  </VButton>
</template>
<script lang="ts">
import { defineComponent } from '@nuxtjs/composition-api'

import VButton from '~/components/VButton.vue'

export default defineComponent({
  name: 'VShowResultsButton',
  components: { VButton },
  props: {
    isFetching: {
      type: Boolean,
      default: false,
    },
  },
})
</script>
