<template>
  <section
    id="title-button"
    class="flex flex-row flex-wrap justify-between gap-x-6 md:mt-6 md:flex-row-reverse"
  >
    <VGetMediaButton
      :media="image"
      media-type="image"
      class="mb-4 !w-full flex-initial md:mb-0 md:!w-max"
    />
    <div class="description-bold flex flex-1 flex-col justify-center">
      <h1 class="description-bold md:heading-5 line-clamp-2">
        {{ image.title }}
      </h1>
      <i18n-t
        v-if="image.creator"
        scope="global"
        keypath="imageDetails.creator"
        tag="span"
      >
        <template #name>
          <VLink
            v-if="image.creator_url"
            :aria-label="
              t('mediaDetails.aria.creatorUrl', {
                creator: image.creator,
              })
            "
            :href="image.creator_url"
            :send-external-link-click-event="false"
            @click="sendVisitCreatorLinkEvent"
            >{{ image.creator }}
          </VLink>
          <span v-else>{{ image.creator }}</span>
        </template>
      </i18n-t>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { ImageDetail } from "~/types/media"
import { useAnalytics } from "~/composables/use-analytics"

import VLink from "~/components/VLink.vue"
import VGetMediaButton from "~/components/VMediaInfo/VGetMediaButton.vue"

const props = defineProps<{
  image: ImageDetail
}>()

const {
  $i18n: { t },
} = useNuxtApp()

const { sendCustomEvent } = useAnalytics()

const sendVisitCreatorLinkEvent = () => {
  sendCustomEvent("VISIT_CREATOR_LINK", {
    id: props.image.id,
    source: props.image.source ?? props.image.provider,
    url: props.image.creator_url ?? "",
  })
}
</script>
