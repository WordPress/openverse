<template>
  <section
    :key="type"
    ref="sectionRef"
    class="external-sources flex flex-row place-items-center justify-center py-4"
    data-testid="external-sources-form"
  >
    <i18n
      v-if="!hasNoResults && isSupported"
      path="externalSources.form.supportedTitle"
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
      <template #type>{{ $t(`externalSources.form.types.${type}`) }}</template>
    </i18n>

    <i18n
      v-else
      path="externalSources.form.noResultsTitle"
      tag="p"
      class="description-regular"
    >
      <template #type>{{ $t(`externalSources.form.types.${type}`) }}</template>
      <template #query>{{ searchTerm }}</template>
    </i18n>

    <VButton
      id="external-sources-button"
      ref="triggerRef"
      :pressed="triggerA11yProps['aria-expanded']"
      aria-haspopup="dialog"
      :aria-controls="
        isMd ? 'external-sources-popover' : 'external-sources-modal'
      "
      variant="dropdown-label"
      size="disabled"
      class="caption-regular ms-2 min-w-max gap-1 px-3 py-1 pe-1 text-dark-charcoal focus-visible:border-tx"
      @click="onTriggerClick"
      >{{ $t("externalSources.button").toString()
      }}<VIcon
        class="text-dark-charcoal-40"
        :class="{ 'text-white': triggerA11yProps['aria-expanded'] }"
        name="caret-down"
      />
    </VButton>
    <template v-if="triggerElement">
      <Component
        :is="isMd ? 'VPopoverContent' : 'VModalContent'"
        :id="isMd ? 'external-sources-popover' : 'external-sources-modal'"
        :aria-labelledby="'external-sources-button'"
        :hide="closeDialog"
        :trigger-element="triggerElement"
        :visible="isVisible"
        :z-index="isMd ? 'popover' : 'modal'"
        :variant="isMd ? undefined : 'centered'"
      >
        <VExternalSourceList
          class="flex flex-col"
          :external-sources="externalSources"
          :media-type="type"
          :search-term="searchTerm"
          @close="closeDialog"
        />
      </Component>
    </template>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, PropType, ref, SetupContext } from "vue"

import { storeToRefs } from "pinia"

import { defineEvent } from "~/types/emits"

import { useUiStore } from "~/stores/ui"
import { useSearchStore } from "~/stores/search"
import { useMediaStore } from "~/stores/media"

import { useDialogControl } from "~/composables/use-dialog-control"
import { useAnalytics } from "~/composables/use-analytics"

import type { MediaType } from "~/constants/media"
import type { ExternalSource } from "~/types/external-source"

import VExternalSourceList from "~/components/VExternalSearch/VExternalSourceList.vue"
import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VPopoverContent from "~/components/VPopover/VPopoverContent.vue"
import VModalContent from "~/components/VModal/VModalContent.vue"

export default defineComponent({
  name: "VExternalSearchForm",
  components: {
    VModalContent,
    VPopoverContent,
    VIcon,
    VButton,
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
    const sectionRef = ref<HTMLElement | null>(null)
    const triggerRef = ref<InstanceType<typeof VButton> | null>(null)
    const uiStore = useUiStore()
    const searchStore = useSearchStore()
    const { sendCustomEvent } = useAnalytics()

    const isMd = computed(() => uiStore.isBreakpoint("md"))

    const triggerElement = computed(() => triggerRef.value?.$el as HTMLElement)

    const lockBodyScroll = computed(() => !isMd.value)

    const isVisible = ref(false)

    const mediaStore = useMediaStore()
    const { currentPage } = storeToRefs(mediaStore)

    const {
      close: closeDialog,
      open: openDialog,
      onTriggerClick,
      triggerA11yProps,
    } = useDialogControl({
      visibleRef: isVisible,
      nodeRef: sectionRef,
      lockBodyScroll,
      emit: emit as SetupContext["emit"],
    })

    const eventedOnTriggerClick = () => {
      if (!isVisible.value) {
        sendCustomEvent("VIEW_EXTERNAL_SOURCES", {
          searchType: searchStore.searchType,
          query: searchStore.searchTerm,
          resultPage: currentPage.value || 1,
        })
      }
      onTriggerClick()
    }

    return {
      sectionRef,
      triggerRef,
      triggerElement,
      isMd,

      closeDialog,
      openDialog,
      onTriggerClick: eventedOnTriggerClick,
      triggerA11yProps,

      isVisible,
    }
  },
})
</script>
