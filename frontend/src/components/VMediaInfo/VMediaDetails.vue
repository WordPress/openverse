<template>
  <section class="flex flex-col gap-y-6 md:gap-y-8">
    <header class="flex flex-row items-center justify-between">
      <h2 class="heading-6 md:heading-5">
        {{ $t(`mediaDetails.${media.frontendMediaType}Info`) }}
      </h2>
      <VContentReportPopover :media="media" />
    </header>
    <div class="flex flex-col items-start gap-6 md:flex-row">
      <slot name="thumbnail" />

      <div class="flex flex-col gap-6 md:gap-8">
        <div
          class="flex w-full flex-grow flex-col items-start gap-6 md:flex-row"
        >
          <p v-if="media.description">{{ media.description }}</p>
          <VMetadata v-if="metadata" :metadata="metadata" />
        </div>
        <VMediaTags
          :tags="media.tags"
          :media-type="media.frontendMediaType"
          :provider="media.provider"
        />
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { AudioDetail, ImageDetail, Metadata } from "~/types/media"

import { useI18n } from "~/composables/use-i18n"
import { getMediaMetadata } from "~/utils/metadata"

import VContentReportPopover from "~/components/VContentReport/VContentReportPopover.vue"
import VMetadata from "~/components/VMediaInfo/VMetadata.vue"
import VMediaTags from "~/components/VMediaInfo/VMediaTags.vue"

export default defineComponent({
  components: {
    VMediaTags,
    VMetadata,
    VContentReportPopover,
  },
  props: {
    media: {
      type: Object as PropType<AudioDetail | ImageDetail>,
      required: true,
    },
    imageWidth: {
      type: Number,
    },
    imageHeight: {
      type: Number,
    },
    imageType: {
      type: String,
    },
  },
  setup(props) {
    const i18n = useI18n()

    const metadata = computed<null | Metadata[]>(() => {
      if (!props.media) {
        return null
      }
      return getMediaMetadata(props.media, i18n, {
        width: props.imageWidth,
        height: props.imageHeight,
        type: props.imageType,
      })
    })

    return {
      metadata,
    }
  },
})
</script>
