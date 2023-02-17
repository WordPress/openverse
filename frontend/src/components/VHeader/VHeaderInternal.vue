<template>
  <header
    ref="nodeRef"
    class="main-header z-30 flex h-20 w-full items-stretch justify-between gap-x-2 border-b border-tx py-4 ps-2 pe-3 md:py-4 lg:ps-6 lg:pe-10"
  >
    <VHomeLink variant="dark" class="px-4 hover:bg-yellow" />
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
        :icon-props="{ iconPath: menuIcon }"
        :aria-label="$t('header.aria.menu')"
        v-bind="triggerA11yProps"
        class="border-tx hover:bg-dark-charcoal hover:text-white"
        :class="{ 'bg-dark-charcoal text-white': isModalVisible }"
        @click="onTriggerClick"
      />
      <template v-if="triggerElement">
        <VPopoverContent
          v-if="isSm"
          z-index="popover"
          :hide="closePageMenu"
          :visible="isModalVisible"
          :trigger-element="triggerElement"
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
            <div class="flex h-20 w-full justify-between py-4 pe-3 ps-6">
              <VHomeLink
                variant="light"
                class="focus-visible:ring-yellow focus-visible:ring-offset-0"
              />
              <VIconButton
                ref="closeButton"
                :icon-props="{ iconPath: closeIcon }"
                class="border-tx text-white focus-visible:ring-yellow focus-visible:ring-offset-0"
                :aria-label="$t('modal.close')"
                @click="closePageMenu"
              />
            </div>
          </template>
          <template #default>
            <nav>
              <VPageLinks
                mode="dark"
                class="mt-3 flex flex-col items-end gap-y-6"
                nav-link-classes="text-white text-3xl focus-visible:ring-yellow"
                :is-in-modal="true"
                @close="closePageMenu"
              />
            </nav>
            <VWordPressLink
              class="mt-auto focus-visible:ring-yellow focus-visible:ring-offset-0"
              mode="dark"
            />
          </template>
        </VModalContent>
      </template>
    </div>
  </header>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  ref,
  useRoute,
  watch,
} from "@nuxtjs/composition-api"

import { useDialogControl } from "~/composables/use-dialog-control"
import usePages from "~/composables/use-pages"

import { useUiStore } from "~/stores/ui"

import VHomeLink from "~/components/VHeader/VHomeLink.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"
import VPageLinks from "~/components/VHeader/VPageLinks.vue"
import VModalContent from "~/components/VModal/VModalContent.vue"
import VPopoverContent from "~/components/VPopover/VPopoverContent.vue"
import VWordPressLink from "~/components/VHeader/VWordPressLink.vue"

import closeIcon from "~/assets/icons/close.svg"
import menuIcon from "~/assets/icons/menu.svg"

export default defineComponent({
  name: "VHeaderInternal",
  components: {
    VModalContent,
    VPopoverContent,
    VHomeLink,
    VIconButton,
    VPageLinks,
    VWordPressLink,
  },
  setup(_, { emit }) {
    const menuButtonRef = ref<InstanceType<typeof VIconButton> | null>(null)
    const nodeRef = ref<HTMLElement | null>(null)
    const modalContentRef = ref<InstanceType<typeof VModalContent> | null>(null)

    const uiStore = useUiStore()

    const route = useRoute()

    const { all: allPages, current: currentPage } = usePages(true)

    const isModalVisible = ref(false)

    const isSm = computed(() => uiStore.isBreakpoint("sm"))

    const triggerElement = computed(
      () => (menuButtonRef.value?.$el as HTMLElement) || null
    )

    const lockBodyScroll = computed(() => !isSm.value)

    const deactivateFocusTrap = computed(
      () => modalContentRef.value?.deactivateFocusTrap
    )

    const {
      close: closePageMenu,
      open: openPageMenu,
      onTriggerClick,
      triggerA11yProps,
    } = useDialogControl({
      visibleRef: isModalVisible,
      nodeRef,
      lockBodyScroll,
      emit,
      deactivateFocusTrap,
    })

    // When clicking on an internal link in the modal, close the modal
    watch(route, () => {
      if (isModalVisible.value) {
        closePageMenu()
      }
    })

    return {
      menuButtonRef,
      modalContentRef,
      nodeRef,

      closeIcon,
      menuIcon,

      allPages,
      currentPage,

      isModalVisible,
      closePageMenu,
      openPageMenu,
      isSm,
      onTriggerClick,
      triggerA11yProps,
      triggerElement,
    }
  },
})
</script>
