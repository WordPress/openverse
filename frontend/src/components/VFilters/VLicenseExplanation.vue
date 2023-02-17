<template>
  <div class="license-explanation w-70 max-w-xs p-6">
    <h5 class="text-base font-semibold">
      <template v-if="isLicense(license)">{{
        $t("filters.license-explanation.license-definition")
      }}</template>
      <template v-else>{{
        $t("filters.license-explanation.mark-definition", {
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
        isLicense(license) ? 'license' : 'mark'
      }`"
      tag="p"
      class="text-sm"
    >
      <template #read-more>
        <VLink :href="`${getLicenseUrl(license)}`">{{
          $t("filters.license-explanation.more.read-more")
        }}</VLink>
      </template>
      <template #mark>{{ license.toUpperCase() }}</template>
    </i18n>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "@nuxtjs/composition-api"

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
