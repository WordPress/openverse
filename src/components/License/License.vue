<template>
  <div class="license text-dark-charcoal-70">
    <span class="icons text-lg">
      <i v-if="isCC" class="icon mr-1 cc-logo" title="CC" /><i
        v-for="(name, index) in icons"
        :key="index"
        class="icon mr-px"
        :class="`cc-${name}`"
        :title="name.toUpperCase()"
      />
    </span>
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
      icons,
      isCC,
    }
  },
}
</script>
