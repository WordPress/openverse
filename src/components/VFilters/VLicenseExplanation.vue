<template>
  <div class="license-explanation w-full max-w-xs p-6">
    <h5 class="text-base font-semibold">
      <template v-if="isTechnicallyLicense">{{
        $t('filters.license-explanation.license-definition')
      }}</template>
      <template v-else>{{
        $t('filters.license-explanation.mark-definition', {
          mark: license.toUpperCase(),
        })
      }}</template>
    </h5>

    <VLicenseElements
      v-if="license"
      size="small"
      class="my-4"
      :license="license"
    />

    <i18n
      :path="`filters.license-explanation.more.${
        isTechnicallyLicense ? 'license' : 'mark'
      }`"
      tag="p"
      class="text-sm"
    >
      <template #read-more>
        <VLink :href="`${getLicenseDeedLink(license)}`">{{
          $t('filters.license-explanation.more.read-more')
        }}</VLink>
      </template>
      <template #mark>{{ license.toUpperCase() }}</template>
    </i18n>
  </div>
</template>

<script>
import { isLicense } from '~/utils/license'

import { DEPRECATED_LICENSES } from '~/constants/license'

import VLicenseElements from '~/components/VLicenseElements.vue'
import VLink from '~/components/VLink.vue'

/**
 * Renders the explanation of the license passed to it by breaking it down to
 * its constituent clauses.
 */
export default {
  name: 'VLicenseExplanation',
  components: {
    VLicenseElements,
    VLink,
  },
  props: {
    /**
     * the code of the license whose elements need to be explained
     */
    license: {
      type: String,
      required: true,
    },
  },
  computed: {
    /**
     * Public domain marks such as CC0 and PDM are not technically licenses.
     * @return {boolean} true if the license is not CC0 or PDM, false otherwise
     */
    isTechnicallyLicense() {
      return isLicense(this.license)
    },
  },
  methods: {
    getLicenseDeedLink(licenseTerm) {
      let fragment
      if (licenseTerm === 'cc0') {
        fragment = 'publicdomain/zero/1.0'
      } else if (licenseTerm === 'pdm') {
        fragment = 'publicdomain/mark/1.0'
      } else if (DEPRECATED_LICENSES.includes(licenseTerm)) {
        fragment = `licenses/${licenseTerm}/1.0`
      } else {
        fragment = `licenses/${licenseTerm}/4.0`
      }
      return `https://creativecommons.org/${fragment}/?ref=openverse`
    },
  },
}
</script>
