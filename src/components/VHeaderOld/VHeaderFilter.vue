<template>
  <div
    ref="nodeRef"
    class="flex items-stretch justify-end text-sr md:text-base"
  >
    <VFilterButtonOld
      ref="buttonRef"
      class="self-stretch"
      :class="isFilterVisible ? 'hidden md:flex' : 'flex'"
      :pressed="isFilterVisible"
      :disabled="disabled"
      aria-haspopup="dialog"
      :aria-expanded="isFilterVisible"
      @toggle="onTriggerClick"
      @tab="onTab"
    />
    <VModalContent
      v-if="isFilterVisible && !isDesktopLayout"
      :hide="onTriggerClick"
      :visible="true"
      :trigger-element="triggerElement"
      :aria-label="$t('header.filter-button.simple')"
    >
      <VSearchGridFilter class="px-6 pt-[7px] pb-10" @close="onTriggerClick" />
    </VModalContent>
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  ref,
  watch,
  computed,
  onBeforeUnmount,
} from '@nuxtjs/composition-api'

import { useBodyScrollLock } from '~/composables/use-body-scroll-lock'
import { useFocusFilters } from '~/composables/use-focus-filters'

import { Focus } from '~/utils/focus-management'
import { defineEvent } from '~/types/emits'

import { useUiStore } from '~/stores/ui'

import VModalContent from '~/components/VModal/VModalContent.vue'
import VSearchGridFilter from '~/components/VFilters/VSearchGridFilter.vue'
import VFilterButtonOld from '~/components/VHeaderOld/VFilterButtonOld.vue'

export default defineComponent({
  name: 'VHeaderFilter',
  components: {
    VFilterButtonOld,
    VModalContent,
    VSearchGridFilter,
  },
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
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
  setup(props, { emit }) {
    const nodeRef = ref<HTMLElement | null>(null)

    const uiStore = useUiStore()

    const isDesktopLayout = computed(() => uiStore.isDesktopLayout)

    const isFilterVisible = computed(
      () => !props.disabled && uiStore.isFilterVisible
    )
    watch(isFilterVisible, (visible) => {
      emit(visible ? 'open' : 'close')
    })
    const { lock, unlock } = useBodyScrollLock({ nodeRef })

    onBeforeUnmount(() => unlock())

    // Lock the scroll when the screen changes to below Md if filters are open.
    watch(isDesktopLayout, (isDesktop) => {
      if (!isDesktop && uiStore.isFilterVisible) {
        lock()
      }
    })

    const onTriggerClick = () => uiStore.toggleFilters()

    const focusFilters = useFocusFilters()
    /**
     * Focus the first element in the sidebar when navigating from the VFilterButton
     * using keyboard `Tab` key.
     */
    const onTab = (event: KeyboardEvent) => {
      focusFilters.focusFilterSidebar(event, Focus.First)
    }

    const triggerElement = computed(() =>
      nodeRef.value?.firstChild
        ? (nodeRef.value?.firstChild as HTMLElement)
        : null
    )

    return {
      nodeRef,
      isFilterVisible,
      triggerElement,
      isDesktopLayout,

      onTriggerClick,
      onTab,
    }
  },
})
</script>
