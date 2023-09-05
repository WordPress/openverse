<template>
  <main :id="skipToContentTargetId" tabindex="-1" class="relative flex-grow">
    <template v-if="audio">
      <VSafetyWall v-if="isHidden" :media="audio" @reveal="reveal" />
      <template v-else>
        <VSingleResultControls :media="audio" />
        <VAudioTrack
          layout="full"
          :audio="audio"
          class="main-track"
          @interacted="sendAudioEvent($event, 'AudioDetailPage')"
        />
        <div
          class="mx-auto mt-10 flex flex-col gap-10 px-6 lg:mt-16 lg:max-w-5xl lg:gap-16"
        >
          <VMediaReuse :media="audio" />
          <VMediaDetails :media="audio">
            <template #thumbnail>
              <div
                class="h-[75px] w-[75px] flex-none overflow-hidden rounded-sm lg:h-30 lg:w-30"
              >
                <VAudioThumbnail :audio="audio" />
              </div>
            </template>
          </VMediaDetails>
          <VRelatedAudio
            @interacted="sendAudioEvent($event, 'VRelatedAudio')"
          />
        </div>
      </template>
    </template>
  </main>
</template>

<script lang="ts">
import { computed, ref } from "vue"
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

import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"
import VMediaReuse from "~/components/VMediaInfo/VMediaReuse.vue"
import VRelatedAudio from "~/components/VAudioDetails/VRelatedAudio.vue"
import VMediaDetails from "~/components/VMediaInfo/VMediaDetails.vue"
import VSafetyWall from "~/components/VSafetyWall/VSafetyWall.vue"
import VSingleResultControls from "~/components/VSingleResultControls.vue"
import VAudioThumbnail from "~/components/VAudioThumbnail/VAudioThumbnail.vue"

export default defineComponent({
  name: "AudioDetailPage",
  components: {
    VAudioThumbnail,
    VSingleResultControls,
    VSafetyWall,
    VMediaDetails,
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
    const isSensitive = computed(() => audio.value?.isSensitive ?? false)

    const getPageTitle = (
      isHidden: boolean | null,
      audio: AudioDetail | null | undefined
    ) => {
      return `${
        isHidden ? i18n.t("sensitiveContent.title.audio") : audio?.title
      } | Openverse`
    }

    const pageTitle = ref(getPageTitle(isHidden.value, audio.value))
    // Do not show sensitive content title in the social preview cards.
    const detailPageMeta = createDetailPageMeta(
      isSensitive.value
        ? {
            title: `${i18n.t("sensitiveContent.title.audio")}`,
            thumbnail: undefined,
          }
        : {
            title:
              audio.value?.title ?? `${i18n.t("mediaDetails.reuse.audio")}`,
            thumbnail: audio.value?.thumbnail,
          }
    )
    useMeta(() => ({
      ...detailPageMeta,
      title: pageTitle.value,
    }))

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
