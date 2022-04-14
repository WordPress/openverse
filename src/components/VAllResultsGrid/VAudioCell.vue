<template>
  <VAudioTrack :audio="audio" layout="box" />
</template>

<script>
import { defineComponent } from '@vue/composition-api'

import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'

export default defineComponent({
  components: { VAudioTrack },
  props: ['audio'],
})
</script>
