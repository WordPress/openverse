<template>
  <header
    class="flex w-full flex-grow flex-col justify-between lg:w-auto lg:min-w-[32rem] lg:justify-center xl:min-w-[64rem]"
  >
    <VLogoButtonOld
      class="ms-3 lg:hidden"
      :auto-resize-logo="false"
      :is-search-route="false"
    />

    <div class="z-10 mx-auto w-full px-6 lg:w-auto lg:pe-0 lg:ps-24">
      <VLink href="/" class="hidden text-dark-charcoal lg:block">
        <!-- eslint-disable vuejs-accessibility/heading-has-content -->
        <h1>
          <VBrand class="text-[46px]" />
        </h1>
        <!-- eslint-enable vuejs-accessibility/heading-has-content -->
      </VLink>
      <h2
        class="mt-auto mb-2 max-w-[80%] text-[27px] font-normal leading-[35px] md:mt-16 md:mb-4 md:text-[46px] md:leading-[60px]"
      >
        {{ $t("hero.subtitle") }}
      </h2>

      <p class="text-base md:text-3xl">
        {{ $t("hero.description") }}
      </p>

      <div class="mt-8 flex justify-start gap-4 md:hidden">
        <VSearchTypeRadio
          v-for="type in supportedSearchTypes"
          :key="type"
          :search-type="type"
          :selected="type === searchType"
          @select="setSearchType"
        />
      </div>
      <VStandaloneSearchBarOld
        class="mt-4 max-w-[40rem] md:mt-6"
        @submit="handleSearch"
      >
        <VSearchTypePopoverOld
          v-show="isDesktopLayout"
          ref="contentSwitcher"
          class="mx-3 group-focus-within:bg-white group-hover:bg-white"
          :active-item="searchType"
          placement="searchbar"
          @select="setSearchType"
        />
      </VStandaloneSearchBarOld>

      <!-- Disclaimer for large screens -->
      <i18n
        path="hero.disclaimer.content"
        tag="p"
        class="mt-4 hidden text-sr lg:block"
      >
        <template #openverse>Openverse</template>
        <template #license>
          <VLink
            href="https://creativecommons.org/licenses/"
            class="text-dark-charcoal underline hover:text-dark-charcoal"
            >{{ $t("hero.disclaimer.license") }}</VLink
          >
        </template>
      </i18n>
    </div>
  </header>
</template>
<script lang="ts">
import { PropType } from "@nuxtjs/composition-api"

import { SearchType, supportedSearchTypes } from "~/constants/media"

import VBrand from "~/components/VBrand/VBrand.vue"
import VLink from "~/components/VLink.vue"
import VLogoButtonOld from "~/components/VHeaderOld/VLogoButtonOld.vue"
import VSearchTypePopoverOld from "~/components/VContentSwitcherOld/VSearchTypePopoverOld.vue"
import VSearchTypeRadio from "~/components/VContentSwitcher/VSearchTypeRadio.vue"
import VStandaloneSearchBarOld from "~/components/VHeaderOld/VSearchBar/VStandaloneSearchBarOld.vue"

export default {
  name: "VOldHomepageContent",
  components: {
    VBrand,
    VLink,
    VLogoButtonOld,
    VSearchTypePopoverOld,
    VSearchTypeRadio,
    VStandaloneSearchBarOld,
  },
  props: {
    handleSearch: {
      type: Function as PropType<(query: string) => void>,
      required: true,
    },
    isDesktopLayout: {
      type: Boolean,
      required: true,
    },
    searchType: {
      type: String as PropType<SearchType>,
      required: true,
    },
    setSearchType: {
      type: Function as PropType<(type: SearchType) => void>,
      required: true,
    },
  },
  setup() {
    return {
      supportedSearchTypes,
    }
  },
}
</script>
<style>
@screen lg {
}
</style>
