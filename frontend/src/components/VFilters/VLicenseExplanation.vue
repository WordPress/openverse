<script setup lang="ts">
/**
 * Renders the explanation of the license passed to it by breaking it down to
 * its constituent clauses.
 */
import { getLicenseUrl, isLicense } from "~/utils/license"

import type { License } from "~/constants/license"

import VLicenseElements from "~/components/VLicense/VLicenseElements.vue"
import VLink from "~/components/VLink.vue"

defineProps<{
  /**
   * the code of the license whose elements need to be explained
   */
  license: License
}>()
</script>

<template>
  <div
    class="license-explanation flex flex-col gap-y-4 p-6 pt-0 sm:p-9 sm:pt-0"
  >
    <VLicenseElements size="small" :license="license" />

    <i18n-t
      scope="global"
      :keypath="`filters.licenseExplanation.more.${
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
    </i18n-t>
  </div>
</template>
