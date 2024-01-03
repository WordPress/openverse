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

<script lang="ts">
import { defineNuxtComponent, definePageMeta } from "#imports"

import { IMAGE } from "~/constants/media"
import { skipToContentTargetId } from "~/constants/window"

import { useSingleResultStore } from "~/stores/media/single-result"
import { getAttribution } from "~/utils/attribution-html"
import type { ImageDetail } from "~/types/media"

import VButton from "~/components/VButton.vue"
import VContentReportForm from "~/components/VContentReport/VContentReportForm.vue"

export default defineNuxtComponent({
  name: "ReportImage",
  components: {
    VButton,
    VContentReportForm,
  },
  setup() {
    definePageMeta({ layout: "content-layout" })
    return {}
  },
  async asyncData({ route, $pinia, i18n, error: nuxtError }) {
    const singleResultStore = useSingleResultStore($pinia)
    const imageId = route.params.id
    const image = await singleResultStore.fetch(IMAGE, imageId)
    if (!image) {
      return nuxtError({
        statusCode: 404,
        message: i18n
          .t("error.imageNotFound", {
            id: imageId,
          })
          .toString(),
      })
    }
    const attributionMarkup = getAttribution(image, i18n, {
      includeIcons: false,
    })
    return {
      attributionMarkup,
      image,
    }
  },
  data: () => ({
    image: null as ImageDetail | null,
    attributionMarkup: "",
    skipToContentTargetId,
  }),
})
</script>
