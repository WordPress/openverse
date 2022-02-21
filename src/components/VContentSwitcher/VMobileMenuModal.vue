<template>
  <div ref="nodeRef" class="mobile-menu ms-auto md:ms-0">
    <div ref="triggerContainerRef" @click="onTriggerClick">
      <VSearchTypeButton
        :a11y-props="triggerA11yProps"
        :active-item="activeItem"
        aria-controls="content-switcher-modal"
      />
    </div>
    <VMobileModalContent
      :visible="visibleRef"
      :trigger-element="triggerRef"
      :hide="close"
      :aria-label="$t('header.filter-button.simple')"
      :initial-focus-element="initialFocusElement"
    >
      <nav
        id="content-switcher-modal"
        class="p-6"
        aria-labelledby="content-switcher-heading"
      >
        <VSearchTypes
          ref="searchTypesNode"
          size="small"
          :active-item="content.activeType.value"
          @select="selectItem"
        />
        <VPageList layout="columns" class="mt-10" />
      </nav>
    </VMobileModalContent>
  </div>
</template>

<script>
import {
  computed,
  defineComponent,
  onMounted,
  reactive,
  ref,
  watch,
} from '@nuxtjs/composition-api'
import { useBodyScrollLock } from '~/composables/use-body-scroll-lock'
import useSearchType from '~/composables/use-search-type'
import usePages from '~/composables/use-pages'

import VMobileModalContent from '~/components/VModal/VMobileModalContent.vue'
import VSearchTypes from '~/components/VContentSwitcher/VSearchTypes.vue'
import VPageList from '~/components/VHeader/VPageMenu/VPageList.vue'
import VSearchTypeButton from '~/components/VContentSwitcher/VSearchTypeButton.vue'

export default defineComponent({
  name: 'VMobileContentSwitcher',
  components: {
    VMobileModalContent,
    VSearchTypes,
    VPageList,
    VSearchTypeButton,
  },
  props: {
    activeItem: {
      type: String,
      required: true,
    },
  },
  setup(_, { emit }) {
    const content = useSearchType()
    const pages = usePages()

    /** @type {import('@nuxtjs/composition-api').Ref<import('vue/types/vue').Vue | null>} */
    const searchTypesNode = ref(null)
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

    const initialFocusElement = computed(() =>
      searchTypesNode.value?.$el?.querySelector('[aria-checked="true"]')
    )

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

    return {
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
      initialFocusElement,
      searchTypesNode,
    }
  },
})
</script>
