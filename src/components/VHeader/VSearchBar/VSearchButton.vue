<template>
  <VButton
    v-bind="$attrs"
    :aria-label="$t('search.search')"
    size="disabled"
    :variant="isIcon ? 'plain' : 'primary'"
    class="transition-none flex-shrink-0 rounded-s-none font-semibold text-2xl hover:text-white group-hover:text-white group-hover:border-pink hover:bg-pink group-hover:bg-pink focus-visible:ring focus-visible:ring-pink"
    :class="[
      isIcon
        ? 'search-button focus-visible:bg-pink focus-visible:text-white p-[0.5px] ps-[1.5px]'
        : 'py-6 px-10 whitespace-nowrap h-full',
      sizeClasses,
      isHomeRoute
        ? 'bg-pink border-b border-b-pink text-white border-tx'
        : 'border-dark-charcoal-20',
    ]"
    v-on="$listeners"
  >
    <template v-if="isIcon">
      <VIcon :icon-path="searchIcon" />
    </template>
    <template v-else>
      <span>{{ $t('search.search') }}</span>
    </template>
  </VButton>
</template>

<script lang="ts">
import { defineComponent, computed, PropType } from '@nuxtjs/composition-api'

import { isMinScreen } from '~/composables/use-media-query'
import { useBrowserIsMobile } from '~/composables/use-browser-detection'

import VIcon from '~/components/VIcon/VIcon.vue'
import VButton from '~/components/VButton.vue'
import type { FieldSize } from '~/components/VInputField/VInputField.vue'

import searchIcon from '~/assets/icons/search.svg'

export default defineComponent({
  name: 'VSearchButton',
  components: { VIcon, VButton },
  inheritAttrs: false,
  props: {
    size: {
      type: String as PropType<FieldSize>,
      required: true,
    },
    isHomeRoute: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const isMobile = useBrowserIsMobile()
    const isMinScreenMd = isMinScreen('md', { shouldPassInSSR: !isMobile })
    const isIcon = computed(() => {
      // split the evaluation of the isMinScreenMd ref
      // out to prevent short-circuiting from creating
      // problems with `computed`'s dependency detection
      const currentIsMinScreenMd = isMinScreenMd.value

      return (
        props.size !== 'standalone' ||
        (props.size === 'standalone' && !currentIsMinScreenMd)
      )
    })

    const sizeClasses = computed(() => {
      return isIcon
        ? {
            small: ['w-10', 'md:w-12', 'h-10', 'md:h-12'],
            medium: ['w-12', 'h-12'],
            large: ['w-14', 'h-14'],
            standalone: ['w-14', 'md:w-auto', 'h-full'],
          }[props.size]
        : undefined
    })

    return { isMinScreenMd, searchIcon, sizeClasses, isIcon }
  },
})
</script>

<style scoped>
.search-button {
  /* Negative margin removes a tiny gap between the button and the input borders */
  margin-inline-start: -1px;
  border-inline-start-color: transparent;
  border-width: 1px;
}
.search-button.search-button:not(:hover):not(:focus):not(:focus-within) {
  border-inline-start-color: transparent;
  border-width: 1px;
}
.search-button.search-button:hover {
  border-inline-start-color: rgba(214, 212, 213, 1);
  border-width: 1px;
}
</style>
