<template>
  <li>
    <VAudioTrack
      :audio="audio"
      :layout="layout"
      :size="size"
      :search-term="searchTerm"
      v-bind="$attrs"
      v-on="$listeners"
      @interacted="sendInteractionEvent"
      @mousedown="sendSelectSearchResultEvent(audio, $event)"
    />
  </li>
</template>

<script lang="ts">
import { defineComponent, PropType, toRefs } from "vue"

import { useAnalytics } from "~/composables/use-analytics"
import { useAudioSnackbar } from "~/composables/use-audio-snackbar"
import { useSensitiveMedia } from "~/composables/use-sensitive-media"
import { AUDIO } from "~/constants/media"

import type { AudioInteractionData } from "~/types/analytics"
import type { AudioLayout, AudioSize } from "~/constants/audio"
import type { AudioTrackClickEvent } from "~/types/events"
import type { AudioDetail } from "~/types/media"
import type { ResultKind } from "~/types/result"

import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"

export default defineComponent({
  name: "VAudioResult",
  components: { VAudioTrack },
  inheritAttrs: false,
  props: {
    layout: {
      type: String as PropType<Extract<AudioLayout, "box" | "row">>,
      required: true,
    },
    size: {
      type: String as PropType<AudioSize>,
    },
    audio: {
      type: Object as PropType<AudioDetail>,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
    kind: {
      type: String as PropType<ResultKind>,
      default: "search",
    },
  },
  setup(props) {
    const { sendCustomEvent } = useAnalytics()

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
      sendCustomEvent("SELECT_SEARCH_RESULT", {
        id: audio.id,
        kind: props.kind,
        mediaType: AUDIO,
        query: props.searchTerm,
        provider: audio.provider,
        relatedTo: null,
        sensitivities: audio.sensitivity?.join(",") ?? "",
        isBlurred: shouldBlur.value,
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

    return {
      sendSelectSearchResultEvent,
      sendInteractionEvent,
    }
  },
})
</script>
