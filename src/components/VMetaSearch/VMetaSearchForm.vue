<template>
  <section
    :key="type"
    ref="sectionRef"
    class="p-6 meta-search text-center mt-12"
    data-testid="meta-search-form"
    @keydown.tab.exact="handleTab"
  >
    <header class="mb-10">
      <i18n
        v-if="!hasNoResults"
        :path="
          isSupported
            ? 'meta-search.form.supported-title'
            : 'meta-search.form.unsupported-title'
        "
        tag="h4"
        class="text-4xl mb-2"
      >
        <template #openverse>Openverse</template>
        <template #type>
          {{ type }}
        </template>
      </i18n>
      <i18n
        v-else
        path="meta-search.form.no-results-title"
        tag="h4"
        class="text-4xl mb-2"
      >
        <template #type>{{ type }}</template>
        <template #query>{{ query.q }}</template>
      </i18n>
      <i18n path="meta-search.form.caption" tag="p">
        <template #type>{{ type }}</template>
        <template #break>
          <br />
        </template>
        <template #filter>{{ unsupportedByUseFilter }}</template>
      </i18n>
    </header>

    <VMetaSourceList
      class="md:justify-center mt-6 mb-10"
      :type="type"
      :query="query"
    />

    <p class="text-sm font-semibold max-w-3xl my-0 mx-auto">
      {{ $t('meta-search.caption', { openverse: 'Openverse' }) }}
    </p>
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
import { getAdditionalSourceBuilders } from '~/utils/get-additional-sources'
import { getFocusableElements } from '~/utils/focus-management'
import { defineEvent } from '~/types/emits'

import VMetaSourceList from './VMetaSourceList.vue'

export default defineComponent({
  name: 'VMetaSearchForm',
  components: {
    VMetaSourceList,
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
  setup(props, { emit }) {
    const sectionRef = ref<HTMLElement>()
    const unsupportedByUseFilter = computed(() =>
      getAdditionalSourceBuilders(props.type)
        .filter((source) => !source.supportsUseFilters)
        .map((source) => source.name)
        .join(', ')
    )

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
      unsupportedByUseFilter,
      handleTab,
    }
  },
})
</script>
