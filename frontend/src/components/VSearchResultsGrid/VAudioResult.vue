<script setup lang="ts">
import { useNuxtApp } from "#imports"
import { toRefs } from "vue"

import { AUDIO } from "#shared/constants/media"
import type { AudioLayout, AudioSize } from "#shared/constants/audio"
import type { AudioInteractionData } from "#shared/types/analytics"
import type { AudioTrackClickEvent } from "#shared/types/events"
import type { AudioDetail } from "#shared/types/media"
import type { SingleResultProps } from "#shared/types/collection-component-props"
import { useSearchStore } from "~/stores/search"
import { useSensitiveMedia } from "~/composables/use-sensitive-media"
import { useAudioSnackbar } from "~/composables/use-audio-snackbar"

import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"

defineOptions({ inheritAttrs: false })

const props = withDefaults(
  defineProps<
    SingleResultProps & {
      layout: Extract<AudioLayout, "box" | "row">
      size?: AudioSize
      audio: AudioDetail
    }
  >(),
  { relatedTo: "null" }
)

const { $sendCustomEvent } = useNuxtApp()
const searchStore = useSearchStore()

const { audio } = toRefs(props)
const { isHidden: shouldBlur } = useSensitiveMedia(audio)

const sendSelectSearchResultEvent = (
  audio: AudioDetail,
  { inWaveform }: AudioTrackClickEvent
) => {
  // Only send the event when the click navigates to the single result page.
  // If the click is in waveform or audio-control button, it controls the audio player.
  if (inWaveform) {
    return
  }
  useAudioSnackbar().hide()
  $sendCustomEvent("SELECT_SEARCH_RESULT", {
    id: audio.id,
    kind: props.kind,
    mediaType: AUDIO,
    query: props.searchTerm,
    provider: audio.provider,
    relatedTo: props.relatedTo ?? "null",
    sensitivities: audio.sensitivity?.join(",") ?? "",
    isBlurred: shouldBlur.value ?? "null",
    collectionType:
      searchStore.strategy !== "default" ? searchStore.strategy : "null",
    collectionValue: searchStore.collectionValue ?? "null",
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
  $sendCustomEvent("AUDIO_INTERACTION", { ...data, component })
}
</script>

<template>
  <li>
    <VAudioTrack
      :audio="audio"
      :layout="layout"
      :size="size"
      :search-term="searchTerm"
      v-bind="$attrs"
      @interacted="sendInteractionEvent"
      @mousedown="sendSelectSearchResultEvent(audio, $event)"
    />
  </li>
</template>
