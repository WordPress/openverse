<template>
  <VSkipToContentContainer
    as="main"
    class="mx-auto mb-6 mt-8 max-w-none gap-x-10 px-4 md:grid md:max-w-4xl md:grid-cols-2 md:px-6 lg:mb-30 lg:px-0 xl:max-w-4xl"
  >
    <figure class="mb-6 flex flex-col items-start gap-y-4">
      <img
        id="main-image"
        :src="imageSrc"
        :alt="image.title"
        class="mx-auto h-auto w-full rounded-sm"
        :width="imageWidth"
        :height="imageHeight"
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
        {{ $t("report.image-details") }}
      </VButton>
    </figure>

    <VContentReportForm
      :close-fn="() => {}"
      :media="image"
      :allow-cancel="false"
      :provider-name="image.providerName"
    />
  </VSkipToContentContainer>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from "vue"

import { useI18n } from "~/composables/use-i18n"

import { IMAGE } from "~/constants/media"

import { useSingleResultStore } from "~/stores/media/single-result"
import type { ImageDetail } from "~/types/media"
import { AttributionOptions, getAttribution } from "~/utils/attribution-html"

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
    const i18n = useI18n()
    const singleResultStore = useSingleResultStore()
    const image = computed(() =>
      singleResultStore.mediaType === IMAGE
        ? (singleResultStore.mediaItem as ImageDetail)
        : null
    )
    const imageWidth = ref(0)
    const imageHeight = ref(0)
    const imageType = ref("Unknown")
    /**
     * To make sure that image is loaded fast, we `src` to `image.thumbnail`,
     * and then replace it with the provider image once it is loaded.
     */
    const imageSrc = ref(image.value.thumbnail)

    const getAttributionMarkup = (options?: AttributionOptions) =>
      getAttribution(image.value, i18n, options)

    return {
      image,
      imageWidth,
      imageHeight,
      imageType,
      imageSrc,
      getAttributionMarkup,
    }
  },
  async asyncData({ app, error, route, $pinia }) {
    const imageId = route.params.id
    const singleResultStore = useSingleResultStore($pinia)
    try {
      await singleResultStore.fetch(IMAGE, imageId)
    } catch (err) {
      const errorMessage = app.i18n
        .t("error.image-not-found", {
          id: imageId,
        })
        .toString()
      return error({
        statusCode: 404,
        message: errorMessage,
      })
    }
  },
})
</script>
