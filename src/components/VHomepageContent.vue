<template>
  <div>
    <h2
      class="mt-auto mb-2 text-[40px] font-light leading-tight lg:text-[63px]"
    >
      {{ $t("hero.subtitle") }}
    </h2>

    <p class="text-base leading-relaxed">
      {{ $t("hero.description") }}
    </p>

    <VStandaloneSearchBar class="mt-4 md:mt-6" @submit="handleSearch">
      <VSearchTypePopover
        class="mx-3 group-focus-within:bg-white group-hover:bg-white"
        :active-item="searchType"
        placement="searchbar"
        @select="setSearchType"
      />
    </VStandaloneSearchBar>

    <!-- Disclaimer for large screens -->
    <i18n path="hero.disclaimer.content" tag="p" class="mt-4 text-sr">
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
</template>
<script lang="ts">
import type { SearchType } from "~/constants/media"

import VLink from "~/components/VLink.vue"
import VStandaloneSearchBar from "~/components/VHeader/VSearchBar/VStandaloneSearchBar.vue"
import VSearchTypePopover from "~/components/VContentSwitcher/VSearchTypePopover.vue"

import type { PropType } from "@nuxtjs/composition-api"

export default {
  name: "VHomepageContent",
  components: { VSearchTypePopover, VStandaloneSearchBar, VLink },
  props: {
    handleSearch: {
      type: Function as PropType<(query: string) => void>,
      required: true,
    },
    searchType: {
      type: String as PropType<SearchType>,
      required: true,
    },
    setSearchType: {
      type: Function as PropType<(searchType: SearchType) => void>,
      required: true,
    },
  },
}
</script>
<style>
@screen lg {
}
</style>
