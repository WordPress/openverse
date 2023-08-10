<template>
  <section
    :key="externalSourcesType"
    ref="sectionRef"
    class="external-sources flex flex-row place-items-center justify-center py-4"
    data-testid="external-sources-form"
  >

    <VModal
      variant="centered"
      :hide-on-click-outside="true"
      labelled-by="external-sources-button"
      @open="handleModalOpen"
    >
      <template #trigger="triggerA11yProps">
        <VButton
            id="external-sources-button"
            ref="triggerRef"
            :pressed="triggerA11yProps['aria-expanded']"
            aria-haspopup="dialog"
            :aria-controls="'external-sources-modal'"
            variant="filled-gray"
            size="disabled"
            class="label-bold lg:description-bold h-16 w-full lg:h-18"
        >
          <i18n
              v-if="!hasNoResults && isSupported && isMd"
              path="externalSources.form.supportedTitle"
              tag="p"
              class="description-regular"
          />

          <i18n
              v-else-if="!hasNoResults && isSupported && !isMd"
              path="externalSources.form.supportedTitleSM"
              tag="p"
              class="description-regular"
          />

          <i18n
              v-else-if="!hasNoResults && !isSupported"
              path="externalSources.form.unsupportedTitle"
              tag="p"
              class="description-regular"
          >
            <template #openverse>Openverse</template>
            <template #type>{{
                $t(`externalSources.form.types.${externalSourcesType}`)
              }}</template>
          </i18n>

          <i18n
              v-else
              path="externalSources.form.noResultsTitle"
              tag="p"
              class="description-regular"
          >
            <template #type>{{
                $t(`externalSources.form.types.${externalSourcesType}`)
              }}</template>
            <template #query>{{ searchTerm }}</template>
          </i18n>
          <VIcon
              class="text-dark-charcoal-40"
              :class="{ 'text-white': triggerA11yProps['aria-expanded'] }"
              name="caret-down"
          />
        </VButton>
      </template>
      <template #top-bar="{ close }">
        <header
          class="flex items-center justify-between pe-5 ps-7 pt-5 sm:pe-7 sm:ps-9 sm:pt-7"
        >
          <h2 class="heading-6" tabindex="-1">
            {{ $t("externalSources.title") }}
          </h2>
          <VIconButton
            size="small"
            :icon-props="{ name: 'close' }"
            variant="transparent-gray"
            :label="$t('modal.close')"
            @click="close"
          />
        </header>
      </template>
      <VExternalSourceList class="flex flex-col" :search-term="searchTerm" />
    </VModal>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from "vue"

import { storeToRefs } from "pinia"

import { defineEvent } from "~/types/emits"

import { useUiStore } from "~/stores/ui"
import { useSearchStore } from "~/stores/search"
import { useMediaStore } from "~/stores/media"

import { useAnalytics } from "~/composables/use-analytics"
import { useExternalSources } from "~/composables/use-external-sources"

import VExternalSourceList from "~/components/VExternalSearch/VExternalSourceList.vue"
import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VModal from "~/components/VModal/VModal.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"

export default defineComponent({
  name: "VExternalSearchForm",
  components: {
    VModal,
    VIconButton,
    VIcon,
    VButton,
    VExternalSourceList,
  },
  props: {
    searchTerm: {
      type: String,
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
  setup() {
    const sectionRef = ref<HTMLElement | null>(null)
    const searchStore = useSearchStore()
    const uiStore = useUiStore()

    const { sendCustomEvent } = useAnalytics()

    const mediaStore = useMediaStore()
    const { currentPage } = storeToRefs(mediaStore)

    const handleModalOpen = () => {
      sendCustomEvent("VIEW_EXTERNAL_SOURCES", {
        searchType: searchStore.searchType,
        query: searchStore.searchTerm,
        resultPage: currentPage.value || 1,
      })
    }

    const { externalSourcesType } = useExternalSources()

    const isMd = computed(() => uiStore.isBreakpoint("md"))

    return {
      externalSourcesType,
      sectionRef,
      isMd,

      handleModalOpen,
    }
  },
})
</script>
