<script setup lang="ts">
import { useI18n } from "#imports"

import { computed } from "vue"

import type { AudioDetail, ImageDetail, Metadata } from "~/types/media"
import { IMAGE } from "~/constants/media"

import { getMediaMetadata } from "~/utils/metadata"

import VContentReportModal from "~/components/VContentReport/VContentReportModal.vue"
import VMetadata from "~/components/VMediaInfo/VMetadata.vue"
import VMediaTags from "~/components/VMediaInfo/VMediaTags.vue"

const props = defineProps<{ media: AudioDetail | ImageDetail }>()

const i18n = useI18n({ useScope: "global" })

const metadata = computed<null | Metadata[]>(() => {
  if (!props.media) {
    return null
  }
  const imageInfo =
    props.media.frontendMediaType === IMAGE
      ? {
          width: props.media.width,
          height: props.media.height,
          type: props.media.filetype,
        }
      : {}
  return getMediaMetadata(props.media, i18n, imageInfo)
})
</script>

<template>
  <section class="flex flex-col gap-y-6 md:gap-y-8">
    <header class="flex flex-row items-center justify-between">
      <h2 class="heading-6 md:heading-5">
        {{ $t(`mediaDetails.${media.frontendMediaType}Info`) }}
      </h2>
      <VContentReportModal :media="media" />
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
