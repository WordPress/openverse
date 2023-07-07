<template>
  <VSkipToContentContainer
    as="main"
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
        v-html="getAttributionMarkup({ includeIcons: false })"
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
  </VSkipToContentContainer>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue"

import { useI18n } from "~/composables/use-i18n"
import { IMAGE } from "~/constants/media"
import { useSingleResultStore } from "~/stores/media/single-result"
import { AttributionOptions, getAttribution } from "~/utils/attribution-html"
import type { ImageDetail } from "~/types/media"

import VButton from "~/components/VButton.vue"
import VContentReportForm from "~/components/VContentReport/VContentReportForm.vue"
import VSkipToContentContainer from "~/components/VSkipToContentContainer.vue"

export default defineComponent({
  name: "ReportImage",
  components: {
    VButton,
    VContentReportForm,
    VSkipToContentContainer,
  },
  layout: "content-layout",
  setup() {
    const image = ref<ImageDetail | null>(null)

    const getAttributionMarkup = (options?: AttributionOptions) => {
      return image.value ? getAttribution(image.value, useI18n(), options) : ""
    }

    return {
      image,
      getAttributionMarkup,
    }
  },
  async asyncData({ route, $pinia, error: nuxtError }) {
    const singleResultStore = useSingleResultStore($pinia)
    try {
      await singleResultStore.fetch(IMAGE, route.params.id, {
        fetchRelated: false,
      })

      const image = singleResultStore.image
      if (!image) {
        throw new Error("Image not found")
      }
      return {
        image,
      }
    } catch (error) {
      return nuxtError({
        statusCode: 404,
        message: "Image not found",
      })
    }
  },
})
</script>
