<template>
  <section class="audio-info">
    <header class="mb-6 flex flex-row items-center justify-between">
      <h2 class="heading-6 md:heading-5">
        {{ $t("audioDetails.information") }}
      </h2>
      <VContentReportPopover :media="audio" />
    </header>

    <div class="flex flex-col items-start gap-6 md:flex-row">
      <div class="h-[75px] w-[75px] overflow-hidden rounded-sm lg:h-30 lg:w-30">
        <VAudioThumbnail :audio="audio" />
      </div>
      <div class="flex flex-grow flex-col gap-6">
        <p v-if="audio.description">{{ audio.description }}</p>
        <VMediaTags :tags="audio.tags" />
        <VMetadata
          v-if="audioMetadata"
          :metadata="audioMetadata"
          :media="audio"
        />
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"

import { useI18n } from "~/composables/use-i18n"

import { getMediaMetadata } from "~/utils/metadata"

import VAudioThumbnail from "~/components/VAudioThumbnail/VAudioThumbnail.vue"
import VContentReportPopover from "~/components/VContentReport/VContentReportPopover.vue"
import VMediaTags from "~/components/VMediaInfo/VMediaTags.vue"
import VMetadata from "~/components/VMediaInfo/VMetadata.vue"

export default defineComponent({
  name: "VAudioDetails",
  components: {
    VMediaTags,
    VAudioThumbnail,
    VContentReportPopover,
    VMetadata,
  },
  props: {
    audio: {
      type: Object as PropType<AudioDetail>,
      required: true,
    },
  },
  setup(props) {
    const i18n = useI18n()

    const audioMetadata = computed(() => {
      if (!props.audio) return null
      return getMediaMetadata(props.audio, i18n)
    })

    return { audioMetadata }
  },
})
</script>
