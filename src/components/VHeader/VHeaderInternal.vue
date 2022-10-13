<template>
  <header
    class="main-header z-30 flex h-20 w-full items-stretch justify-between gap-x-2 bg-white py-4 pe-3 ps-6 md:py-4 md:px-7"
  >
    <VHomeLink variant="dark" />
    <nav class="justify-stretch md:justify-stretch hidden ms-auto md:flex">
      <VPageLinks mode="dark" variant="inline" @close="closeModal" />
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
            :button-props="{ variant: 'plain' }"
            :aria-label="$t('header.aria.menu')"
            v-bind="a11yProps"
            class="border-tx hover:bg-dark-charcoal hover:text-white"
            size="search-medium"
          />
        </template>

        <template #top-bar>
          <div
            class="flex h-20 w-full justify-between bg-dark-charcoal py-4 text-white pe-3 ps-6"
          >
            <VHomeLink variant="light" />
            <VIconButton
              ref="closeButton"
              :button-props="{ variant: 'plain' }"
              :icon-props="{ iconPath: closeIcon }"
              size="search-medium"
              class="border-tx text-white focus-visible:ring-offset-tx"
              :aria-label="$t('modal.close')"
              @click="closeModal"
            />
          </div>
        </template>
        <template #default>
          <VPageLinks mode="light" variant="column" @close="closeModal" />
          <VLink
            href="https://wordpress.org"
            class="text-white hover:no-underline focus-visible:rounded-sm focus-visible:outline-none focus-visible:ring focus-visible:ring-pink focus-visible:ring-offset-1 focus-visible:ring-offset-tx"
          >
            <i18n
              tag="p"
              path="footer.wordpress-affiliation"
              class="mt-auto flex flex-row items-center text-sm"
            >
              <template #wordpress>
                <WordPress class="aria-hidden text-white" />
                <span class="sr-only">WordPress</span>
              </template>
            </i18n>
          </VLink>
        </template>
      </VModal>
    </div>
  </header>
</template>

<script lang="ts">
import {
  defineComponent,
  inject,
  ref,
  useRoute,
  watch,
} from '@nuxtjs/composition-api'

import usePages from '~/composables/use-pages'

import { IsMinScreenMdKey } from '~/types/provides'

import VHomeLink from '~/components/VHeader/VHomeLink.vue'
import VIconButton from '~/components/VIconButton/VIconButton.vue'
import VLink from '~/components/VLink.vue'
import VPageLinks from '~/components/VHeader/VPageLinks.vue'
import VModal from '~/components/VModal/VModal.vue'

import closeIcon from '~/assets/icons/close.svg'
import menuIcon from '~/assets/icons/menu.svg'
import WordPress from '~/assets/wordpress.svg?inline'

export default defineComponent({
  name: 'VHeaderInternal',
  components: { VHomeLink, VIconButton, VLink, VModal, VPageLinks, WordPress },
  setup() {
    const menuButtonRef = ref<InstanceType<typeof VIconButton> | null>(null)

    const { all: allPages, current: currentPage } = usePages(true)
    const route = useRoute()

    const isMinScreenMd = inject(IsMinScreenMdKey)

    const isModalVisible = ref(false)
    const closeModal = () => (isModalVisible.value = false)
    const openModal = () => (isModalVisible.value = true)

    // When clicking on an internal link in the modal, close the modal
    watch(route, () => {
      if (isModalVisible.value) {
        closeModal()
      }
    })

    watch(isMinScreenMd, (isMd) => {
      if (isMd && isModalVisible.value) {
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
