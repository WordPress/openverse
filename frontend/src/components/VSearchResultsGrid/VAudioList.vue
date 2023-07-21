<template>
  <!-- Negative margin compensates for the `p-4` padding in row layout. -->
  <ol
    :aria-label="collectionLabel"
    class="-mx-2 flex flex-col md:-mx-4"
    :class="{ 'gap-4': isRelated }"
  >
    <li
      v-for="audio in results"
      :key="audio.id"
      :class="{ 'mb-2 md:mb-1': !isRelated }"
    >
      <VAudioTrack
        :audio="audio"
        :size="audioTrackSize"
        layout="row"
        :search-term="searchTerm"
        @interacted="handleInteraction"
        @mousedown="handleMousedown(audio, $event)"
        @focus="$emit('focus', $event)"
      />
    </li>
  </ol>
</template>

<script lang="ts">
import { computed, defineComponent, inject, ref, PropType } from "vue"
import { useRoute } from "@nuxtjs/composition-api"

import type { AudioInteractionData } from "~/types/analytics"
import type { AudioDetail } from "~/types/media"
import { IsSidebarVisibleKey } from "~/types/provides"
import { defineEvent } from "~/types/emits"
import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"
import { useAnalytics } from "~/composables/use-analytics"
import { AUDIO } from "~/constants/media"

import type { AudioTrackClickEvent } from "~/types/events"

import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"

/**
 * The list of audio for the search results and the related audio.
 */
export default defineComponent({
  name: "VAudioList",
  components: { VAudioTrack },
  props: {
    results: {
      type: Array as PropType<AudioDetail[]>,
      default: () => [],
    },
    isRelated: {
      type: Boolean,
      required: true,
    },
    /**
     * The label used for the list of audio for accessibility.
     */
    collectionLabel: {
      type: String,
      required: true,
    },
  },
  emits: {
    interacted: defineEvent<[Omit<AudioInteractionData, "component">]>(),
    mousedown: defineEvent<[AudioTrackClickEvent]>(),
    focus: defineEvent<[FocusEvent]>(),
  },
  setup(props, { emit }) {
    const route = useRoute()
    const uiStore = useUiStore()

    const filterVisibleRef = inject(IsSidebarVisibleKey, ref(false))

    const audioTrackSize = computed(() => {
      if (props.isRelated) {
        return uiStore.isBreakpoint("md") ? "l" : "s"
      } else {
        return !uiStore.isDesktopLayout
          ? "s"
          : filterVisibleRef.value
          ? "l"
          : "m"
      }
    })

    const searchStore = useSearchStore()
    const searchTerm = computed(() => searchStore.searchTerm)

    const { sendCustomEvent } = useAnalytics()
    const handleInteraction = (
      data: Omit<AudioInteractionData, "component">
    ) => {
      sendCustomEvent("AUDIO_INTERACTION", {
        ...data,
        component: props.isRelated ? "VRelatedAudio" : "AudioSearch",
      })
      emit("interacted", data)
    }
    const handleMousedown = (
      audio: AudioDetail,
      { event, inWaveform }: AudioTrackClickEvent
    ) => {
      // We only navigate when clicking the audio track outside the waveform.
      if (!inWaveform) {
        sendCustomEvent("SELECT_SEARCH_RESULT", {
          id: audio.id,
          relatedTo: props.isRelated ? route.value.params.id : null,
          mediaType: AUDIO,
          provider: audio.provider,
          query: searchTerm.value,
        })
      }
      emit("mousedown", { event, inWaveform })
    }

    return {
      audioTrackSize,
      searchTerm,

      handleInteraction,
      handleMousedown,
    }
  },
})
</script>
