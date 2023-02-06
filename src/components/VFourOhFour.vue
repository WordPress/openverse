<template>
  <div
    class="error relative flex flex-col overflow-x-hidden"
    :class="
      isNewHeaderEnabled
        ? 'flex-grow px-6 sm:px-0'
        : 'h-screen h-[100dvh] bg-yellow'
    "
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
    <div v-if="!isNewHeaderEnabled">
      <VLink href="/" class="relative z-10 text-dark-charcoal">
        <VBrand class="m-6 text-[18px] lg:mx-10 lg:my-8" />
      </VLink>
    </div>

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
        <VStandaloneSearchBar
          v-if="isNewHeaderEnabled"
          route="404"
          @submit="handleSearch"
        />
        <VStandaloneSearchBarOld v-else route="404" @submit="handleSearch" />
      </div>
    </main>
  </div>
</template>

<script>
import { defineComponent, useRouter } from "@nuxtjs/composition-api"

import { useSearchStore } from "~/stores/search"
import { useFeatureFlagStore } from "~/stores/feature-flag"

import { ALL_MEDIA } from "~/constants/media"

import VStandaloneSearchBarOld from "~/components/VHeaderOld/VSearchBar/VStandaloneSearchBarOld.vue"
import VLink from "~/components/VLink.vue"
import VBrand from "~/components/VBrand/VBrand.vue"

import Oops from "~/assets/oops.svg"

export default defineComponent({
  name: "VFourOhFour",
  components: {
    VLink,
    VStandaloneSearchBarOld,
    VStandaloneSearchBar: () =>
      import("~/components/VHeader/VSearchBar/VStandaloneSearchBar.vue"),

    VBrand,
  },
  props: ["error"],
  setup() {
    const searchStore = useSearchStore()
    const router = useRouter()

    const handleSearch = (searchTerm) => {
      if (!searchTerm) return

      router.push(searchStore.updateSearchPath({ type: ALL_MEDIA, searchTerm }))
    }

    const featureFlagStore = useFeatureFlagStore()
    const isNewHeaderEnabled = featureFlagStore.isOn("new_header")

    return {
      handleSearch,
      isNewHeaderEnabled,
      Oops,
    }
  },
  head: {
    meta: [
      {
        hid: "theme-color",
        name: "theme-color",
        content: "#ffe033",
      },
    ],
  },
})
</script>
