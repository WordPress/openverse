<template>
  <VIconButton
    :button-props="{ variant: 'plain' }"
    :icon-props="{ iconPath: closeIcon }"
    size="smaller"
    class="border-tx text-dark-charcoal-70"
    :aria-label="$t('browse-page.search-form.clear')"
    @click="$emit('click')"
  />
</template>

<script lang="ts">
import { defineComponent } from '@nuxtjs/composition-api'

import closeIcon from '~/assets/icons/close-small.svg'

export default defineComponent({
  name: 'VClearButton',
  setup() {
    return {
      closeIcon,
    }
  },
})
</script>
