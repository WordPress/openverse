<template>
  <div
    class="error relative flex flex-grow flex-col overflow-x-hidden px-6 sm:px-0"
  >
    <svg
      class="z-0 pointer-events-none absolute top-20 -mt-[10%] -ml-[20%] w-[140%] fill-dark-charcoal px-6 opacity-5 lg:mx-auto lg:ml-0 lg:w-full lg:px-16"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 1320 569"
      aria-hidden="true"
      focusable="false"
    >
      <use :href="`${Oops}#oops`" />
    </svg>

    <main
      class="page-404 flex w-full flex-shrink-0 flex-grow flex-col overflow-x-hidden px-6 lg:mx-auto lg:max-w-2xl lg:px-0"
    >
      <!-- Push content by 1/4th height without absolute positioning. -->
      <div class="spacer grow" />
      <div class="z-10 grow-[3] space-y-4 lg:space-y-6">
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
      </div>
    </main>
  </div>
</template>

<script>
import { defineComponent, useMeta, useRouter } from "@nuxtjs/composition-api"

import { useSearchStore } from "~/stores/search"

import { ALL_MEDIA } from "~/constants/media"

import VStandaloneSearchBar from "~/components/VHeader/VSearchBar/VStandaloneSearchBar.vue"
import VLink from "~/components/VLink.vue"

import Oops from "~/assets/oops.svg"

export default defineComponent({
  name: "VFourOhFour",
  components: {
    VLink,
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
