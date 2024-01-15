<template>
  <div class="error grid overflow-x-hidden">
    <VSvg
      class="z-0 pointer-events-none col-start-1 row-start-1 -mx-[15%] fill-dark-charcoal opacity-5 lg:mx-15 lg:-mt-20"
      viewBox="0 0 1320 569"
      name="oops"
    />
    <div
      class="page-404 col-start-1 row-start-1 flex flex-col justify-self-stretch px-6 lg:max-w-2xl lg:justify-self-center lg:px-0"
    >
      <!-- Push content by 1/4th height without absolute positioning. -->
      <div class="spacer grow" />
      <main
        :id="skipToContentTargetId"
        tabindex="-1"
        class="z-10 grow-[3] space-y-4 lg:space-y-6"
      >
        <h1 class="heading-5 lg:heading-2 mb-6 lg:mb-10 lg:leading-tight">
          {{ $t("404.title") }}
        </h1>
        <p class="sr-only">{{ error }}</p>
        <p class="label-bold lg:heading-6">
          <i18n-t scope="global" keypath="404.main" tag="span">
            <template #link>
              <VLink
                class="text-current underline hover:text-current active:text-current"
                href="/"
                >Openverse</VLink
              >
            </template>
          </i18n-t>
        </p>
        <VStandaloneSearchBar route="404" @submit="handleSearch" />
      </main>
    </div>
  </div>
</template>

<script lang="ts">
import { navigateTo, useHead } from "#imports"

import { defineComponent } from "vue"

import { useSearchStore } from "~/stores/search"

import { useAnalytics } from "~/composables/use-analytics"
import { ALL_MEDIA } from "~/constants/media"
import { skipToContentTargetId } from "~/constants/window"

import VLink from "~/components/VLink.vue"
import VStandaloneSearchBar from "~/components/VHeader/VSearchBar/VStandaloneSearchBar.vue"
import VSvg from "~/components/VSvg/VSvg.vue"

export default defineComponent({
  name: "VFourOhFour",
  components: {
    VLink,
    VStandaloneSearchBar,
    VSvg,
  },
  props: ["error"],
  setup() {
    const searchStore = useSearchStore()

    const { sendCustomEvent } = useAnalytics()

    const handleSearch = (searchTerm: string) => {
      sendCustomEvent("SUBMIT_SEARCH", {
        searchType: ALL_MEDIA,
        query: searchTerm,
      })

      return navigateTo(
        searchStore.updateSearchPath({ type: ALL_MEDIA, searchTerm })
      )
    }

    useHead({
      meta: [{ hid: "theme-color", name: "theme-color", content: "#ffe033" }],
    })

    return {
      handleSearch,

      skipToContentTargetId,
    }
  },
})
</script>
