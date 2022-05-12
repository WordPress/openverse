<template>
  <figure class="error-image">
    <img
      :src="image.src"
      :alt="$t(image.alt).toString()"
      :title="$t(image.alt).toString()"
    />
    <!-- Disable reason: We control the attribution HTML generation so this is safe and will not lead to XSS attacks -->
    <!-- eslint-disable-next-line vue/no-v-html -->
    <figcaption class="attribution" v-html="image.attribution" />
  </figure>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import type { License, LicenseVersion } from '~/constants/license'
import { ErrorCode, errorCodes } from '~/constants/errors'
import { AttributableMedia, getAttribution } from '~/utils/attribution-html'
import { useI18n } from '~/composables/use-i18n'

import imageInfo from '~/assets/error_images/image_info.json'

interface ErrorImage extends AttributableMedia {
  src: string
  alt: string
  attribution?: string
}

/**
 * Displays a sad image to convey the negative outcome such as absence of
 * results or a server error.
 */
export default defineComponent({
  name: 'VErrorImage',
  props: {
    /**
     * the code of the error, used to identify and render the appropriate image
     */
    errorCode: {
      type: String as PropType<ErrorCode>,
      required: true,
      validator: (val: ErrorCode) => errorCodes.includes(val),
    },
  },
  setup(props) {
    const i18n = useI18n()

    const images = Object.fromEntries(
      imageInfo.errors.map((errorItem) => {
        let image = errorItem.image
        const errorImage: ErrorImage = {
          ...image,
          src: require(`~/assets/error_images/${image.file}.jpg`),
          alt: `error-images.${image.id}`,
          license: image.license as License,
          license_version: image.license_version as LicenseVersion,
        }
        errorImage.attribution = getAttribution(errorImage, i18n)
        return [errorItem.error, errorImage]
      })
    )
    const image = computed(() => images[props.errorCode])

    return {
      image,
    }
  },
})
</script>

<style scoped>
::v-deep .attribution {
  @apply text-dark-charcoal-70;
}
::v-deep a {
  @apply text-current underline;
}
::v-deep img {
  @apply opacity-70; /* to match the text color */
}
</style>
