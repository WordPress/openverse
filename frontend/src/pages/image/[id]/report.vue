<script setup lang="ts">
import { definePageMeta, useAsyncData, useI18n, useRoute } from "#imports"

import { ref } from "vue"

import { IMAGE } from "~/constants/media"
import { skipToContentTargetId } from "~/constants/window"

import { useSingleResultStore } from "~/stores/media/single-result"
import { getAttribution } from "~/utils/attribution-html"
import { firstParam } from "~/utils/query-utils"
import type { ImageDetail } from "~/types/media"

import VButton from "~/components/VButton.vue"
import VContentReportForm from "~/components/VContentReport/VContentReportForm.vue"

defineOptions({
  name: "ImageReportPage",
})

definePageMeta({
  layout: "content-layout",
})

const i18n = useI18n({ useScope: "global" })
const route = useRoute()
const singleResultStore = useSingleResultStore()

const image = ref<ImageDetail>()
const attributionMarkup = ref<string>()

await useAsyncData("image-report", async () => {
  const imageId = firstParam(route?.params.id)
  if (imageId) {
    image.value = (await singleResultStore.fetch(IMAGE, imageId)) ?? undefined
    if (image.value) {
      attributionMarkup.value = getAttribution(image.value, i18n, {
        includeIcons: false,
      })
    }
  } else {
    // TODO: Handle Error
    console.warn("Not found image")
  }
})
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

    <VContentReportForm
      v-if="image"
      :close-fn="() => {}"
      :media="image"
      :allow-cancel="false"
      :provider-name="image.providerName || image.provider"
    />
  </main>
</template>
