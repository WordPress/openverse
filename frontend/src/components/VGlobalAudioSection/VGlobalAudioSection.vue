<template>
  <div
    class="global-audio sticky z-global-audio sm:hidden"
    :class="{ 'bottom-2 mx-2': !!audio }"
  >
    <template v-if="audio">
      <VGlobalAudioTrack :audio="audio" />
      <VIconButton
        class="!absolute end-0 top-0 z-30 m-2"
        variant="transparent-gray"
        :icon-props="{ name: 'close-small' }"
        size="small"
        :label="$t('audioTrack.close')"
        @click="handleClose"
      />
    </template>
  </div>
</template>

<script lang="ts">
import { useRoute } from "#imports"

import { watch, computed, defineComponent } from "vue"

import { AUDIO } from "~/constants/media"
import { useActiveAudio } from "~/composables/use-active-audio"

import { useActiveMediaStore } from "~/stores/active-media"
import { useMediaStore } from "~/stores/media"
import { useSingleResultStore } from "~/stores/media/single-result"
import { useUiStore } from "~/stores/ui"

import type { AudioDetail } from "~/types/media"

import VIconButton from "~/components/VIconButton/VIconButton.vue"
import VGlobalAudioTrack from "~/components/VAudioTrack/VGlobalAudioTrack.vue"

export default defineComponent({
  name: "VGlobalAudioSection",
  components: {
    VIconButton,
    VGlobalAudioTrack,
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
      if (singleResultStore.mediaId === trackId) {
        return singleResultStore.audio
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
      if (!error) {
        return
      }
      let errorMsg
      switch (error.code) {
        case error.MEDIA_ERR_ABORTED: {
          errorMsg = "err_aborted"
          break
        }
        case error.MEDIA_ERR_NETWORK: {
          errorMsg = "err_network"
          break
        }
        case error.MEDIA_ERR_DECODE: {
          errorMsg = "err_decode"
          break
        }
        case error.MEDIA_ERR_SRC_NOT_SUPPORTED: {
          errorMsg = "err_unsupported"
          break
        }
        default: {
          errorMsg = "err_unknown"
        }
      }
      activeMediaStore.setMessage({ message: errorMsg })
    }

    watch(
      activeAudio.obj,
      (audio, _, onInvalidate) => {
        if (!audio) {
          return
        }
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
    const routeValue = computed(() => route)
    watch(routeValue, (newRouteVal, oldRouteVal) => {
      const oldName = oldRouteVal.name ? String(oldRouteVal.name) : ""
      const newName = newRouteVal.name ? String(newRouteVal.name) : ""
      if (
        (oldName.includes("audio") && !newName.includes("audio")) ||
        (uiStore.isDesktopLayout &&
          newName.includes("audio-id") &&
          newRouteVal.params.id != activeMediaStore.id)
      ) {
        activeAudio.obj.value?.pause()
        activeMediaStore.ejectActiveMediaItem()
      }
    })

    return {
      audio,

      handleClose,
    }
  },
})
</script>
