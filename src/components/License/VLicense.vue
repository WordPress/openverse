<template>
  <div class="license flex flex-row items-center gap-2">
    <div class="flex gap-1">
      <VIcon
        v-if="isCC"
        :class="['icon', bgFilled ? 'bg-filled text-black' : '']"
        view-box="0 0 30 30"
        :icon-path="ccLogo"
        :size="4"
      />
      <VIcon
        v-for="(name, index) in icons"
        :key="index"
        :class="['icon', bgFilled ? 'bg-filled text-black' : '']"
        view-box="0 0 30 30"
        :icon-path="svgs[name]"
        :size="4"
      />
    </div>
    <span v-if="!hideName" class="name" :aria-label="licenseName.readable">
      {{ licenseName.full }}
    </span>
  </div>
</template>

<script>
import { computed, useContext } from '@nuxtjs/composition-api'

import VIcon from '~/components/VIcon/VIcon.vue'

import {
  ALL_LICENSES,
  CC_LICENSES,
  DEPRECATED_LICENSES,
  LICENSE_ICON_MAPPING,
} from '~/constants/license.js'

import by from '~/assets/licenses/by.svg'
import cc0 from '~/assets/licenses/cc0.svg'
import ccLogo from '~/assets/licenses/cc-logo.svg'
import nc from '~/assets/licenses/nc.svg'
import nd from '~/assets/licenses/nd.svg'
import pdm from '~/assets/licenses/pdm.svg'
import sa from '~/assets/licenses/sa.svg'

/**
 * Displays the icons for the license along with a readable display name for the
 * license.
 */
export default {
  name: 'VLicense',
  components: { VIcon },
  props: {
    /**
     * the slug of the license
     * @values
     */
    license: {
      type: String,
      required: true,
      validator: (val) => ALL_LICENSES.includes(val),
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
    const isDeprecated = computed(() =>
      DEPRECATED_LICENSES.includes(props.license)
    )
    const icons = computed(() => {
      if (isDeprecated.value) {
        return []
      }
      return props.license
        .split(/[-\s]/)
        .map((term) => LICENSE_ICON_MAPPING[term])
    })
    const isCC = computed(
      () => CC_LICENSES.includes(props.license) || props.license === 'cc0'
    )
    /**
     * @type {import('@nuxtjs/composition-api').ComputedRef<{ readable: string, full: string }>}
     */
    const licenseName = computed(() => {
      if (isDeprecated.value) {
        return { readable: props.license, full: props.license }
      } else {
        return {
          readable: i18n.t(`license-readable-names.${props.license}`),
          full: i18n.t(`license-names.${props.license}`),
        }
      }
    })

    return {
      ccLogo,
      svgs: {
        by,
        cc0,
        nc,
        nd,
        pdm,
        sa,
      },

      icons,
      isCC,
      licenseName,
    }
  },
}
</script>

<style scoped>
.bg-filled {
  background-image: radial-gradient(circle, #ffffff 60%, transparent 60%);
}
</style>
