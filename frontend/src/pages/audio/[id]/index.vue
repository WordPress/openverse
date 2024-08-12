<script setup lang="ts">
import {
  definePageMeta,
  firstParam,
  handledClientSide,
  showError,
  useAsyncData,
  useHead,
  useNuxtApp,
  useRoute,
  useSingleResultPageMeta,
} from "#imports"

import { computed, ref, watch } from "vue"

import { AUDIO } from "~/constants/media"
import { skipToContentTargetId } from "~/constants/window"
import type { AudioDetail } from "~/types/media"
import type { AudioInteractionData } from "~/types/analytics"
import { validateUUID } from "~/utils/query-utils"

import { useAnalytics } from "~/composables/use-analytics"
import { useSensitiveMedia } from "~/composables/use-sensitive-media"
import { useSingleResultStore } from "~/stores/media/single-result"
import singleResultMiddleware from "~/middleware/single-result"

import { usePageRobotsRule } from "~/composables/use-page-robots-rule"

import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"
import VMediaReuse from "~/components/VMediaInfo/VMediaReuse.vue"
import VRelatedMedia from "~/components/VMediaInfo/VRelatedMedia.vue"
import VMediaDetails from "~/components/VMediaInfo/VMediaDetails.vue"
import VSafetyWall from "~/components/VSafetyWall/VSafetyWall.vue"
import VSingleResultControls from "~/components/VSingleResultControls.vue"
import VAudioThumbnail from "~/components/VAudioThumbnail/VAudioThumbnail.vue"
import VErrorSection from "~/components/VErrorSection/VErrorSection.vue"

defineOptions({
  name: "AudioDetailPage",
})

definePageMeta({
  layout: "content-layout",
  middleware: singleResultMiddleware,
})

usePageRobotsRule("single-result")

const singleResultStore = useSingleResultStore()

const route = useRoute()
const mediaId = computed(() => firstParam(route?.params.id))

const nuxtApp = useNuxtApp()

if (!mediaId.value || !validateUUID(mediaId.value)) {
  showError({
    statusCode: 404,
    message: `Invalid audio id: "${mediaId.value}".`,
    fatal: true,
  })
}

const audio = ref<AudioDetail | null>(
  singleResultStore.audio?.id &&
    mediaId.value &&
    singleResultStore.audio.id === mediaId.value
    ? singleResultStore.audio
    : null
)
const fetchingError = computed(() => singleResultStore.fetchState.fetchingError)

const { isHidden, reveal } = useSensitiveMedia(audio.value)

const { pageTitle, detailPageMeta } = useSingleResultPageMeta(audio)

useHead(() => ({
  ...detailPageMeta,
  title: pageTitle.value,
}))

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

const fetchAudio = async () => {
  if (nuxtApp.isHydrating) {
    return audio.value
  }

  const fetchedAudio = await singleResultStore.fetch(AUDIO, mediaId.value)
  if (fetchedAudio) {
    audio.value = fetchedAudio
    return fetchedAudio
  }
  throw new Error(`Could not fetch audio with id ${mediaId.value}`)
}

const { error } = await useAsyncData(
  "single-audio",
  async () => {
    return await fetchAudio()
  },
  { lazy: true, server: false }
)

const handleError = (error: Error) => {
  if (["Audio not found", "Audio ID not found"].includes(error.message)) {
    showError({
      statusCode: 404,
      message: "Audio ID not found",
      fatal: true,
    })
  }
  if (fetchingError.value && !handledClientSide(fetchingError.value)) {
    showError({
      ...(fetchingError.value ?? {}),
      fatal: true,
    })
  }
}

if (error.value) {
  handleError(error.value)
}
watch(error, (err) => {
  if (err) {
    handleError(err)
  }
})
</script>

<template>
  <main :id="skipToContentTargetId" tabindex="-1" class="relative flex-grow">
    <VErrorSection
      v-if="fetchingError"
      :fetching-error="fetchingError"
      class="px-6 py-10 lg:px-10"
    />
    <template v-else-if="audio">
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
          <VRelatedMedia
            v-if="audio"
            media-type="audio"
            :related-to="audio.id"
            class="mb-12"
          />
        </div>
      </template>
    </template>
  </main>
</template>
