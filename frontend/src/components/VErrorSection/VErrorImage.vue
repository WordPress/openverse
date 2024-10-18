<script setup lang="ts">
import { useI18n } from "#imports"

import { computed } from "vue"

import type { License, LicenseVersion } from "~/constants/license"
import { AttributableMedia, getAttribution } from "~/utils/attribution-html"

import imageInfo from "~/assets/error_images.json"

interface ErrorImage extends AttributableMedia {
  src: string
  alt: string
}

/**
 * Displays a sad image to convey the negative outcome such as absence of
 * results or a server error.
 */
const props = defineProps<{
  /**
   * the code of the error, used to identify and render the appropriate image
   */
  errorCode: "NO_RESULT" | "SERVER_TIMEOUT"
}>()

const i18n = useI18n({ useScope: "global" })

const images = Object.fromEntries(
  imageInfo.errors.map((errorItem) => {
    const image = errorItem.image
    const errorImage: ErrorImage = {
      ...image,
      originalTitle: image.title,
      src: `/error_images/${image.file}.jpg`,
      alt: `errorImages.${image.id}`,
      license: image.license as License,
      license_version: image.license_version as LicenseVersion,
      frontendMediaType: "image",
    }
    errorImage.attribution = getAttribution(errorImage, i18n)
    return [errorItem.error, errorImage]
  })
)
const image = computed(() => images[props.errorCode])
</script>

<template>
  <figure class="error-image">
    <img :src="image.src" :alt="$t(image.alt)" :title="$t(image.alt)" />
    <!-- Disable reason: We control the attribution HTML generation so this is safe and will not lead to XSS attacks -->
    <!-- eslint-disable-next-line vue/no-v-html -->
    <figcaption class="attribution" v-html="image.attribution" />
  </figure>
</template>

<style scoped>
::v-deep(.attribution) {
  @apply mt-4 text-sr text-secondary;
}
::v-deep(.attribution a) {
  @apply text-current underline;
}
/* license icons should match the text color */
::v-deep(.attribution img) {
  @apply opacity-70;
}
</style>
