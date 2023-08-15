<template>
  <section class="flex flex-col gap-y-6">
    <header class="flex flex-row items-center justify-between">
      <h2 class="heading-6 md:heading-5">
        {{ $t(`mediaDetails.${media.frontendMediaType}Info`) }}
      </h2>
      <VContentReportPopover :media="media" />
    </header>
    <div class="flex flex-col items-start gap-6 md:flex-row">
      <slot name="thumbnail" />

      <div class="flex flex-grow flex-col gap-6">
        <p v-if="media.description">{{ media.description }}</p>
        <VMediaTags :tags="media.tags" />
        <VAudioMetadata v-if="isDetail.audio(media)" :audio="media" />
        <VImageMetadata
          v-else-if="isDetail.image(media)"
          :image="media"
          v-bind="imageData"
        />
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { AudioDetail, ImageDetail } from "~/types/media"

import { isDetail } from "~/types/media"

import VContentReportPopover from "~/components/VContentReport/VContentReportPopover.vue"
import VAudioMetadata from "~/components/VMediaInfo/VAudioMetadata.vue"
import VImageMetadata from "~/components/VMediaInfo/VImageMetadata.vue"
import VMediaTags from "~/components/VMediaInfo/VMediaTags.vue"

export default defineComponent({
  components: {
    VImageMetadata,
    VAudioMetadata,
    VMediaTags,
    VContentReportPopover,
  },
  props: {
    media: {
      type: Object as PropType<AudioDetail | ImageDetail>,
      required: true,
    },
    imageData: {
      type: Object as PropType<{
        width: number
        height: number
        imageType: string
      }>,
    },
  },
  setup() {
    return {
      isDetail,
    }
  },
})
</script>
