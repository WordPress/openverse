<template>
  <VButton
    v-bind="$attrs"
    :aria-label="$t('search.search')"
    size="disabled"
    :variant="isIcon ? 'plain' : 'primary'"
    class="heading-6 flex-shrink-0 transition-none rounded-s-none hover:bg-pink hover:text-white focus-visible:ring focus-visible:ring-pink group-hover:border-pink group-hover:bg-pink group-hover:text-white"
    :class="[
      isIcon
        ? 'search-button ps-[1.5px] p-[0.5px] focus-visible:bg-pink focus-visible:text-white'
        : 'h-full whitespace-nowrap py-6 px-10',
      sizeClasses,
      route === 'home'
        ? 'border-b border-tx border-b-pink bg-pink text-white'
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
import type { FieldSize } from '~/components/VInputFieldOld/VInputFieldOld.vue'

import searchIcon from '~/assets/icons/search.svg'

export default defineComponent({
  name: 'VSearchButtonOld',
  components: { VIcon, VButton },
  inheritAttrs: false,
  props: {
    size: {
      type: String as PropType<FieldSize>,
      required: true,
    },
    route: {
      type: String as PropType<'home' | '404'>,
      validator: (v: string) => ['home', '404'].includes(v),
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
        props.route === '404' ||
        props.size !== 'standalone' ||
        (props.size === 'standalone' && !currentIsMinScreenMd)
      )
    })

    const sizeClasses = computed(() => {
      return isIcon.value
        ? {
            small: 'w-10 md:w-12 h-10 md:h-12',
            medium: 'w-12 h-12',
            large: 'w-14 h-14',
            standalone: 'w-[57px] md:w-[69px] h-full',
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
}
</style>
