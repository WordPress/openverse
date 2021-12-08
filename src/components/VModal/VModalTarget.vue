<template>
  <VTeleportTarget name="modal" />
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'
import { VTeleportTarget } from '~/components/VTeleport'

export default defineComponent({
  name: 'VModalTarget',
  components: { VTeleportTarget },
})
</script>
