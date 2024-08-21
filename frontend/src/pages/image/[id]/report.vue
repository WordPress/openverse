<script setup lang="ts">
import { defineNuxtRouteMiddleware, definePageMeta, useI18n } from "#imports"

import { computed } from "vue"

import { IMAGE } from "~/constants/media"
import { skipToContentTargetId } from "~/constants/window"

import { useContentReport } from "~/composables/use-content-report"
import { useSingleResultStore } from "~/stores/media/single-result"

import { getAttribution } from "~/utils/attribution-html"
import { firstParam } from "~/utils/query-utils"

import VButton from "~/components/VButton.vue"
import VContentReportForm from "~/components/VContentReport/VContentReportForm.vue"

defineOptions({
  name: "ImageReportPage",
})

definePageMeta({
  layout: "content-layout",
  middleware: defineNuxtRouteMiddleware(async (to) => {
    const imageId = firstParam(to.params?.id)
    const singleResultStore = useSingleResultStore()
    await singleResultStore.fetch(IMAGE, imageId)
  }),
})

const i18n = useI18n({ useScope: "global" })
const singleResultStore = useSingleResultStore()

const image = computed(() => singleResultStore.image)
const attributionMarkup = computed(() =>
  image.value
    ? getAttribution(image.value, i18n, {
        includeIcons: false,
      })
    : ""
)
const { status, updateStatus, title } = useContentReport()
</script>

<template>
  <main
    :id="skipToContentTargetId"
    tabindex="-1"
    class="mx-auto mb-6 mt-8 max-w-none gap-x-10 px-4 md:grid md:max-w-4xl md:grid-cols-2 md:px-6 lg:mb-30 lg:px-0 xl:max-w-4xl"
  >
    <figure v-if="image" class="mb-6 flex flex-col items-start gap-y-4">
      <img
        id="main-image"
        :src="image.thumbnail"
        :alt="image.title"
        class="mx-auto h-auto w-full rounded-sm"
        :width="image.width"
        :height="image.height"
      />
      <!-- Disable reason: We control the attribution HTML generation so this is safe and will not lead to XSS attacks -->
      <!-- eslint-disable vue/no-v-html -->
      <figcaption
        class="block w-full text-left text-sr"
        v-html="attributionMarkup"
      />
      <!-- eslint-enable vue/no-v-html -->
      <VButton
        variant="bordered-gray"
        :href="`/image/${image.id}`"
        as="VLink"
        size="medium"
        class="label-bold"
      >
        {{ $t("report.imageDetails") }}
      </VButton>
    </figure>

    <div>
      <h2 class="heading-6 mb-4">{{ title }}</h2>
      <VContentReportForm
        v-if="image"
        :media="image"
        :allow-cancel="false"
        :status="status"
        @update-status="updateStatus"
      />
    </div>
  </main>
</template>
