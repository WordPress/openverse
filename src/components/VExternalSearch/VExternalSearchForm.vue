<template>
  <section
    :key="type"
    ref="sectionRef"
    class="external-sources flex flex-row place-items-center justify-center p-4"
    data-testid="external-sources-form"
    @keydown.tab.exact="handleTab"
  >
    <i18n
      v-if="!hasNoResults && isSupported"
      path="external-sources.form.supported-title"
      tag="p"
      class="text-base font-normal leading-[130%]"
    />

    <i18n
      v-else-if="!hasNoResults && !isSupported"
      path="external-sources.form.unsupported-title"
      tag="p"
      class="text-base font-normal leading-[130%]"
    >
      <template #openverse>Openverse</template>
      <template #type>{{ $t(`external-sources.form.types.${type}`) }}</template>
    </i18n>

    <i18n
      v-else
      path="external-sources.form.no-results-title"
      tag="p"
      class="text-base font-normal leading-[130%]"
    >
      <template #type>{{ $t(`external-sources.form.types.${type}`) }}</template>
      <template #query>{{ query.q }}</template>
    </i18n>

    <VExternalSourceList
      class="inline-flex ms-2 md:justify-center"
      :type="type"
      :query="query"
    />
  </section>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  PropType,
  ref,
} from '@nuxtjs/composition-api'

import type { MediaType } from '~/constants/media'
import type { ApiQueryParams } from '~/utils/search-query-transform'
import { getFocusableElements } from '~/utils/focus-management'
import { defineEvent } from '~/types/emits'

import VExternalSourceList from './VExternalSourceList.vue'

export default defineComponent({
  name: 'VExternalSearchForm',
  components: {
    VExternalSourceList,
  },
  props: {
    query: { type: Object as PropType<ApiQueryParams>, required: true },
    type: { type: String as PropType<MediaType>, required: true },
    isSupported: { type: Boolean, default: false },
    hasNoResults: { type: Boolean, required: true },
  },
  emits: {
    tab: defineEvent<[KeyboardEvent]>(),
  },
  setup(_, { emit }) {
    const sectionRef = ref<HTMLElement>()

    /**
     * Find the last focusable element in VSearchGridFilter to add a 'Tab' keydown event
     * handler to it.
     * We could actually hard-code this because 'searchBy' is always the last now.
     */
    const lastFocusableElement = computed<HTMLElement>(() => {
      const focusable = getFocusableElements(sectionRef.value)
      return focusable[focusable.length - 1]
    })

    const handleTab = (event: KeyboardEvent) => {
      if (event.target === lastFocusableElement.value) {
        emit('tab', event)
      }
    }
    return {
      sectionRef,
      handleTab,
    }
  },
})
</script>
