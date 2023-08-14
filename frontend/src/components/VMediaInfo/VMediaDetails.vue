<template>
  <section class="flex w-full flex-col gap-y-6">
    <header class="flex flex-row items-center justify-between">
      <h2 class="heading-6 md:heading-5">
        {{ $t(`mediaDetails.${media.frontendMediaType}Info`) }}
      </h2>
      <VContentReportPopover :media="media" />
    </header>
    <div
      :class="{ 'flex flex-col items-start gap-6 md:flex-row': isAudio(media) }"
    >
      <div
        v-if="isAudio(media)"
        class="h-[75px] w-[75px] flex-none overflow-hidden rounded-sm lg:h-30 lg:w-30"
      >
        <VAudioThumbnail :audio="media" />
      </div>
      <div class="flex w-full flex-grow flex-col gap-6">
        <p v-if="media.description">{{ media.description }}</p>
        <VMediaTags :tags="media.tags" />
        <VMetadata v-if="metadata" :metadata="metadata" :media="media" />
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { AudioDetail, ImageDetail, Media, Metadata } from "~/types/media"
import { useI18n } from "~/composables/use-i18n"
import { getMediaMetadata } from "~/utils/metadata"

import VContentReportPopover from "~/components/VContentReport/VContentReportPopover.vue"
import VMetadata from "~/components/VMediaInfo/VMetadata.vue"
import VMediaTags from "~/components/VMediaInfo/VMediaTags.vue"
import VAudioThumbnail from "~/components/VAudioThumbnail/VAudioThumbnail.vue"

export default defineComponent({
  components: { VAudioThumbnail, VMediaTags, VMetadata, VContentReportPopover },
  props: {
    media: {
      type: Object as PropType<AudioDetail | ImageDetail>,
      required: true,
    },
    imageData: {
      type: Object as PropType<{ width: number; height: number; type: string }>,
    },
  },
  setup(props) {
    const i18n = useI18n()

    const metadata = computed<null | Metadata[]>(() => {
      if (!props.media) return null
      return getMediaMetadata(props.media, i18n, props.imageData)
    })

    const isAudio = (media: Media): media is AudioDetail =>
      media.frontendMediaType === "audio"

    return {
      metadata,
      isAudio,
    }
  },
})
</script>
