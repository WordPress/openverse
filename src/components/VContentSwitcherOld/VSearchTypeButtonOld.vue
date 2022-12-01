<template>
  <VButton
    class="group flex flex-row py-2 text-sr font-semibold md:text-base"
    :class="[
      sizeClasses,
      {
        'max-w-[10rem] sm:max-w-[20rem] md:max-w-[16rem]': isHeaderScrolled,
        'focus-visible:border-tx focus-visible:bg-white focus-visible:ring-offset-dark-charcoal-06 group-hover:border-dark-charcoal-20 group-hover:bg-white group-hover:focus-within:border-tx':
          isInSearchBar && !isPressed,
      },
    ]"
    :variant="buttonVariant"
    size="disabled"
    :aria-label="buttonLabel"
    v-bind="a11yProps"
    @click="$emit('click')"
  >
    <VIcon :icon-path="icon" />
    <span
      class="md:block md:truncate md:ms-2 md:text-start"
      :class="isHeaderScrolled ? 'hidden' : 'block truncate ms-2 text-start'"
      >{{ buttonLabel }}</span
    >
    <VIcon
      class="hidden text-dark-charcoal-40 md:block md:ms-2"
      :icon-path="caretDownIcon"
    />
  </VButton>
</template>
<script lang="ts">
import {
  computed,
  defineComponent,
  inject,
  PropType,
  ref,
} from '@nuxtjs/composition-api'

import { ALL_MEDIA, type SearchType } from '~/constants/media'
import type { ButtonVariant } from '~/types/button'

import useSearchType from '~/composables/use-search-type'
import { useUiStore } from '~/stores/ui'

import { useI18n } from '~/composables/use-i18n'

import VIcon from '~/components/VIcon/VIcon.vue'
import VButton from '~/components/VButton.vue'

import caretDownIcon from '~/assets/icons/caret-down.svg'

export default defineComponent({
  name: 'VSearchTypeButtonOld',
  components: { VButton, VIcon },
  props: {
    a11yProps: {
      type: Object,
      required: true,
    },
    activeItem: {
      type: String as PropType<SearchType>,
      default: ALL_MEDIA,
    },
    type: {
      type: String as PropType<'header' | 'searchbar'>,
      default: 'header',
    },
  },
  setup(props) {
    const i18n = useI18n()

    const uiStore = useUiStore()

    const isHeaderScrolled = inject('isHeaderScrolled', ref(false))

    const isDesktopLayout = computed(() => uiStore.isDesktopLayout)

    const { icons, activeType: activeItem } = useSearchType()
    const isIconButton = computed(
      () => isHeaderScrolled.value && !isDesktopLayout.value
    )
    const sizeClasses = computed(() => {
      if (props.type === 'searchbar') {
        return 'h-12 px-2'
      } else if (isIconButton.value) {
        return 'w-10 h-10'
      } else {
        /**
          When there is a caret down icon (on 'md' screens), paddings are balanced,
          without it, paddings need to be adjusted.
          */
        return 'ps-2 pe-3 md:px-2'
      }
    })

    const buttonVariant = computed<ButtonVariant>(() => {
      if (props.type === 'searchbar') {
        return 'action-menu'
      } else {
        return isDesktopLayout.value && !isHeaderScrolled.value
          ? 'action-menu-bordered'
          : 'action-menu'
      }
    })
    const buttonLabel = computed(() => {
      return i18n.t(`search-type.${props.activeItem}`)
    })

    const isInSearchBar = computed(() => props.type === 'searchbar')
    const isPressed = computed(() => Boolean(props.a11yProps['aria-expanded']))

    return {
      buttonVariant,
      sizeClasses,
      buttonLabel,

      isHeaderScrolled,
      isInSearchBar,
      isPressed,

      icon: computed(() => icons[activeItem.value]),
      caretDownIcon,
    }
  },
})
</script>
