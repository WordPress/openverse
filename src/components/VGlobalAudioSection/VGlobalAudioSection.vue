<template>
  <div class="global-audio sticky sm:hidden bottom-0">
    <VGlobalAudioTrack v-if="audio" layout="global" :audio="audio" />
    <VIconButton
      v-if="audio"
      class="absolute top-0 rtl:left-0 ltr:right-0 border-none z-10"
      :icon-props="{ iconPath: icons.closeIcon }"
      @click="handleClose"
    />
  </div>
</template>

<script lang="ts">
import {
  useRoute,
  watch,
  computed,
  defineComponent,
} from '@nuxtjs/composition-api'

import { AUDIO } from '~/constants/media'
import { useActiveAudio } from '~/composables/use-active-audio'
import { useActiveMediaStore } from '~/stores/active-media'
import { useMediaStore } from '~/stores/media'
import { useSingleResultStore } from '~/stores/media/single-result'

import type { AudioDetail } from '~/models/media'

import VIconButton from '~/components/VIconButton/VIconButton.vue'
import VGlobalAudioTrack from '~/components/VAudioTrack/VGlobalAudioTrack.vue'

import closeIcon from '~/assets/icons/close-small.svg'

export default defineComponent({
  name: 'VGlobalAudioSection',
  components: {
    VGlobalAudioTrack,
    VIconButton,
  },
  setup() {
    const activeMediaStore = useActiveMediaStore()
    const mediaStore = useMediaStore()
    const route = useRoute()

    const activeAudio = useActiveAudio()

    /* Active audio track */
    const getAudioItemById = (trackId: string): AudioDetail | null => {
      const audioFromMediaStore = mediaStore.getItemById(AUDIO, trackId)
      if (audioFromMediaStore) {
        return audioFromMediaStore as AudioDetail
      }
      const singleResultStore = useSingleResultStore()
      if (singleResultStore.mediaItem?.id === trackId) {
        return singleResultStore.mediaItem as AudioDetail
      }
      return null
    }
    const audio = computed(() => {
      const trackId = activeMediaStore.id
      if (trackId) {
        return getAudioItemById(trackId)
      }
      return null
    })

    /* Message */

    const handleError = (event: Event) => {
      if (!(event.target instanceof HTMLAudioElement)) {
        activeMediaStore.setMessage({ message: 'err_unknown' })
        return
      }
      const error = event.target.error
      if (!error) return
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
        default:
          errorMsg = 'err_unknown'
      }
      activeMediaStore.setMessage({ message: errorMsg })
    }

    watch(
      activeAudio.obj,
      (audio, _, onInvalidate) => {
        if (!audio) return
        audio.addEventListener('error', handleError)

        onInvalidate(() => {
          audio.removeEventListener('error', handleError)
        })
      },
      { immediate: true }
    )

    const handleClose = () => {
      activeAudio.obj.value?.pause()
      activeAudio.obj.value = undefined
      activeMediaStore.ejectActiveMediaItem()
    }

    /* Router observation */

    const routeName = computed(() => route.value.name)
    watch(routeName, (routeNameVal, oldRouteNameVal) => {
      if (
        oldRouteNameVal?.includes('audio') &&
        !routeNameVal?.includes('audio')
      ) {
        activeAudio.obj.value?.pause()
        activeMediaStore.ejectActiveMediaItem()
      }
    })

    return {
      icons: {
        closeIcon,
      },

      audio,

      handleError,
      handleClose,
    }
  },
})
</script>
