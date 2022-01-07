<template>
  <div class="media-attribution">
    <h5 class="b-header mb-6">
      {{ headerText }}
    </h5>
    <template v-if="isLicense">
      <i18n
        path="media-details.reuse.attribution.main"
        tag="span"
        class="block"
      >
        <template #link>
          <a
            class="uppercase"
            :href="licenseUrl"
            target="_blank"
            rel="noopener"
          >
            {{ fullLicenseName }}
          </a>
        </template>
      </i18n>
      <LicenseElements :license="license" />
      <i18n
        v-if="!isLicense"
        path="media-details.reuse.license.content"
        tag="span"
        class="caption font-semibold"
      >
        <template #link>
          <a
            :aria-label="$t('media-details.aria.attribution.license')"
            :href="licenseUrl"
            target="_blank"
            rel="noopener"
          >
            {{ $t('media-details.reuse.license.link') }}
          </a>
        </template>
      </i18n>
    </template>
    <template v-else>
      <LicenseElements :license="license" />
      <i18n
        path="media-details.reuse.tool.content"
        tag="span"
        class="caption font-semibold"
      >
        <template #link>
          <a
            :aria-label="$t('media-details.aria.attribution.tool')"
            :href="licenseUrl"
            target="_blank"
            rel="noopener"
          >
            {{ $t('media-details.reuse.tool.link') }}
          </a>
        </template>
      </i18n>
    </template>
  </div>
</template>

<script>
import { isLicense } from '~/utils/license'
import LicenseElements from '~/components/LicenseElements.vue'

export default {
  name: 'MediaLicense',
  components: {
    LicenseElements,
  },
  props: {
    fullLicenseName: String,
    license: String,
    licenseUrl: String,
  },
  computed: {
    isLicense() {
      return isLicense(this.$props.license)
    },
    headerText() {
      const licenseOrTool = this.isLicense ? 'license' : 'tool'
      return this.$t(`media-details.reuse.${licenseOrTool}-header`)
    },
  },
}
</script>
