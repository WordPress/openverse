<template>
  <VAudioTrack
    :audio="audio"
    layout="box"
    size="full"
    @boxedAudioClick="navigateToSinglePage"
  />
</template>

<script>
import { useContext, useRouter } from '@nuxtjs/composition-api'
import { defineComponent } from '@vue/composition-api'
import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'

export default defineComponent({
  components: { VAudioTrack },
  props: ['audio'],
  setup() {
    const { app } = useContext()
    const router = useRouter()
    const navigateToSinglePage = (audio) => {
      router.push(app.localePath({ path: `/audio/${audio.id}` }))
    }

    return {
      navigateToSinglePage,
    }
  },
})
</script>
