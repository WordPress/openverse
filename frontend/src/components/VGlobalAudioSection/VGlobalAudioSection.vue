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
        :label="t('audioTrack.close')"
        @click="handleClose"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { useNuxtApp, useRoute } from "#imports"

import { watch, computed } from "vue"

import { useActiveAudio } from "~/composables/use-active-audio"

import { useActiveMediaStore } from "~/stores/active-media"
import { useUiStore } from "~/stores/ui"

import VIconButton from "~/components/VIconButton/VIconButton.vue"
import VGlobalAudioTrack from "~/components/VAudioTrack/VGlobalAudioTrack.vue"

import type { RouteRecordName } from "vue-router"

const {
  $i18n: { t },
} = useNuxtApp()

const route = useRoute()

const activeMediaStore = useActiveMediaStore()
const uiStore = useUiStore()

const activeAudio = useActiveAudio()

const audio = computed(() => activeMediaStore.detail)

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

const getRouteId = (routeName: RouteRecordName | null | undefined) => {
  return String(routeName).split("__")[0]
}

/**
 * Router observation
 *
 * When navigating to pages other than search or single audio detail,
 * close the global audio player.
 *
 *
 * The player will continue only within 'search-audio' and 'audio-id' routes,
 * and on desktop, only if the next route is the 'audio-id' page of the
 * track currently playing, or the original search result page.
 */
const routeId = computed(() => getRouteId(route?.name))
watch(routeId, (newRouteId) => {
  if (!["search", "search-audio", "audio-id"].includes(newRouteId)) {
    ejectAndClose()
  }
})

const ejectAndClose = () => {
  activeAudio.obj.value?.pause()
  activeMediaStore.ejectActiveMediaItem()
}

/**
 * Stop the global audio when the global audio player is hidden on screens
 * above sm.
 */
const isSm = computed(() => uiStore.isBreakpoint("sm"))
watch(isSm, (aboveSm) => {
  if (aboveSm) {
    ejectAndClose()
  }
})
</script>
