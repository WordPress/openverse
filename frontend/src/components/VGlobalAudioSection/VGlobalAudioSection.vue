<template>
  <div class="global-audio sticky bottom-0 z-global-audio sm:hidden">
    <VGlobalAudioTrack v-if="audio" :audio="audio" />
    <VIconButton
      v-if="audio"
      class="absolute top-0 z-10 border-none ltr:right-0 rtl:left-0"
      size="large"
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
} from "@nuxtjs/composition-api"

import { AUDIO } from "~/constants/media"
import { useActiveAudio } from "~/composables/use-active-audio"

import { useActiveMediaStore } from "~/stores/active-media"
import { useMediaStore } from "~/stores/media"
import { useSingleResultStore } from "~/stores/media/single-result"
import { useUiStore } from "~/stores/ui"

import type { AudioDetail } from "~/types/media"

import VIconButton from "~/components/VIconButton/VIconButton.vue"
import VGlobalAudioTrack from "~/components/VAudioTrack/VGlobalAudioTrack.vue"

import closeIcon from "~/assets/icons/close-small.svg"

export default defineComponent({
  name: "VGlobalAudioSection",
  components: {
    VGlobalAudioTrack,
    VIconButton,
  },
  setup() {
    const route = useRoute()

    const activeMediaStore = useActiveMediaStore()
    const mediaStore = useMediaStore()
    const uiStore = useUiStore()

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
        activeMediaStore.setMessage({ message: "err_unknown" })
        return
      }
      const error = event.target.error
      if (!error) return
      let errorMsg
      switch (error.code) {
        case error.MEDIA_ERR_ABORTED:
          errorMsg = "err_aborted"
          break
        case error.MEDIA_ERR_NETWORK:
          errorMsg = "err_network"
          break
        case error.MEDIA_ERR_DECODE:
          errorMsg = "err_decode"
          break
        case error.MEDIA_ERR_SRC_NOT_SUPPORTED:
          errorMsg = "err_unsupported"
          break
        default:
          errorMsg = "err_unknown"
      }
      activeMediaStore.setMessage({ message: errorMsg })
    }

    watch(
      activeAudio.obj,
      (audio, _, onInvalidate) => {
        if (!audio) return
        audio.addEventListener("error", handleError)

        onInvalidate(() => {
          audio.removeEventListener("error", handleError)
        })
      },
      { immediate: true }
    )

    const handleClose = () => {
      activeAudio.obj.value?.pause()
      activeAudio.obj.value = undefined
      activeMediaStore.ejectActiveMediaItem()
    }

    /**
     * Router observation
     *
     * The player will continue only within 'search-audio' and 'audio-id' routes,
     * and on desktop, only if the next route is the 'audio-id' page of the
     * track currently playing, or the original search result page.
     */
    const routeValue = computed(() => route.value)
    watch(routeValue, (newRouteVal, oldRouteVal) => {
      if (
        (oldRouteVal.name?.includes("audio") &&
          !newRouteVal.name?.includes("audio")) ||
        (uiStore.isDesktopLayout &&
          newRouteVal.name?.includes("audio-id") &&
          newRouteVal.params.id != activeMediaStore.id)
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
