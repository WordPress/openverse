<template>
  <div class="license flex flex-row items-center gap-2">
    <div class="flex gap-1">
      <VIcon
        v-for="(name, index) in icons"
        :key="index"
        :class="['icon', bgFilled ? 'bg-filled text-black' : '']"
        view-box="0 0 30 30"
        :icon-path="svgs[name]"
        :size="4"
      />
    </div>
    <span v-show="!hideName" class="name" :aria-label="licenseName.readable">
      {{ licenseName.full }}
    </span>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  PropType,
  useContext,
} from '@nuxtjs/composition-api'

import { ALL_LICENSES, License, licenseIcons } from '~/constants/license'

import { isCc, getFullLicenseName, licenseToElements } from '~/utils/license'

import VIcon from '~/components/VIcon/VIcon.vue'

import ccLogo from '~/assets/licenses/cc-logo.svg'

/**
 * Displays the icons for the license along with a readable display name for the
 * license.
 */
export default defineComponent({
  name: 'VLicense',
  components: { VIcon },
  props: {
    /**
     * the slug of the license
     * @values
     */
    license: {
      type: String as PropType<License>,
      required: true,
      validator: (val: string) => ALL_LICENSES.includes(val as License),
    },
    /**
     * Whether to display icons filled with a white background or leave them transparent.
     */
    bgFilled: {
      type: Boolean,
      default: false,
    },
    /**
     * Either to show the license name next to the icons or hide it.
     */
    hideName: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const { i18n } = useContext()

    const isCcLicense = computed(() => isCc(props.license))

    const icons = computed(() => {
      if (isCcLicense.value) {
        return ['ccLogo', ...licenseToElements(props.license)] as const
      } else {
        return [...licenseToElements(props.license)] as const
      }
    })

    const licenseName = computed(() => {
      return {
        readable: i18n.t(`license-readable-names.${props.license}`).toString(),
        full: getFullLicenseName(props.license, '', i18n),
      }
    })

    return {
      ccLogo,
      svgs: { ...licenseIcons, ccLogo },

      icons,
      isCcLicense,
      licenseName,
    }
  },
})
</script>

<style scoped>
.bg-filled {
  background-image: radial-gradient(circle, #ffffff 60%, transparent 60%);
}
</style>
