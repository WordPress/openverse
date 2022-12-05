<template>
  <div class="media-attribution">
    <h3 class="description-bold md:heading-6 mb-4">
      {{ headerText }}
    </h3>

    <template v-if="isLicense">
      <i18n
        path="media-details.reuse.attribution"
        tag="span"
        class="mb-2 block text-sm md:mb-4 md:text-base"
      >
        <template #link>
          <VLink :href="licenseUrl">
            {{ fullLicenseName }}
          </VLink>
        </template>
      </i18n>
      <VLicenseElements :license="license" />
    </template>

    <template v-else>
      <VLicenseElements :license="license" />
      <i18n
        path="media-details.reuse.tool.content"
        tag="span"
        class="description-bold"
      >
        <template #link>
          <VLink
            :aria-label="$t('media-details.aria.attribution.tool')"
            :href="licenseUrl"
            >{{ $t('media-details.reuse.tool.link') }}</VLink
          >
        </template>
      </i18n>
    </template>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import { getFullLicenseName, isLicense as isLicenseFn } from '~/utils/license'
import { useI18n } from '~/composables/use-i18n'

import type { License, LicenseVersion } from '~/constants/license'

import VLicenseElements from '~/components/VLicense/VLicenseElements.vue'
import VLink from '~/components/VLink.vue'

export default defineComponent({
  name: 'VMediaLicense',
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
    const i18n = useI18n()
    const isLicense = computed(() => isLicenseFn(props.license))
    const headerText = computed(() => {
      const licenseOrTool = isLicense.value ? 'license' : 'tool'
      return i18n.t(`media-details.reuse.${licenseOrTool}-header`)
    })
    const fullLicenseName = computed(() =>
      getFullLicenseName(props.license, props.licenseVersion, i18n)
    )
    return {
      isLicense,
      headerText,
      fullLicenseName,
    }
  },
})
</script>
