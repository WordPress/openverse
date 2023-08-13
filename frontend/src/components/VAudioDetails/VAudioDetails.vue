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
    const audioFormats = computed(() => {
      if (!props.audio.alt_files) return props.audio.filetype ?? ""
      const altFormats = props.audio.alt_files.map(
        (altFile) => altFile.filetype
      )
      if (props.audio.filetype) {
        altFormats.unshift(props.audio.filetype)
      }
      const uniqueFormats = new Set(altFormats)
      return [...uniqueFormats].join(", ")
    })

    const audioMetadata = computed(() => {
      if (!props.audio) return null
      const metadata = []
      if (props.audio.audio_set) {
        metadata.push({
          label: i18n.t("audioDetails.table.album"),
          value: props.audio.audio_set.title,
          url: props.audio.audio_set.foreign_landing_url,
        })
      }
      if (props.audio.category) {
        metadata.push({
          label: i18n.t("audioDetails.table.category"),
          value: i18n.t(`filters.audioCategories.${props.audio.category}`),
        })
      }
      if (props.audio.sample_rate) {
        metadata.push({
          label: i18n.t("audioDetails.table.sampleRate"),
          value: props.audio.sample_rate.toString(),
        })
      }
      if (props.audio.filetype) {
        metadata.push({
          label: i18n.t("audioDetails.table.filetype"),
          value: audioFormats.value.toUpperCase(),
        })
      }
      if (
        props.audio.source &&
        props.audio.sourceName !== props.audio.providerName
      ) {
        metadata.push({
          label: i18n.t("audioDetails.table.provider"),
          value: props.audio.providerName || props.audio.provider,
        })
      }
      metadata.push({
        label: i18n.t("audioDetails.table.source"),
        value: props.audio,
        component: "VSourceExternalLink" as const,
      })
      if (props.audio.genres && props.audio.genres.length > 0) {
        metadata.push({
          label: i18n.t("audioDetails.table.genre"),
          value: props.audio.genres.join(", "),
        })
      }
      return metadata
    })

    return { audioFormats, audioMetadata }
  },
})
</script>
