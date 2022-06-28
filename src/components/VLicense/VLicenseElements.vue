<template>
  <ul>
    <li
      v-for="element in elementNames"
      :key="element"
      class="flex items-center gap-3 mb-2 text-sm md:text-base"
    >
      <VIcon
        view-box="0 0 30 30"
        :size="isSmall ? 5 : 6"
        :icon-path="icons[element]"
      />
      <span v-if="elementNames.length > 1" class="sr-only">{{
        element.toUpperCase()
      }}</span>
      <p :class="{ 'text-sm': isSmall }">
        {{ $t(`browse-page.license-description.${element}`) }}
      </p>
    </li>
  </ul>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import type { License } from '~/constants/license'
import { LICENSE_ICONS } from '~/constants/license'

import { getElements } from '~/utils/license'

import VIcon from '~/components/VIcon/VIcon.vue'

export default defineComponent({
  name: 'VLicenseElements',
  components: { VIcon },
  props: {
    /**
     * the slug of the license
     * @values ALL_LICENSES
     */
    license: {
      type: String as PropType<License>,
      required: true,
    },
    /**
     * the size of the icons and text
     */
    size: {
      type: String as PropType<'big' | 'small'>,
      default: 'big',
    },
  },
  setup(props) {
    const elementNames = computed(() =>
      getElements(props.license).filter((icon) => icon !== 'cc')
    )

    const isSmall = computed(() => props.size === 'small')

    return {
      icons: LICENSE_ICONS,
      elementNames,
      isSmall,
    }
  },
})
</script>
