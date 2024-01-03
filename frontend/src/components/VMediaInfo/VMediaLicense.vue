<template>
  <div class="media-attribution">
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

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { getFullLicenseName, isLicense as isLicenseFn } from "~/utils/license"
import { useNuxtI18n } from "~/composables/use-i18n"
import { useAnalytics } from "~/composables/use-analytics"

import type { License, LicenseVersion } from "~/constants/license"

import VLicenseElements from "~/components/VLicense/VLicenseElements.vue"
import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "VMediaLicense",
  components: { VLicenseElements, VLink },
  props: {
    license: {
      type: String as PropType<License>,
      required: true,
    },
    licenseVersion: {
      type: String as PropType<LicenseVersion>,
      required: true,
    },
    licenseUrl: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const i18n = useNuxtI18n()
    const { sendCustomEvent } = useAnalytics()

    const isLicense = computed(() => isLicenseFn(props.license))
    const headerText = computed(() => {
      const licenseOrTool = isLicense.value ? "license" : "tool"
      return i18n.t(`mediaDetails.reuse.${licenseOrTool}Header`)
    })
    const fullLicenseName = computed(() =>
      getFullLicenseName(props.license, props.licenseVersion, i18n)
    )

    const sendVisitLicensePage = () => {
      sendCustomEvent("VISIT_LICENSE_PAGE", {
        license: props.license,
      })
    }

    return {
      isLicense,
      headerText,
      fullLicenseName,

      sendVisitLicensePage,
    }
  },
})
</script>
