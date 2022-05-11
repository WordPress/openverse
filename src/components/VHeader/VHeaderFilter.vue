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
      @tab="onTab"
    />
    <Component
      :is="filterComponent"
      v-bind="options"
      :visible="visibleRef"
      @close="onTriggerClick"
    >
      <VSearchGridFilter @close="onTriggerClick" />
    </Component>
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  ref,
  watch,
  reactive,
  computed,
  onMounted,
  inject,
  Ref,
} from '@nuxtjs/composition-api'

import { useBodyScrollLock } from '~/composables/use-body-scroll-lock'
import { useI18n } from '~/composables/use-i18n'
import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'
import { useFocusFilters } from '~/composables/use-focus-filters'

import { Focus } from '~/utils/focus-management'
import { defineEvent } from '~/types/emits'

import VTeleport from '~/components/VTeleport/VTeleport.vue'
import VFilterButton from '~/components/VHeader/VFilterButton.vue'
import VSearchGridFilter from '~/components/VFilters/VSearchGridFilter.vue'

export default defineComponent({
  name: 'VHeaderFilter',
  components: {
    VFilterButton,
    VSearchGridFilter,
    VTeleport,
  },
  emits: {
    /**
     * Fires when the popover opens, regardless of reason. There are no extra parameters.
     */
    open: defineEvent(),
    /**
     * Fires when the popover closes, regardless of reason. There are no extra parameters.
     */
    close: defineEvent(),
  },
  setup(_, { emit }) {
    const modalRef = ref<HTMLElement | null>(null)
    const nodeRef = ref<HTMLElement | null>(null)
    const buttonRef = ref<HTMLElement | null>(null)

    const visibleRef = ref(false)
    const filterSidebar = useFilterSidebarVisibility()
    const i18n = useI18n()

    const isMinScreenMd: Ref<boolean> = inject('isMinScreenMd', ref(true))
    const isHeaderScrolled: Ref<boolean> = inject(
      'isHeaderScrolled',
      ref(false)
    )

    const filterComponent = ref('VModalContent')

    const triggerA11yProps = reactive({
      'aria-expanded': false,
      'aria-haspopup': 'dialog',
    })
    const { lock, unlock } = useBodyScrollLock({ nodeRef })

    watch([visibleRef], ([visible]) => {
      triggerA11yProps['aria-expanded'] = visible
      filterSidebar.setVisibility(visible)
    })

    const open = () => {
      visibleRef.value = true
      emit('open')
      if (!isMinScreenMd.value) {
        lock()
      }
    }

    const close = () => {
      visibleRef.value = false
      emit('close')
      if (!isMinScreenMd.value) {
        unlock()
      }
    }

    const onTriggerClick = () => {
      visibleRef.value === true ? close() : open()
    }
    const focusFilters = useFocusFilters()
    /**
     * Focus the first element in the sidebar when navigating from the VFilterButton
     * using keyboard `Tab` key.
     */
    const onTab = (event: KeyboardEvent) => {
      focusFilters.focusFilterSidebar(event, Focus.First)
    }

    type MobileFilterOptions = {
      'aria-label': string
      hide: () => void
    }
    type DesktopFilterOptions = {
      to: string
    }

    const mobileOptions = {
      triggerElement: computed(() =>
        nodeRef.value?.firstChild
          ? (nodeRef.value?.firstChild as HTMLElement)
          : null
      ),
      'aria-label': i18n.t('header.filter-button.simple'),
      hide: close,
    }

    const desktopOptions = {
      to: 'sidebar',
    }

    const options: Ref<MobileFilterOptions | DesktopFilterOptions> =
      ref(mobileOptions)

    onMounted(() => {
      if (isMinScreenMd.value && filterSidebar.isVisible.value) {
        open()
      }
    })
    watch(
      [isMinScreenMd],
      ([isMinScreenMd]) => {
        if (isMinScreenMd) {
          filterComponent.value = 'VSidebarContent'
          options.value = desktopOptions
        } else {
          filterComponent.value = 'VModalContent'
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
      onTab,
      triggerA11yProps,
      isMinScreenMd,
      options,
    }
  },
})
</script>
