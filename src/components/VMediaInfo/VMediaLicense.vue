<template>
  <div class="media-attribution">
    <h5 class="mb-4 text-base md:text-2xl font-semibold">
      {{ headerText }}
    </h5>

    <template v-if="isLicense">
      <i18n
        path="media-details.reuse.attribution"
        tag="span"
        class="block text-sm md:text-base mb-2"
      >
        <template #link>
          <VLink class="uppercase" :href="licenseUrl">
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
        class="text-sm font-semibold"
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

import { isLicense as isLicenseFn } from '~/utils/license'
import { useI18n } from '~/composables/use-i18n'

import type { License } from '~/constants/license'

import VLicenseElements from '~/components/VLicense/VLicenseElements.vue'
import VLink from '~/components/VLink.vue'

export default defineComponent({
  name: 'VMediaLicense',
  components: { VLicenseElements, VLink },
  props: {
    fullLicenseName: {
      type: String,
      required: true,
    },
    license: {
      type: String as PropType<License>,
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
    return {
      isLicense,
      headerText,
    }
  },
})
</script>
