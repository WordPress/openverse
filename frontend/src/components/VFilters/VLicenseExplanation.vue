<template>
  <div class="license-explanation w-70 max-w-xs p-6">
    <h5 class="text-base font-semibold">
      <template v-if="isLicense(license)">{{
        t("filters.licenseExplanation.licenseDefinition")
      }}</template>
      <template v-else>{{
        t("filters.licenseExplanation.markDefinition", {
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
          t("filters.licenseExplanation.more.readMore")
        }}</VLink>
      </template>
      <template #mark>{{ license.toUpperCase() }}</template>
    </i18n-t>
  </div>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { getLicenseUrl, isLicense } from "~/utils/license"

import type { License } from "~/constants/license"

import VLicenseElements from "~/components/VLicense/VLicenseElements.vue"
import VLink from "~/components/VLink.vue"

/**
 * Renders the explanation of the license passed to it by breaking it down to
 * its constituent clauses.
 */

defineProps<{
  /**
   * the code of the license whose elements need to be explained
   */
  license: License
}>()

const {
  $i18n: { t },
} = useNuxtApp()
</script>
