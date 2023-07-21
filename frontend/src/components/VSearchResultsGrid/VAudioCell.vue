<template>
  <li>
    <VAudioTrack
      :audio="audio"
      layout="box"
      :search-term="searchTerm"
      v-bind="$attrs"
      v-on="$listeners"
      @interacted="sendInteractionEvent"
      @mousedown="sendSelectSearchResultEvent(audio)"
    />
  </li>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"

import { useAnalytics } from "~/composables/use-analytics"
import { AUDIO } from "~/constants/media"

import type { AudioInteractionData } from "~/types/analytics"

import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"

export default defineComponent({
  components: { VAudioTrack },
  inheritAttrs: false,
  props: {
    audio: {
      type: Object as PropType<AudioDetail>,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const { sendCustomEvent } = useAnalytics()

    const sendSelectSearchResultEvent = (audio: AudioDetail) => {
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
      sendCustomEvent("AUDIO_INTERACTION", {
        ...data,
        component: "VAllResultsGrid",
      })
    }

    return {
      sendSelectSearchResultEvent,
      sendInteractionEvent,
    }
  },
})
</script>
