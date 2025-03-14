<script setup lang="ts">
import { useI18n, useNuxtApp } from "#imports"
import { computed } from "vue"

import type { License, LicenseVersion } from "#shared/constants/license"
import {
  getFullLicenseName,
  isLicense as isLicenseFn,
} from "#shared/utils/license"

import VLicenseElements from "~/components/VLicense/VLicenseElements.vue"
import VLink from "~/components/VLink.vue"

const props = defineProps<{
  license: License
  licenseVersion: LicenseVersion
  licenseUrl: string
}>()

const { t } = useI18n({ useScope: "global" })
const { $sendCustomEvent } = useNuxtApp()

const isLicense = computed(() => isLicenseFn(props.license))
const headerText = computed(() => {
  const licenseOrTool = isLicense.value ? "license" : "tool"
  return t(`mediaDetails.reuse.${licenseOrTool}Header`)
})
const fullLicenseName = computed(() =>
  getFullLicenseName(props.license, props.licenseVersion, t)
)

const sendVisitLicensePage = () => {
  $sendCustomEvent("VISIT_LICENSE_PAGE", {
    license: props.license,
  })
}
</script>

<template>
  <div class="media-attribution mb-2 md:mb-0">
    <h3 class="description-bold md:heading-6 mb-4">
      {{ headerText }}
    </h3>

    <template v-if="isLicense">
      <i18n-t
        scope="global"
        keypath="mediaDetails.reuse.attribution"
        tag="span"
        class="mb-2 block text-sm md:mb-4 md:text-base"
      >
        <template #link>
          <VLink
            :href="licenseUrl"
            :send-external-link-click-event="false"
            @click="sendVisitLicensePage"
          >
            {{ fullLicenseName }}
          </VLink>
        </template>
      </i18n-t>
      <VLicenseElements :license="license" />
    </template>

    <template v-else>
      <VLicenseElements :license="license" />
      <i18n-t
        scope="global"
        keypath="mediaDetails.reuse.tool.content"
        tag="span"
        class="description-bold"
      >
        <template #link>
          <VLink
            :aria-label="$t('mediaDetails.aria.attribution.tool')"
            :href="licenseUrl"
            :send-external-link-click-event="false"
            @click="sendVisitLicensePage"
            >{{ $t("mediaDetails.reuse.tool.link") }}</VLink
          >
        </template>
      </i18n-t>
    </template>
  </div>
</template>
