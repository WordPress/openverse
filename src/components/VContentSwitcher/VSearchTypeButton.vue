<template>
  <VButton
    class="flex flex-row font-semibold py-2 text-sr md:text-base"
    :class="[
      sizeClasses,
      showLabel ? 'max-w-[10rem] sm:max-w-[20rem] md:max-w-[16rem]' : '',
    ]"
    :variant="buttonVariant"
    size="disabled"
    :aria-label="buttonLabel"
    v-bind="a11yProps"
    @click="$emit('click')"
  >
    <VIcon :icon-path="icon" />
    <span
      v-show="showLabel"
      class="hidden xs:block"
      :class="{ 'ms-2 truncate text-left': showLabel }"
      >{{ buttonLabel }}</span
    >
    <VIcon
      class="hidden md:block text-dark-charcoal-40 md:ms-2"
      :icon-path="caretDownIcon"
    />
  </VButton>
</template>
<script>
import {
  computed,
  defineComponent,
  inject,
  useContext,
} from '@nuxtjs/composition-api'

import { ALL_MEDIA } from '~/constants/media'
import useSearchType from '~/composables/use-search-type'
import { isMinScreen } from '~/composables/use-media-query'
import { isValidSearchType } from '~/utils/prop-validators'

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
      type: String,
      default: ALL_MEDIA,
      validator: isValidSearchType,
    },
    type: {
      type: String,
      default: 'header',
      validator: (v) => ['header', 'searchbar'].includes(v),
    },
  },
  setup(props) {
    const { i18n } = useContext()
    const isHeaderScrolled = inject('isHeaderScrolled', null)
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
    const showLabel = computed(
      () => isMinScreenMd.value || !isHeaderScrolled?.value
    )

    return {
      buttonVariant,
      sizeClasses,
      buttonLabel,
      caretDownIcon,
      showLabel,
      isHeaderScrolled,
      isMinScreenMd,
      icon: computed(() => icons[activeItem.value]),
    }
  },
})
</script>
