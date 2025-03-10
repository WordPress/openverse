<script setup lang="ts">
import { computed, ref } from "vue"

import type { SearchType } from "#shared/constants/media"
import { skipToContentTargetId } from "#shared/constants/window"
import { HOMEPAGE_CONTENT_SETTINGS_DIALOG } from "#shared/constants/dialogs"
import { useUiStore } from "~/stores/ui"
import { useDialogControl } from "~/composables/use-dialog-control"

import VContentSettingsModalContent from "~/components/VHeader/VHeaderMobile/VContentSettingsModalContent.vue"
import VLink from "~/components/VLink.vue"
import VPopoverContent from "~/components/VPopover/VPopoverContent.vue"
import VSearchTypeButton from "~/components/VContentSwitcher/VSearchTypeButton.vue"
import VSearchTypes from "~/components/VContentSwitcher/VSearchTypes.vue"
import VStandaloneSearchBar from "~/components/VHeader/VSearchBar/VStandaloneSearchBar.vue"

const props = defineProps<{
  handleSearch: (query: string) => void
  searchType: SearchType
  setSearchType: (searchType: SearchType) => void
}>()

const emit = defineEmits<{
  keydown: []
  blur: []
  focus: []
  open: []
  close: []
}>()

const searchTypeButtonRef = ref<InstanceType<typeof VSearchTypeButton> | null>(
  null
)
const searchBarRef = ref<InstanceType<typeof VStandaloneSearchBar> | null>(null)
const nodeRef = computed(() => searchBarRef.value?.$el ?? null)

const uiStore = useUiStore()

const isContentSwitcherVisible = ref(false)

const isSm = computed(() => uiStore.isBreakpoint("sm"))
const isLg = computed(() => uiStore.isBreakpoint("lg"))

const triggerElement = computed(() => searchTypeButtonRef.value?.$el || null)

const lockBodyScroll = computed(() => !isLg.value)

/**
 * When a search type is selected, we close the popover or modal,
 * and focus the search input.
 *
 * @param searchType
 */
const handleSelect = (searchType: SearchType) => {
  props.setSearchType(searchType)
  searchBarRef.value?.focusInput()
  closeContentSwitcher()
}

const {
  close: closeContentSwitcher,
  open: openContentSwitcher,
  onTriggerClick,
  triggerA11yProps,
} = useDialogControl({
  id: HOMEPAGE_CONTENT_SETTINGS_DIALOG,
  visibleRef: isContentSwitcherVisible,
  nodeRef,
  lockBodyScroll,
  emit: emit as (event: string) => void,
})
</script>

<template>
  <div :id="skipToContentTargetId" tabindex="-1">
    <h1
      class="mb-2 mt-auto text-[40px] font-light leading-tight lg:text-[63px]"
    >
      {{ $t("hero.subtitle") }}
    </h1>

    <p class="text-base leading-relaxed">
      {{ $t("hero.description") }}
    </p>

    <VStandaloneSearchBar
      ref="searchBarRef"
      class="mt-4 md:mt-6 xl:max-w-[43.75rem]"
      :has-popover="!!triggerElement && isContentSwitcherVisible"
      @submit="handleSearch"
    >
      <VSearchTypeButton
        id="search-type-button"
        ref="searchTypeButtonRef"
        class="ms-2 flex-none"
        :search-type="searchType"
        v-bind="triggerA11yProps"
        :show-label="isSm"
        aria-controls="content-switcher-popover"
        @click="onTriggerClick"
      />
      <template v-if="triggerElement">
        <VPopoverContent
          v-if="isLg"
          :id="HOMEPAGE_CONTENT_SETTINGS_DIALOG"
          z-index="popover"
          :hide="closeContentSwitcher"
          :trap-focus="false"
          :visible="isContentSwitcherVisible"
          :trigger-element="triggerElement"
          aria-labelledby="search-type-button"
        >
          <VSearchTypes
            size="small"
            :use-links="false"
            @select="handleSelect"
          />
        </VPopoverContent>

        <VContentSettingsModalContent
          v-else
          :id="HOMEPAGE_CONTENT_SETTINGS_DIALOG"
          aria-labelledby="search-type-button"
          :close="closeContentSwitcher"
          :visible="isContentSwitcherVisible"
          :use-links="false"
          :show-filters="false"
          variant="fit-content"
          @open="openContentSwitcher"
          @select="handleSelect"
        />
      </template>
    </VStandaloneSearchBar>

    <!-- Disclaimer for large screens -->
    <i18n-t
      scope="global"
      keypath="hero.disclaimer.content"
      tag="p"
      class="mt-4 text-sr"
    >
      <template #license>
        <VLink
          href="https://creativecommons.org/licenses/"
          class="text-default underline hover:text-default"
          >{{ $t("hero.disclaimer.license") }}</VLink
        >
      </template>
    </i18n-t>
  </div>
</template>
