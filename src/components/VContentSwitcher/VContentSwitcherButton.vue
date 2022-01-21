<template>
  <VButton
    class="flex flex-row font-semibold px-3 py-2 text-sr md:text-base"
    :class="{ 'w-12': isIconButton }"
    :variant="buttonVariant"
    size="disabled"
    :aria-label="buttonLabel"
    v-bind="a11yProps"
    @click="$emit('click')"
  >
    <VIcon :icon-path="icon" />
    <span v-show="showLabel" :class="{ 'ms-2': showLabel }">{{
      buttonLabel
    }}</span>
    <VIcon
      class="hidden md:block text-dark-charcoal-40 md:ms-2"
      :icon-path="caretDownIcon"
    />
  </VButton>
</template>
<script>
import { ALL_MEDIA, AUDIO, IMAGE } from '~/constants/media'
import { computed, inject, useContext } from '@nuxtjs/composition-api'
import useContentType from '~/composables/use-content-type'
import { isMinScreen } from '~/composables/use-media-query'

import caretDownIcon from '~/assets/icons/caret-down.svg'

import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'

export default {
  name: 'VContentSwitcherButton',
  components: { VButton, VIcon },
  props: {
    a11yProps: {
      type: Object,
      required: true,
    },
    activeItem: {
      type: String,
      default: ALL_MEDIA,
      validator: (val) => [ALL_MEDIA, IMAGE, AUDIO].includes(val),
    },
  },
  setup(props) {
    const { i18n } = useContext()
    const isHeaderScrolled = inject('isHeaderScrolled', null)
    const isMinScreenMd = isMinScreen('md', { shouldPassInSSR: true })

    const { icons, activeType: activeItem } = useContentType()
    const isIconButton = computed(
      () => isHeaderScrolled?.value && !isMinScreenMd.value
    )
    const buttonVariant = computed(() => {
      return isMinScreenMd.value && !isHeaderScrolled?.value
        ? 'tertiary'
        : 'action-menu'
    })
    const buttonLabel = computed(() => {
      const labelKey = {
        image: 'search-type.image',
        audio: 'search-type.audio',
        all: 'search-type.all',
        video: 'search-type.video',
      }[props.activeItem]
      return i18n.t(labelKey)
    })
    const showLabel = computed(
      () => isMinScreenMd.value || !isHeaderScrolled?.value
    )

    return {
      buttonVariant,
      isIconButton,
      buttonLabel,
      caretDownIcon,
      showLabel,
      isHeaderScrolled,
      isMinScreenMd,
      icon: computed(() => icons[activeItem.value]),
    }
  },
}
</script>
