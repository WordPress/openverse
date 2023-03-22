<template>
  <div class="error grid overflow-x-hidden">
    <svg
      class="z-0 pointer-events-none col-start-1 row-start-1 -mx-[15%] fill-dark-charcoal opacity-5 lg:mx-15 lg:-mt-20"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 1320 569"
      aria-hidden="true"
      focusable="false"
    >
      <use :href="`${Oops}#oops`" />
    </svg>

    <div
      class="page-404 col-start-1 row-start-1 flex flex-col justify-self-stretch px-6 lg:max-w-2xl lg:justify-self-center lg:px-0"
    >
      <!-- Push content by 1/4th height without absolute positioning. -->
      <div class="spacer grow" />
      <VSkipToContentContainer
        as="main"
        class="z-10 grow-[3] space-y-4 lg:space-y-6"
      >
        <h1 class="heading-5 lg:heading-2 mb-6 lg:mb-10 lg:leading-tight">
          {{ $t("404.title") }}
        </h1>
        <p class="label-bold lg:heading-6">
          <i18n path="404.main">
            <template #link>
              <VLink
                class="text-current underline hover:text-current active:text-current"
                href="/"
                >Openverse</VLink
              >
            </template>
          </i18n>
        </p>
        <VStandaloneSearchBar route="404" @submit="handleSearch" />
      </VSkipToContentContainer>
    </div>
  </div>
</template>

<script>
import { defineComponent } from "vue"
import { useMeta, useRouter } from "@nuxtjs/composition-api"

import { useSearchStore } from "~/stores/search"

import { ALL_MEDIA } from "~/constants/media"

import VLink from "~/components/VLink.vue"
import VSkipToContentContainer from "~/components/VSkipToContentContainer.vue"
import VStandaloneSearchBar from "~/components/VHeader/VSearchBar/VStandaloneSearchBar.vue"

import Oops from "~/assets/oops.svg"

export default defineComponent({
  name: "VFourOhFour",
  components: {
    VLink,
    VSkipToContentContainer,
    VStandaloneSearchBar,
  },
  props: ["error"],
  setup() {
    const searchStore = useSearchStore()
    const router = useRouter()

    const handleSearch = (searchTerm) => {
      if (!searchTerm) return

      router.push(searchStore.updateSearchPath({ type: ALL_MEDIA, searchTerm }))
    }

    useMeta({
      meta: [{ hid: "theme-color", name: "theme-color", content: "#ffe033" }],
    })

    return {
      handleSearch,
      Oops,
    }
  },
  head: {},
})
</script>
