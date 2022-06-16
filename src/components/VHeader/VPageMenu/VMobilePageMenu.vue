<template>
  <div ref="nodeRef" class="flex justify-center">
    <!-- eslint-disable vuejs-accessibility/click-events-have-key-events -->
    <div
      ref="triggerContainerRef"
      class="flex items-stretch flex-shrink-0"
      @click="onTriggerClick"
    >
      <!-- eslint-enable vuejs-accessibility/click-events-have-key-events -->
      <VPageMenuButton :a11y-props="triggerA11yProps" />
    </div>
    <VModalContent
      :visible="visibleRef"
      :trigger-element="triggerRef"
      :hide="close"
      :aria-label="$t('header.filter-button.simple')"
    >
      <nav class="p-4">
        <VPageList layout="columns" @click="closeMenu" />
      </nav>
    </VModalContent>
  </div>
</template>

<script>
import {
  computed,
  defineComponent,
  reactive,
  ref,
  watch,
} from '@nuxtjs/composition-api'

import { useBodyScrollLock } from '~/composables/use-body-scroll-lock'

import VModalContent from '~/components/VModal/VModalContent.vue'
import VPageMenuButton from '~/components/VHeader/VPageMenu/VPageMenuButton.vue'
import VPageList from '~/components/VHeader/VPageMenu/VPageList.vue'

export default defineComponent({
  name: 'VMobilePageMenu',
  components: { VModalContent, VPageMenuButton, VPageList },
  setup(_, { emit }) {
    const modalRef = ref(null)

    const closeMenu = () => close()

    const visibleRef = ref(false)
    const nodeRef = ref(null)

    const triggerA11yProps = reactive({
      'aria-expanded': false,
      'aria-haspopup': 'dialog',
    })

    const triggerRef = computed(() => nodeRef.value?.firstChild.firstChild)

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

    return {
      close,
      modalRef,
      nodeRef,
      closeMenu,

      triggerRef,
      onTriggerClick,

      triggerA11yProps,
      visibleRef,
    }
  },
})
</script>
