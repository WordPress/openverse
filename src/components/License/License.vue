<template>
  <div class="license text-dark-charcoal-70">
    <span class="icons text-lg">
      <i v-if="isCC" class="icon mr-px cc-logo" title="CC" /><i
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
      validator: (val) =>
        [
          'by',
          'by-sa',
          'by-nd',
          'by-nc',
          'by-nc-sa',
          'by-nc-nd',
          'cc0',
          'pdm',
        ].includes(val),
    },
  },
  setup(props) {
    const iconNames = {
      by: 'by',
      nc: 'nc',
      nd: 'nd',
      sa: 'sa',
      cc0: 'zero',
      pdm: 'pd',
    }
    const icons = computed(() =>
      props.license.split(/[-\s]/).map((term) => iconNames[term])
    )
    const isCC = computed(() => !['cc0', 'pdm'].includes(props.license))

    return {
      icons,
      isCC,
    }
  },
}
</script>
