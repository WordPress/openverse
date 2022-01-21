<template>
  <NuxtLink
    :to="localePath(`/audio/${audio.id}`)"
    class="block focus:bg-white focus:border-tx focus:ring focus:ring-pink focus:outline-none focus:shadow-ring rounded-sm"
    @click.native="navigateToSinglePage(audio)"
  >
    <VAudioTrack :audio="audio" layout="box" size="full" />
  </NuxtLink>
</template>

<script>
import { useContext, useRouter } from '@nuxtjs/composition-api'
import { defineComponent } from '@vue/composition-api'
import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'

export default defineComponent({
  components: { VAudioTrack },
  props: ['audio'],
  setup() {
    const { i18n } = useContext()
    const router = useRouter()
    const navigateToSinglePage = (audio) => (/** @type MouseEvent */ event) => {
      if (!event.metaKey && !event.ctrlKey) {
        event.preventDefault()
        const detailRoute = i18n.localeRoute({
          name: 'AudioDetailPage',
          params: { id: audio.id, location: window.scrollY },
        })
        router.push(detailRoute)
      }
    }

    return {
      navigateToSinglePage,
    }
  },
})
</script>
