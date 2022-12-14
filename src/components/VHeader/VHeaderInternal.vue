<template>
  <header
    class="main-header z-30 flex h-20 w-full items-stretch justify-between gap-x-2 bg-white py-4 pe-3 ps-6 md:py-4 md:px-7"
  >
    <VHomeLink variant="dark" />
    <nav class="md:justify-stretch hidden ms-auto md:flex">
      <VPageLinks
        mode="light"
        class="md:justify-stretch flex hidden flex-row items-center gap-8 text-sm ms-auto md:flex"
        nav-link-classes="ps-3"
        @close="closeModal"
      />
    </nav>
    <div class="flex md:hidden">
      <VModal
        :label="$t('header.aria.menu').toString()"
        variant="full"
        mode="dark"
        modal-content-classes="flex md:hidden"
        :visible="isModalVisible"
        @open="openModal"
      >
        <template #trigger="{ a11yProps }">
          <VIconButton
            ref="menuButtonRef"
            :icon-props="{ iconPath: menuIcon }"
            :aria-label="$t('header.aria.menu')"
            v-bind="a11yProps"
            class="border-tx hover:bg-dark-charcoal hover:text-white"
          />
        </template>

        <template #top-bar>
          <div
            class="flex h-20 w-full justify-between bg-dark-charcoal py-4 text-white pe-3 ps-6"
          >
            <VHomeLink variant="light" />
            <VIconButton
              ref="closeButton"
              :icon-props="{ iconPath: closeIcon }"
              class="border-tx text-white focus-visible:ring-offset-tx"
              :aria-label="$t('modal.close')"
              @click="closeModal"
            />
          </div>
        </template>
        <template #default>
          <nav>
            <VPageLinks
              mode="dark"
              class="mt-3 flex flex-col items-end gap-y-2"
              nav-link-classes="heading-5 py-3"
              @close="closeModal"
            />
          </nav>
          <VWordPressLink class="mt-auto" mode="dark" />
        </template>
      </VModal>
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
} from '@nuxtjs/composition-api'

import usePages from '~/composables/use-pages'

import { useUiStore } from '~/stores/ui'

import VHomeLink from '~/components/VHeader/VHomeLink.vue'
import VIconButton from '~/components/VIconButton/VIconButton.vue'
import VPageLinks from '~/components/VHeader/VPageLinks.vue'
import VModal from '~/components/VModal/VModal.vue'

import VWordPressLink from '~/components/VHeader/VWordPressLink.vue'

import closeIcon from '~/assets/icons/close.svg'
import menuIcon from '~/assets/icons/menu.svg'

export default defineComponent({
  name: 'VHeaderInternal',
  components: {
    VWordPressLink,
    VHomeLink,
    VIconButton,
    VModal,
    VPageLinks,
  },
  setup() {
    const menuButtonRef = ref<InstanceType<typeof VIconButton> | null>(null)

    const route = useRoute()

    const { all: allPages, current: currentPage } = usePages(true)

    const isModalVisible = ref(false)
    const closeModal = () => (isModalVisible.value = false)
    const openModal = () => (isModalVisible.value = true)

    // When clicking on an internal link in the modal, close the modal
    watch(route, () => {
      if (isModalVisible.value) {
        closeModal()
      }
    })

    const uiStore = useUiStore()
    const isDesktopLayout = computed(() => uiStore.isDesktopLayout)
    watch(isDesktopLayout, (isDesktop) => {
      if (isDesktop && isModalVisible.value) {
        closeModal()
      }
    })

    return {
      menuButtonRef,

      closeIcon,
      menuIcon,

      allPages,
      currentPage,

      isModalVisible,
      closeModal,
      openModal,
    }
  },
})
</script>
