<template>
  <li>
    <VAudioTrack
      :audio="audio"
      :layout="layout"
      :size="size"
      :search-term="searchTerm"
      v-bind="$attrs"
      @interacted="sendInteractionEvent"
      @keydown.enter="handleEnter(audio)"
      @mousedown="handleMousedown(audio, $event)"
    />
  </li>
</template>

<script setup lang="ts">
import { useRoute } from "#imports"

import { toRefs } from "vue"

import { useAnalytics } from "~/composables/use-analytics"
import { useAudioSnackbar } from "~/composables/use-audio-snackbar"
import { useSensitiveMedia } from "~/composables/use-sensitive-media"
import { AUDIO } from "~/constants/media"

import type { AudioInteractionData } from "~/types/analytics"
import type { AudioLayout, AudioSize } from "~/constants/audio"
import type { AudioTrackClickEvent } from "~/types/events"
import type { AudioDetail } from "~/types/media"
import type { ResultKind } from "~/types/result"

import { useSearchStore } from "~/stores/search"
import { useSingleResultStore } from "~/stores/media/single-result"
import { isResultsRoute, isSearchRoute } from "~/utils/route"

import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"

defineOptions({
  inheritAttrs: false,
})

const props = withDefaults(
  defineProps<{
    layout: AudioLayout
    size?: AudioSize
    audio: AudioDetail
    searchTerm: string
    kind?: ResultKind
  }>(),
  {
    kind: "search",
  }
)
const { sendCustomEvent } = useAnalytics()

const { audio } = toRefs(props)
const { isHidden: shouldBlur } = useSensitiveMedia(audio)

const handleMousedown = (
  audio: AudioDetail,
  { inWaveform }: AudioTrackClickEvent
) => {
  // Only send the event when the click navigates to the single result page.
  // If the click is in waveform or audio-control button, it controls the audio player.
  if (inWaveform) {
    return
  }
  handleClick(audio)
}
const handleEnter = (audio: AudioDetail) => {
  handleClick(audio)
}
const singleResultStore = useSingleResultStore()
const searchStore = useSearchStore()
const route = useRoute()
const handleClick = (audio: AudioDetail) => {
  sendSelectSearchResultEvent(audio)

  singleResultStore.setMediaById(AUDIO, props.audio.id)

  if (isResultsRoute(route)) {
    searchStore.setBackToSearchPath(route.fullPath)
    if (isSearchRoute(route) && props.searchTerm) {
      searchStore.setSearchTerm(props.searchTerm)
    }
  }
}
const sendSelectSearchResultEvent = (audio: AudioDetail) => {
  useAudioSnackbar().hide()
  sendCustomEvent("SELECT_SEARCH_RESULT", {
    id: audio.id,
    kind: props.kind,
    mediaType: AUDIO,
    query: props.searchTerm,
    provider: audio.provider,
    relatedTo: "null",
    sensitivities: audio.sensitivity?.join(",") ?? "",
    isBlurred: shouldBlur.value ?? "null",
  })
}
const sendInteractionEvent = (
  data: Omit<AudioInteractionData, "component">
) => {
  const component =
    props.kind === "related"
      ? "VRelatedAudio"
      : props.layout === "box"
      ? "VAllResultsGrid"
      : "AudioSearch"
  sendCustomEvent("AUDIO_INTERACTION", { ...data, component })
}
</script>
