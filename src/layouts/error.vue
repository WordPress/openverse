<template>
  <VFourOhFour :error="error" />
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'

import VFourOhFour from '~/components/VFourOhFour.vue'

export default defineComponent({
  name: 'ErrorPage',
  components: { VFourOhFour },
  layout: 'blank',
  props: ['error'],
})
</script>
