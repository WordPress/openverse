<script setup lang="ts">
import { useNuxtApp, useRoute } from "#imports"

import { computed, ref, SetupContext, watch } from "vue"

import { useDialogControl } from "~/composables/use-dialog-control"
import { useHydrating } from "~/composables/use-hydrating"

import { useUiStore } from "~/stores/ui"

import VHomeLink from "~/components/VHeader/VHomeLink.vue"
import VPageLinks from "~/components/VHeader/VPageLinks.vue"
import VModalContent from "~/components/VModal/VModalContent.vue"
import VPopoverContent from "~/components/VPopover/VPopoverContent.vue"
import VWordPressLink from "~/components/VHeader/VWordPressLink.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"

const emit = defineEmits<{
  open: []
  close: []
}>() as SetupContext["emit"]

const menuButtonRef = ref<InstanceType<typeof VIconButton> | null>(null)
const nodeRef = ref<HTMLElement | null>(null)
const modalContentRef = ref<InstanceType<typeof VModalContent> | null>(null)

const uiStore = useUiStore()

const route = useRoute()

const { $sendCustomEvent } = useNuxtApp()

const isModalVisible = ref(false)

const isSm = computed(() => uiStore.isBreakpoint("sm"))

const triggerElement = computed(
  () => (menuButtonRef.value?.$el as HTMLElement) || null
)

const lockBodyScroll = computed(() => !isSm.value)

const deactivateFocusTrap = computed(
  () => modalContentRef.value?.deactivateFocusTrap
)

const { doneHydrating } = useHydrating()

const menuId = "pages-menu"

const {
  close: closePageMenu,
  open: openPageMenu,
  onTriggerClick: internalOnTriggerClick,
  triggerA11yProps,
} = useDialogControl({
  id: menuId,
  visibleRef: isModalVisible,
  nodeRef,
  lockBodyScroll,
  emit,
  deactivateFocusTrap,
})

const onTriggerClick = () => {
  if (!isModalVisible.value) {
    $sendCustomEvent("OPEN_PAGES_MENU", {})
  }
  return internalOnTriggerClick()
}

// When clicking on an internal link in the modal, close the modal
watch(route, () => {
  if (isModalVisible.value) {
    closePageMenu()
  }
})
</script>

<template>
  <header
    ref="nodeRef"
    class="main-header z-30 flex h-20 w-full items-stretch justify-between gap-x-2 border-b border-tx px-2 py-4 md:py-4 lg:pe-10 lg:ps-6"
  >
    <VHomeLink variant="dark" />
    <nav class="hidden lg:flex">
      <VPageLinks
        mode="light"
        class="flex items-center gap-6 text-sm"
        @close="closePageMenu"
      />
    </nav>
    <div class="flex lg:hidden">
      <VIconButton
        id="menu-button"
        ref="menuButtonRef"
        variant="transparent-dark"
        size="large"
        :disabled="!doneHydrating"
        :icon-props="{ name: 'menu' }"
        :label="$t('header.aria.menu')"
        v-bind="triggerA11yProps"
        @click="onTriggerClick"
      />
      <template v-if="triggerElement">
        <VPopoverContent
          v-if="isSm"
          :id="menuId"
          z-index="popover"
          :hide="closePageMenu"
          :visible="isModalVisible"
          :trigger-element="triggerElement"
          :trap-focus="false"
          aria-labelledby="menu-button"
        >
          <VPageLinks
            mode="dark"
            variant="itemgroup"
            class="label-regular w-50 items-start"
            @close="closePageMenu"
          />
        </VPopoverContent>
        <VModalContent
          v-else-if="!isSm"
          :id="menuId"
          ref="modalContentRef"
          aria-labelledby="menu-button"
          :hide="closePageMenu"
          variant="full"
          mode="dark"
          modal-content-classes="flex sm:hidden"
          :visible="isModalVisible"
          @open="openPageMenu"
        >
          <template #top-bar>
            <div class="flex h-20 w-full justify-between px-2 py-4">
              <VHomeLink variant="light" />
              <VIconButton
                variant="transparent-tx"
                size="large"
                :icon-props="{ name: 'close' }"
                class="focus-visible:ring-bg-complementary text-white focus-slim-tx hover:bg-tertiary"
                :label="$t('modal.closePagesMenu')"
                @click="closePageMenu"
              />
            </div>
          </template>
          <template #default>
            <nav>
              <VPageLinks
                mode="dark"
                class="mt-3 flex flex-col items-end gap-y-6"
                nav-link-classes="text-white text-3xl focus-visible:ring-bg-complementary"
                :is-in-modal="true"
                @close="closePageMenu"
              />
            </nav>
            <VWordPressLink
              class="focus-visible:ring-bg-complementary mt-auto focus-visible:ring-offset-0"
              mode="dark"
            />
          </template>
        </VModalContent>
      </template>
    </div>
  </header>
</template>
