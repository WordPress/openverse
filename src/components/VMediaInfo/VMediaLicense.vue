<template>
  <div class="media-attribution">
    <h5 class="mb-4 text-base md:text-2xl font-semibold">
      {{ headerText }}
    </h5>
    <template v-if="isLicense">
      <i18n
        path="media-details.reuse.attribution"
        tag="span"
        class="block text-sm md:text-base"
      >
        <template #link>
          <VLink class="uppercase text-pink" :href="licenseUrl">
            {{ fullLicenseName }}
          </VLink>
        </template>
      </i18n>
      <VLicenseElements v-if="license" :license="license" class="md:py-4" />
      <i18n
        v-if="!isLicense"
        path="media-details.reuse.license.content"
        tag="span"
        class="caption font-semibold"
      >
        <template #link>
          <VLink
            :aria-label="$t('media-details.aria.attribution.license')"
            :href="licenseUrl"
            class="text-pink"
            >{{ $t('media-details.reuse.license.link') }}</VLink
          >
        </template>
      </i18n>
    </template>
    <template v-else>
      <VLicenseElements v-if="license" :license="license" class="md:py-4" />
      <i18n
        path="media-details.reuse.tool.content"
        tag="span"
        class="caption font-semibold"
      >
        <template #link>
          <VLink
            :aria-label="$t('media-details.aria.attribution.tool')"
            :href="licenseUrl"
            class="text-pink"
            >{{ $t('media-details.reuse.tool.link') }}</VLink
          >
        </template>
      </i18n>
    </template>
  </div>
</template>

<script>
import { isLicense } from '~/utils/license'

import VLicenseElements from '~/components/VLicenseElements.vue'
import VLink from '~/components/VLink.vue'

export default {
  name: 'VMediaLicense',
  components: { VLicenseElements, VLink },
  props: {
    fullLicenseName: String,
    license: String,
    licenseUrl: String,
  },
  computed: {
    isLicense() {
      return isLicense(this.license)
    },
    headerText() {
      const licenseOrTool = this.isLicense ? 'license' : 'tool'
      return this.$t(`media-details.reuse.${licenseOrTool}-header`)
    },
  },
}
</script>
