<template>
  <main :id="skipToContentTargetId" tabindex="-1" class="relative flex-grow">
    <VSafetyWall v-if="isHidden" :media="audio" @reveal="reveal" />
    <template v-else>
      <VSingleResultControls v-if="audio" :media="audio" />
      <template v-if="audio">
        <VAudioTrack
          layout="full"
          :audio="audio"
          class="main-track"
          @interacted="sendAudioEvent($event, 'AudioDetailPage')"
        />
        <div
          class="mx-auto mt-10 flex flex-col gap-10 px-6 lg:mt-16 lg:max-w-5xl lg:gap-16"
        >
          <VMediaReuse data-testid="audio-attribution" :media="audio" />
          <VAudioDetails data-testid="audio-info" :audio="audio" />
          <VRelatedAudio
            @interacted="sendAudioEvent($event, 'VRelatedAudio')"
          />
        </div>
      </template>
    </template>
  </main>
</template>

<script lang="ts">
import { ref } from "vue"
import {
  defineComponent,
  useContext,
  useFetch,
  useMeta,
  useRoute,
} from "@nuxtjs/composition-api"

import { AUDIO } from "~/constants/media"
import { skipToContentTargetId } from "~/constants/window"
import type { AudioDetail } from "~/types/media"
import type { AudioInteractionData } from "~/types/analytics"
import { useAnalytics } from "~/composables/use-analytics"
import { useSensitiveMedia } from "~/composables/use-sensitive-media"
import { singleResultMiddleware } from "~/middleware/single-result"
import { useSingleResultStore } from "~/stores/media/single-result"
import { createDetailPageMeta } from "~/utils/og"

import { useI18n } from "~/composables/use-i18n"

import VAudioDetails from "~/components/VAudioDetails/VAudioDetails.vue"
import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"
import VMediaReuse from "~/components/VMediaInfo/VMediaReuse.vue"
import VRelatedAudio from "~/components/VAudioDetails/VRelatedAudio.vue"

export default defineComponent({
  name: "AudioDetailPage",
  components: {
    VAudioDetails,
    VAudioTrack,
    VMediaReuse,
    VRelatedAudio,
  },
  layout: "content-layout",
  middleware: singleResultMiddleware,
  // Fetching on the server is disabled because it is
  // handled by the `singleResultMiddleware`.
  fetchOnServer: false,
  setup() {
    const singleResultStore = useSingleResultStore()

    const route = useRoute()

    const audio = ref<AudioDetail | null>(singleResultStore.audio)

    const { error: nuxtError } = useContext()
    const i18n = useI18n()

    useFetch(async () => {
      const audioId = route.value.params.id
      await singleResultStore.fetch(AUDIO, audioId)

      const fetchedAudio = singleResultStore.audio

      if (!fetchedAudio) {
        nuxtError(singleResultStore.fetchState.fetchingError ?? {})
      } else {
        audio.value = fetchedAudio
      }
    })

    const { sendCustomEvent } = useAnalytics()
    const sendAudioEvent = (
      data: Omit<AudioInteractionData, "component">,
      component: "AudioDetailPage" | "VRelatedAudio"
    ) => {
      sendCustomEvent("AUDIO_INTERACTION", {
        ...data,
        component,
      })
    }

    const { isHidden, reveal, hide } = useSensitiveMedia(audio.value)

    useMeta(() =>
      createDetailPageMeta(
        isHidden.value
          ? i18n.t("sensitiveContent.title.audio").toString()
          : audio.value?.title,
        isHidden.value ? undefined : audio.value?.url
      )
    )

    return {
      audio,

      sendAudioEvent,

      skipToContentTargetId,

      isHidden,
      reveal,
      hide,
    }
  },
  head: {},
})
</script>
<style>
.audio-page {
  --wp-max-width: 940px;
}
.audio-page section,
.audio-page aside {
  max-width: var(--wp-max-width);
  margin-right: auto;
  margin-left: auto;
}
.audio-page .full-track .mx-16 {
  @apply mt-6;
  @apply px-4 md:px-0;
  max-width: var(--wp-max-width);
  margin-right: auto;
  margin-left: auto;
}
</style>
