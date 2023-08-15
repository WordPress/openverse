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
import { defineComponent, PropType } from "vue"

import { useAnalytics } from "~/composables/use-analytics"
import { useAudioSnackbar } from "~/composables/use-audio-snackbar"
import { AUDIO } from "~/constants/media"

import type { AudioInteractionData } from "~/types/analytics"
import type { AudioLayout, AudioSize } from "~/constants/audio"
import type { AudioTrackClickEvent } from "~/types/events"
import type { AudioDetail } from "~/types/media"

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
    isRelated: {
      type: Boolean,
      required: true,
    },
  },
  setup(props) {
    const { sendCustomEvent } = useAnalytics()

    const sendSelectSearchResultEvent = (
      audio: AudioDetail,
      { inWaveform }: AudioTrackClickEvent
    ) => {
      // Only send the event when the click navigates to the single result page.
      // If the click is in waveform or play-pause button, it controls the audio player.
      if (inWaveform) return
      useAudioSnackbar().hide()
      sendCustomEvent("SELECT_SEARCH_RESULT", {
        id: audio.id,
        mediaType: AUDIO,
        query: props.searchTerm,
        provider: audio.provider,
        relatedTo: null,
      })
    }
    const sendInteractionEvent = (
      data: Omit<AudioInteractionData, "component">
    ) => {
      const component = props.isRelated
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
