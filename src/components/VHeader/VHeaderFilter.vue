<template>
  <div
    ref="nodeRef"
    class="flex justify-end items-stretch text-sr md:text-base"
  >
    <VFilterButton
      ref="buttonRef"
      class="self-stretch"
      :class="visibleRef ? 'hidden md:flex' : 'flex'"
      :pressed="visibleRef"
      v-bind="triggerA11yProps"
      @toggle="onTriggerClick"
    />
    <Component :is="filterComponent" v-bind="options" @close="onTriggerClick">
      <VSearchGridFilter @close="onTriggerClick" />
    </Component>
  </div>
</template>

<script>
import {
  ref,
  watch,
  reactive,
  computed,
  onMounted,
  useContext,
  inject,
} from '@nuxtjs/composition-api'

import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'
import { useBodyScrollLock } from '~/composables/use-body-scroll-lock'

import VTeleport from '~/components/VTeleport/VTeleport.vue'
import VFilterButton from '~/components/VHeader/VFilterButton.vue'
import VSearchGridFilter from '~/components/VFilters/VSearchGridFilter.vue'
import VSidebarContent from '~/components/VHeader/VSidebarContent.vue'
import VModalContent from '~/components/VModal/VModalContent.vue'

export default {
  name: 'VHeaderFilter',
  components: {
    VFilterButton,
    VSearchGridFilter,
    VSidebarContent,
    VModalContent,
    VTeleport,
  },
  emits: [
    /**
     * Fires when the popover opens, regardless of reason. There are no extra parameters.
     */
    'open',
    /**
     * Fires when the popover closes, regardless of reason. There are no extra parameters.
     */
    'close',
  ],
  setup(_, { emit }) {
    const modalRef = ref(null)
    /** @type { import('@nuxtjs/composition-api').Ref<boolean> } */
    const visibleRef = ref(false)
    const nodeRef = ref(null)

    /** @type { import('@nuxtjs/composition-api').Ref<HTMLElement | undefined> } */
    const buttonRef = ref()
    const filterSidebar = useFilterSidebarVisibility()
    const { i18n } = useContext()
    /** @type { import('@nuxtjs/composition-api').Ref<boolean> } */
    const isMinScreenMd = inject('isMinScreenMd')
    /** @type { import('@nuxtjs/composition-api').Ref<boolean> } */
    const isHeaderScrolled = inject('isHeaderScrolled')

    /** @type { import('@nuxtjs/composition-api').Ref<import('@nuxtjs/composition-api').Component> } */
    const filterComponent = ref(VModalContent)

    const triggerA11yProps = reactive({
      'aria-expanded': false,
      'aria-haspopup': 'dialog',
    })
    const { lock, unlock } = useBodyScrollLock({ nodeRef })

    watch([visibleRef], ([visible]) => {
      triggerA11yProps['aria-expanded'] = visible
      filterSidebar.setVisibility(visible)
      if (!isMinScreenMd) {
        visible ? lock() : unlock()
      }
    })

    const open = () => {
      visibleRef.value = true
      emit('open')
    }

    const close = () => {
      visibleRef.value = false
      emit('close')
    }

    const onTriggerClick = () => {
      if (visibleRef.value === true) {
        close()
      } else {
        open()
      }
    }
    const mobileOptions = {
      visible: visibleRef,
      'trigger-element': computed(() => nodeRef?.value?.firstChild),
      hide: close,
      'aria-label': i18n.t('header.filter-button.simple'),
      mode: 'mobile',
    }

    const desktopOptions = {
      to: 'sidebar',
      visible: visibleRef,
    }
    /**
     * @type { import('@nuxtjs/composition-api').Ref<{
     * 'trigger-element'?: import('@nuxtjs/composition-api').ComputedRef<HTMLElement|null>,
     * hide?: () => {}, visible: import('@nuxtjs/composition-api').Ref<boolean>,
     * 'aria-label': [string], to?: string, mode?: string }> }
     */
    const options = ref(mobileOptions)
    onMounted(() => {
      if (isMinScreenMd.value && filterSidebar.isVisible.value) {
        open()
      }
    })
    watch(
      [isMinScreenMd],
      ([isMinScreenMd]) => {
        if (isMinScreenMd) {
          filterComponent.value = VSidebarContent
          options.value = desktopOptions
        } else {
          filterComponent.value = VModalContent
          options.value = mobileOptions
        }
      },
      { immediate: true }
    )

    return {
      filterComponent,
      modalRef,
      buttonRef,
      isHeaderScrolled,
      nodeRef,
      visibleRef,
      open,
      close,
      onTriggerClick,
      triggerA11yProps,
      isMinScreenMd,
      options,
    }
  },
}
</script>
