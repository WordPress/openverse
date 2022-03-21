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

<script>
import { computed, useContext } from '@nuxtjs/composition-api'

import { ALL_LICENSES } from '~/constants/license'

import { isCc, getFullLicenseName } from '~/utils/license'

import VIcon from '~/components/VIcon/VIcon.vue'

import by from '~/assets/licenses/by.svg'
import cc0 from '~/assets/licenses/cc0.svg'
import ccLogo from '~/assets/licenses/cc-logo.svg'
import nc from '~/assets/licenses/nc.svg'
import nd from '~/assets/licenses/nd.svg'
import pdm from '~/assets/licenses/pdm.svg'
import sa from '~/assets/licenses/sa.svg'
import samplingPlus from '~/assets/licenses/sampling-plus.svg'

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

    const isCcLicense = computed(() => isCc(props.license))

    const icons = computed(() => {
      let iconList = props.license.split(/[-\s]/)
      if (isCcLicense.value) iconList = ['ccLogo', ...iconList]
      return iconList
    })

    const licenseName = computed(() => {
      return {
        readable: i18n.t(`license-readable-names.${props.license}`),
        full: getFullLicenseName(props.license, '', i18n),
      }
    })

    return {
      ccLogo,
      svgs: {
        ccLogo,
        by,
        cc0,
        nc,
        nd,
        pdm,
        sa,
        'sampling+': samplingPlus,
      },

      icons,
      isCcLicense,
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
