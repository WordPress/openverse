<template>
  <section class="flex w-full flex-col gap-y-6">
    <div class="flex flex-row items-center justify-between">
      <h2 class="heading-6 md:heading-5">
        {{ $t("imageDetails.information.title") }}
      </h2>
      <VContentReportPopover :media="image" />
    </div>
    <VMediaTags :tags="image.tags" />
    <VMetadata v-if="imageMetadata" :metadata="imageMetadata" :media="image" />
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { useI18n } from "~/composables/use-i18n"

import { getMediaMetadata } from "~/utils/metadata"
import type { ImageDetail, Metadata } from "~/types/media"

import VContentReportPopover from "~/components/VContentReport/VContentReportPopover.vue"
import VMediaTags from "~/components/VMediaInfo/VMediaTags.vue"
import VMetadata from "~/components/VMediaInfo/VMetadata.vue"

export default defineComponent({
  name: "VImageDetails",
  components: { VContentReportPopover, VMediaTags, VMetadata },
  props: {
    image: {
      type: Object as PropType<ImageDetail>,
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

    const imageMetadata = computed<null | Metadata[]>(() => {
      return props.image
        ? getMediaMetadata(props.image, i18n, {
            width: props.imageWidth,
            height: props.imageHeight,
            type: props.imageType,
          })
        : null
    })

    return { imageMetadata }
  },
})
</script>
