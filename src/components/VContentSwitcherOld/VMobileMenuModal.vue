<template>
  <VModal
    ref="nodeRef"
    class="mobile-menu ms-auto md:ms-0"
    :label="$t('header.filter-button.simple').toString()"
    :initial-focus-element="initialFocusElement"
  >
    <template #trigger="{ a11yProps, visible }">
      <VSearchTypeButtonOld
        :a11y-props="a11yProps"
        :visible="visible"
        :active-item="activeItem"
        aria-controls="content-switcher-modal"
      />
    </template>
    <nav
      id="content-switcher-modal"
      class="p-6"
      aria-labelledby="content-switcher-heading"
    >
      <VSearchTypesOld
        ref="searchTypesRef"
        size="small"
        :active-item="content.activeType.value"
        :use-links="true"
        @select="selectItem"
      />
      <VPageList layout="columns" class="mt-10" />
    </nav>
  </VModal>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from '@nuxtjs/composition-api'

import usePages from '~/composables/use-pages'
import useSearchType from '~/composables/use-search-type'

import type { SupportedSearchType } from '~/constants/media'

import VModal from '~/components/VModal/VModal.vue'
import VPageList from '~/components/VHeaderOld/VPageMenu/VPageList.vue'
import VSearchTypeButtonOld from '~/components/VContentSwitcherOld/VSearchTypeButtonOld.vue'
import VSearchTypesOld from '~/components/VContentSwitcherOld/VSearchTypesOld.vue'

export default defineComponent({
  name: 'VMobileMenuModal',
  components: {
    VModal,
    VPageList,
    VSearchTypeButtonOld,
    VSearchTypesOld,
  },
  props: {
    activeItem: {
      type: String,
      required: true,
    },
  },
  setup(_, { emit }) {
    const nodeRef = ref<InstanceType<typeof VModal> | null>(null)

    const searchTypesRef = ref<InstanceType<typeof VSearchTypesOld> | null>(
      null
    )

    const content = useSearchType()
    const pages = usePages()

    const initialFocusElement = computed(() => {
      return searchTypesRef.value?.$el
        ? (searchTypesRef.value.$el as HTMLElement).querySelector<HTMLElement>(
            '[aria-checked="true"]'
          )
        : null
    })

    const selectItem = (item: SupportedSearchType) => emit('select', item)

    const closeMenu = () => nodeRef.value?.close()

    return {
      pages,
      content,
      nodeRef,
      searchTypesRef,

      closeMenu,
      selectItem,
      initialFocusElement,
    }
  },
})
</script>
