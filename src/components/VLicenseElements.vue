<template>
  <ul>
    <li
      v-for="element in elements"
      :key="element"
      class="flex items-center gap-3 mt-2"
    >
      <VIcon
        view-box="0 0 30 30"
        :size="isSmall ? 5 : 6"
        :icon-path="icons[element]"
      />
      <span v-if="elements.length > 1" class="sr-only">{{
        element.toUpperCase()
      }}</span>
      <p :class="{ 'text-sm': isSmall }">
        {{ $t(`browse-page.license-description.${element}`) }}
      </p>
    </li>
  </ul>
</template>

<script>
import { computed, defineComponent } from '@nuxtjs/composition-api'

import by from '~/assets/licenses/by.svg'
import cc0 from '~/assets/licenses/cc0.svg'
import nc from '~/assets/licenses/nc.svg'
import nd from '~/assets/licenses/nd.svg'
import pdm from '~/assets/licenses/pdm.svg'
import sa from '~/assets/licenses/sa.svg'
import sampling from '~/assets/licenses/sampling.svg'
import samplingPlus from '~/assets/licenses/sampling-plus.svg'

export default defineComponent({
  name: 'VLicenseElements',
  props: {
    license: {
      type: String,
      required: true,
    },
    size: {
      type: String,
      default: 'big',
      validator: (val) => ['big', 'small'].includes(val),
    },
  },
  setup(props) {
    const elements = computed(() => props.license.split('-'))

    const isSmall = computed(() => props.size === 'small')

    return {
      icons: {
        by,
        nc,
        nd,
        sa,
        cc0,
        pdm,
        sampling,
        'sampling+': samplingPlus,
      },
      elements,
      isSmall,
    }
  },
})
</script>
