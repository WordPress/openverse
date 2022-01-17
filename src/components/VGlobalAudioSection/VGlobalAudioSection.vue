<template>
  <div class="global-audio sticky sm:hidden bottom-0">
    <VAudioTrack v-if="audio" layout="global" :audio="audio" />

    <!-- eslint-disable vuejs-accessibility/media-has-caption -->
    <audio
      v-show="false"
      ref="audioEl"
      class="audio-controller"
      controls
      crossorigin="anonymous"
      @error="handleError"
    />
    <!-- eslint-enable vuejs-accessibility/media-has-caption -->

    <VIconButton
      v-if="audio"
      class="absolute top-0 end-0 border-none z-10"
      :icon-props="{ iconPath: icons.closeIcon }"
      @click="handleClose"
    />
  </div>
</template>

<script>
import {
  useStore,
  useRoute,
  ref,
  watch,
  onMounted,
  computed,
  onBeforeUnmount,
} from '@nuxtjs/composition-api'

import { ACTIVE } from '~/constants/store-modules'
import {
  SET_MESSAGE,
  EJECT_ACTIVE_MEDIA_ITEM,
} from '~/constants/mutation-types'

import closeIcon from '~/assets/icons/close-small.svg'

export default {
  name: 'VGlobalAudioSection',
  setup() {
    const store = useStore()
    const route = useRoute()

    /* Audio element */

    const audioEl = ref(null)
    onMounted(() => {
      window.audioEl = audioEl.value
    })
    onBeforeUnmount(() => {
      delete window.audioEl
    })

    /* Active audio track */

    const audio = computed(() => {
      const trackId = store.state.active.id
      if (trackId) {
        return store.state.media.results.audio.items[trackId]
      }
      return null
    })

    /* Message */

    const handleError = (event) => {
      const error = event.target.error
      let errorMsg
      switch (error.code) {
        case error.MEDIA_ERR_ABORTED:
          errorMsg = 'err_aborted'
          break
        case error.MEDIA_ERR_NETWORK:
          errorMsg = 'err_network'
          break
        case error.MEDIA_ERR_DECODE:
          errorMsg = 'err_decode'
          break
        case error.MEDIA_ERR_SRC_NOT_SUPPORTED:
          errorMsg = 'err_unsupported'
          break
      }
      store.commit(`${ACTIVE}/${SET_MESSAGE}`, {
        message: errorMsg,
      })
    }

    const handleClose = () => {
      store.commit(`${ACTIVE}/${EJECT_ACTIVE_MEDIA_ITEM}`)
    }

    /* Router observation */

    const routeName = computed(() => route.value.name)
    watch(routeName, (routeNameVal, oldRouteNameVal) => {
      if (
        oldRouteNameVal.includes('audio') &&
        !routeNameVal.includes('audio')
      ) {
        audioEl.value.pause()
        store.commit(`${ACTIVE}/${EJECT_ACTIVE_MEDIA_ITEM}`)
      }
    })

    return {
      icons: {
        closeIcon,
      },

      audioEl,

      audio,

      handleError,
      handleClose,
    }
  },
}
</script>
