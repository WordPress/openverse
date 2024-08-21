<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { computed, ref } from "vue"

import { storeToRefs } from "pinia"

import { useUiStore } from "~/stores/ui"
import { useSearchStore } from "~/stores/search"
import { useMediaStore } from "~/stores/media"

import { useExternalSources } from "~/composables/use-external-sources"

import VExternalSourceList from "~/components/VExternalSearch/VExternalSourceList.vue"
import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VModal from "~/components/VModal/VModal.vue"

withDefaults(
  defineProps<{
    searchTerm: string
    isSupported?: boolean
    hasNoResults?: boolean
  }>(),
  {
    isSupported: false,
    hasNoResults: true,
  }
)

const sectionRef = ref<HTMLElement | null>(null)
const searchStore = useSearchStore()
const uiStore = useUiStore()

const { $sendCustomEvent } = useNuxtApp()

const mediaStore = useMediaStore()
const { currentPage } = storeToRefs(mediaStore)

const handleModalOpen = () => {
  $sendCustomEvent("VIEW_EXTERNAL_SOURCES", {
    searchType: searchStore.searchType,
    query: searchStore.searchTerm,
    resultPage: currentPage.value || 1,
  })
}

const { externalSourcesType } = useExternalSources()

const isMd = computed(() => uiStore.isBreakpoint("md"))
</script>

<template>
  <section
    :key="externalSourcesType"
    ref="sectionRef"
    class="external-sources flex flex-row place-items-center justify-center pb-6 pt-4 lg:pb-10"
    data-testid="external-sources-form"
  >
    <VModal
      variant="centered"
      :hide-on-click-outside="true"
      labelled-by="external-sources-button"
      class="w-full"
      @open="handleModalOpen"
    >
      <template #trigger="{ a11yProps }">
        <VButton
          id="external-sources-button"
          ref="triggerRef"
          :pressed="a11yProps['aria-expanded']"
          aria-haspopup="dialog"
          aria-controls="external-sources-modal"
          variant="bordered-gray"
          size="disabled"
          class="label-bold lg:description-bold h-16 w-full gap-x-2 lg:h-18"
        >
          <i18n-t
            v-if="isMd"
            scope="global"
            keypath="externalSources.form.supportedTitle"
            tag="p"
          />
          <i18n-t
            v-else
            scope="global"
            keypath="externalSources.form.supportedTitleSm"
            tag="p"
          />
          <VIcon
            :class="{
              'text-over-dark': a11yProps['aria-expanded'],
            }"
            name="caret-down"
          />
        </VButton>
      </template>
      <template #title>
        <h2 class="heading-6" tabindex="-1">
          {{ $t("externalSources.title") }}
        </h2>
      </template>
      <VExternalSourceList
        class="-mt-3 flex flex-col"
        :search-term="searchTerm"
      />
    </VModal>
  </section>
</template>
