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
      <template #query>{{ searchTerm }}</template>
    </i18n>

    <VExternalSourceList
      class="inline-flex ms-2 md:justify-center"
      :external-sources="externalSources"
    />
  </section>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  PropType,
  ref,
} from "@nuxtjs/composition-api"

import { getFocusableElements } from "~/utils/focus-management"
import { defineEvent } from "~/types/emits"

import type { MediaType } from "~/constants/media"

import type { ExternalSource } from "~/types/external-source"

import VExternalSourceList from "~/components/VExternalSearch/VExternalSourceList.vue"

export default defineComponent({
  name: "VExternalSearchForm",
  components: {
    VExternalSourceList,
  },
  props: {
    type: {
      type: String as PropType<MediaType>,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
    externalSources: {
      type: Array as PropType<ExternalSource[]>,
      required: true,
    },
    isSupported: {
      type: Boolean,
      default: false,
    },
    hasNoResults: {
      type: Boolean,
      required: true,
    },
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
        emit("tab", event)
      }
    }
    return {
      sectionRef,
      handleTab,
    }
  },
})
</script>
