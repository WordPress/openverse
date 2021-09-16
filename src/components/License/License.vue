<template>
  <div class="license text-dark-charcoal-70">
    <svg
      v-if="isCC"
      class="h-5 w-5 inline"
      viewBox="0 0 30 30"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <use :href="`${ccLogo}#icon`" />
    </svg>
    <svg
      v-for="(name, index) in icons"
      :key="index"
      class="h-5 w-5 inline"
      viewBox="0 0 30 30"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <use :href="`${svgs[name]}#icon`" />
    </svg>
    <span class="name">
      {{ $t(`license-names.${license}`) }}
    </span>
  </div>
</template>

<script>
import {
  ALL_LICENCES,
  CC_LICENSES,
  LICENSE_ICON_MAPPING,
} from '~/constants/license.js'
import { computed } from '@nuxtjs/composition-api'

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
  name: 'License',
  props: {
    /**
     * the slug of the license
     * @values
     */
    license: {
      type: String,
      required: true,
      validator: (val) => ALL_LICENCES.includes(val),
    },
  },
  setup(props) {
    const icons = computed(() =>
      props.license.split(/[-\s]/).map((term) => LICENSE_ICON_MAPPING[term])
    )
    const isCC = computed(() => CC_LICENSES.includes(props.license))

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
    }
  },
}
</script>
