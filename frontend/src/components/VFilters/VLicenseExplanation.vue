<template>
  <div class="license-explanation w-70 max-w-xs p-6">
    <h5 class="text-base font-semibold">
      <template v-if="isLicense(license)">{{
        $t("filters.licenseExplanation.licenseDefinition")
      }}</template>
      <template v-else>{{
        $t("filters.licenseExplanation.markDefinition", {
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
      :path="`filters.licenseExplanation.more.${
        isLicense(license) ? 'license' : 'mark'
      }`"
      tag="p"
      class="text-sm"
    >
      <template #readMore>
        <VLink :href="`${getLicenseUrl(license)}`">{{
          $t("filters.licenseExplanation.more.readMore")
        }}</VLink>
      </template>
      <template #mark>{{ license.toUpperCase() }}</template>
    </i18n>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import { getLicenseUrl, isLicense } from "~/utils/license"

import type { License } from "~/constants/license"

import VLicenseElements from "~/components/VLicense/VLicenseElements.vue"
import VLink from "~/components/VLink.vue"

/**
 * Renders the explanation of the license passed to it by breaking it down to
 * its constituent clauses.
 */
export default defineComponent({
  name: "VLicenseExplanation",
  components: {
    VLicenseElements,
    VLink,
  },
  props: {
    /**
     * the code of the license whose elements need to be explained
     */
    license: {
      type: String as PropType<License>,
      required: true,
    },
  },
  setup() {
    return {
      isLicense,
      getLicenseUrl,
    }
  },
})
</script>
