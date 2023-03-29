<template>
  <section
    :key="type"
    ref="sectionRef"
    class="external-sources flex flex-row place-items-center justify-center py-4"
    data-testid="external-sources-form"
  >
    <i18n
      v-if="!hasNoResults && isSupported"
      path="external-sources.form.supported-title"
      tag="p"
      class="description-regular"
    />

    <i18n
      v-else-if="!hasNoResults && !isSupported"
      path="external-sources.form.unsupported-title"
      tag="p"
      class="description-regular"
    >
      <template #openverse>Openverse</template>
      <template #type>{{ $t(`external-sources.form.types.${type}`) }}</template>
    </i18n>

    <i18n
      v-else
      path="external-sources.form.no-results-title"
      tag="p"
      class="description-regular"
    >
      <template #type>{{ $t(`external-sources.form.types.${type}`) }}</template>
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
      >{{ $t("external-sources.button").toString()
      }}<VIcon
        class="text-dark-charcoal-40"
        :class="{ 'text-white': triggerA11yProps['aria-expanded'] }"
        :icon-path="caretDownIcon"
      />
    </VButton>
    <template v-if="triggerElement">
      <VPopoverContent
        v-if="isMd"
        id="external-sources-popover"
        aria-labelledby="external-sources-button"
        :hide="closeDialog"
        :trigger-element="triggerElement"
        :visible="isVisible"
        z-index="popover"
      >
        <VExternalSourceList
          class="flex flex-col"
          :external-sources="externalSources"
          @close="closeDialog"
      /></VPopoverContent>
      <VModalContent
        v-else
        id="external-sources-modal"
        aria-labelledby="external-sources-button"
        :trigger-element="triggerElement"
        :hide="closeDialog"
        :visible="isVisible"
        variant="centered"
      >
        <VExternalSourceList
          class="flex-col justify-center"
          :external-sources="externalSources"
          @close="closeDialog"
        />
      </VModalContent>
    </template>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, PropType, ref, SetupContext } from "vue"

import { defineEvent } from "~/types/emits"

import { useUiStore } from "~/stores/ui"

import { useDialogControl } from "~/composables/use-dialog-control"

import type { MediaType } from "~/constants/media"
import type { ExternalSource } from "~/types/external-source"

import VExternalSourceList from "~/components/VExternalSearch/VExternalSourceList.vue"
import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VPopoverContent from "~/components/VPopover/VPopoverContent.vue"
import VModalContent from "~/components/VModal/VModalContent.vue"

import caretDownIcon from "~/assets/icons/caret-down.svg"

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

    const isMd = computed(() => uiStore.isBreakpoint("md"))

    const triggerElement = computed(() => triggerRef.value?.$el as HTMLElement)

    const lockBodyScroll = computed(() => !isMd.value)

    const isVisible = ref(false)

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

    return {
      sectionRef,
      triggerRef,
      triggerElement,
      isMd,

      closeDialog,
      openDialog,
      onTriggerClick,
      triggerA11yProps,

      isVisible,

      caretDownIcon,
    }
  },
})
</script>
