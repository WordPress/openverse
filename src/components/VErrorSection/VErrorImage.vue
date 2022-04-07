<template>
  <figure class="error-image">
    <img :src="image.src" :alt="$t(image.alt)" :title="$t(image.alt)" />
    <!-- Disable reason: We control the attribution HTML generation so this is safe and will not lead to XSS attacks -->
    <!-- eslint-disable-next-line vue/no-v-html -->
    <figcaption class="attribution" v-html="image.attribution" />
  </figure>
</template>

<script>
import { computed } from '@nuxtjs/composition-api'

import { errorCodes } from '~/constants/errors'
import { getAttribution } from '~/utils/attribution-html'

import imageInfo from '~/assets/error_images/image_info.json'

/**
 * Displays a sad image to convey the absence of results for a search term.
 */
export default {
  name: 'VErrorImage',
  props: {
    errorCode: {
      type: String,
      required: true,
      validator: (val) => errorCodes.includes(val),
    },
  },
  setup(props) {
    const images = Object.fromEntries(
      imageInfo.errors.map((errorItem) => {
        let image = errorItem.image
        image = {
          ...image,
          src: require(`~/assets/error_images/${image.file}.jpg`),
          alt: `error-images.${image.id}`,
          attribution: getAttribution(image),
        }
        return [errorItem.error, image]
      })
    )
    const image = computed(() => images[props.errorCode])

    return {
      image,
    }
  },
}
</script>

<style scoped>
::v-deep .attribution {
  @apply text-dark-charcoal-70;
}
::v-deep a {
  @apply text-current underline;
}
</style>
