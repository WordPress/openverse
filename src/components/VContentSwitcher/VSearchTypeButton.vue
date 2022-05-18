<template>
  <VButton
    class="flex flex-row font-semibold py-2 text-sr md:text-base"
    :class="[
      sizeClasses,
      isHeaderScrolled ? 'max-w-[10rem] sm:max-w-[20rem] md:max-w-[16rem]' : '',
    ]"
    :variant="buttonVariant"
    size="disabled"
    :aria-label="buttonLabel"
    v-bind="a11yProps"
    @click="$emit('click')"
  >
    <VIcon :icon-path="icon" />
    <span
      class="md:block md:ms-2 md:truncate md:text-left"
      :class="isHeaderScrolled ? 'hidden' : 'block ms-2 truncate text-left'"
      >{{ buttonLabel }}</span
    >
    <VIcon
      class="hidden md:block text-dark-charcoal-40 md:ms-2"
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

import { ALL_MEDIA, SearchType } from '~/constants/media'
import useSearchType from '~/composables/use-search-type'
import { useI18n } from '~/composables/use-i18n'
import { isMinScreen } from '~/composables/use-media-query'

import VIcon from '~/components/VIcon/VIcon.vue'
import VButton from '~/components/VButton.vue'

import caretDownIcon from '~/assets/icons/caret-down.svg'

export default defineComponent({
  name: 'VSearchTypeButton',
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
    const isHeaderScrolled = inject('isHeaderScrolled', ref(null))
    const isMinScreenMd = isMinScreen('md', { shouldPassInSSR: true })

    const { icons, activeType: activeItem } = useSearchType()
    const isIconButton = computed(
      () => isHeaderScrolled?.value && !isMinScreenMd.value
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

    const buttonVariant = computed(() => {
      if (props.type === 'searchbar') {
        return 'action-menu'
      } else {
        return isMinScreenMd.value && !isHeaderScrolled?.value
          ? 'tertiary'
          : 'action-menu'
      }
    })
    const buttonLabel = computed(() => {
      const labelKey = {
        image: 'search-type.image',
        audio: 'search-type.audio',
        all: 'search-type.all',
        video: 'search-type.video',
        model_3d: 'search-type.model_3d',
      }[props.activeItem]
      return i18n.t(labelKey)
    })

    return {
      buttonVariant,
      sizeClasses,
      buttonLabel,
      caretDownIcon,
      isHeaderScrolled,
      isMinScreenMd,
      icon: computed(() => icons[activeItem.value]),
    }
  },
})
</script>
