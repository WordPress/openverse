<template>
  <div ref="nodeRef" class="flex justify-center">
    <div
      ref="triggerContainerRef"
      class="flex items-stretch"
      @click="onTriggerClick"
    >
      <VContentSwitcherButton
        :a11y-props="triggerA11yProps"
        :active-item="activeItem"
      />
    </div>
    <VMobileModalContent
      :visible="visibleRef"
      :trigger-element="triggerRef"
      :hide="close"
      :aria-label="$t('header.filter-button.simple')"
    >
      <nav class="p-6" aria-labelledby="content-switcher-heading">
        <h2
          id="content-switcher-heading"
          class="md:sr-only text-sr pb-4 uppercase font-semibold"
        >
          {{ $t('search-type.heading') }}
        </h2>
        <VContentTypes
          :bordered="false"
          :active-item="content.activeType.value"
          @select="selectItem"
        />
        <VPageList layout="columns" class="mt-10" />
      </nav>
    </VMobileModalContent>
  </div>
</template>

<script>
import { onMounted, reactive, ref, watch } from '@nuxtjs/composition-api'
import { useBodyScrollLock } from '~/composables/use-body-scroll-lock'
import useContentType from '~/composables/use-content-type'
import usePages from '~/composables/use-pages'

import externalLinkIcon from 'assets/icons/external-link.svg'

import VMobileModalContent from '~/components/VModal/VMobileModalContent.vue'
import VContentTypes from '~/components/VContentSwitcher/VContentTypes.vue'
import VPageList from '~/components/VHeader/VPageMenu/VPageList.vue'
import VContentSwitcherButton from '~/components/VContentSwitcher/VContentSwitcherButton'

const externalLinkProps = { as: 'a', target: '_blank', rel: 'noopener' }

export default {
  name: 'VMobileContentSwitcher',
  components: {
    VMobileModalContent,
    VContentTypes,
    VPageList,
    VContentSwitcherButton,
  },
  props: {
    activeItem: {
      type: String,
      required: true,
    },
  },
  setup(_, { emit }) {
    const content = useContentType()
    const pages = usePages()

    const modalRef = ref(null)
    const triggerContainerRef = ref(null)

    const closeMenu = () => close()

    const visibleRef = ref(false)
    const nodeRef = ref(null)

    const triggerA11yProps = reactive({
      'aria-expanded': false,
      'aria-haspopup': 'dialog',
    })

    const triggerRef = ref()
    onMounted(() => (triggerRef.value = triggerContainerRef.value?.firstChild))

    watch([visibleRef], ([visible]) => {
      triggerA11yProps['aria-expanded'] = visible
    })

    const { lock, unlock } = useBodyScrollLock({ nodeRef })

    const open = () => {
      visibleRef.value = true
      emit('open')
      lock()
    }

    const close = () => {
      visibleRef.value = false
      emit('close')
      unlock()
    }

    const onTriggerClick = () => {
      if (visibleRef.value === true) {
        close()
      } else {
        open()
      }
    }
    const selectItem = (item) => {
      emit('select', item)
    }

    const isLinkExternal = (item) => !item.link.startsWith('/')
    const getLinkProps = (item) => {
      return isLinkExternal(item)
        ? { ...externalLinkProps, href: item.link }
        : { as: 'NuxtLink', to: item.link }
    }
    return {
      getLinkProps,
      isLinkExternal,
      externalLinkIcon,
      pages,
      content,
      close,
      modalRef,
      nodeRef,
      triggerContainerRef,
      closeMenu,

      triggerRef,
      onTriggerClick,

      triggerA11yProps,
      visibleRef,
      selectItem,
    }
  },
}
</script>
