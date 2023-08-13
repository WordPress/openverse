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
    const imgType = computed(() => {
      if (props.imageType) {
        if (props.imageType.split("/").length > 1) {
          return props.imageType.split("/")[1].toUpperCase()
        }
        return props.imageType
      }
      return i18n.t("imageDetails.information.unknown")
    })

    const imageMetadata = computed<null | Metadata[]>(() => {
      if (!props.image) return null
      const metadata: Metadata[] = [
        {
          label: i18n.t("imageDetails.information.type"),
          value: imgType.value,
        },
      ]
      if (
        props.image.source &&
        props.image.providerName !== props.image.sourceName
      ) {
        metadata.push({
          label: i18n.t("imageDetails.information.provider"),
          value: props.image.providerName || props.image.provider,
        })
      }
      metadata.push({
        label: i18n.t("imageDetails.information.source"),
        value: props.image,
        component: "VSourceExternalLink",
      })
      metadata.push({
        label: i18n.t("imageDetails.information.dimensions"),
        value: `${props.imageWidth} × ${props.imageHeight} ${i18n.t(
          "imageDetails.information.pixels"
        )}`,
      })
      return metadata
    })

    return { imgType, imageMetadata }
  },
})
</script>
