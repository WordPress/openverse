<template>
  <VButton
    :aria-label="$t('search.search')"
    size="disabled"
    :variant="route === 'home' ? 'primary' : 'plain'"
    class="heading-6 h-full flex-shrink-0 transition-none rounded-s-none"
    :class="[
      route === 'home'
        ? 'w-[57px] whitespace-nowrap md:w-auto md:py-6 md:px-10'
        : 'search-button p-0.5px ps-1.5px hover:bg-pink hover:text-white focus-visible:bg-pink focus-visible:text-white group-focus-within:border-pink group-focus-within:bg-pink group-focus-within:text-white group-focus-within:hover:bg-dark-pink group-hover:border-pink group-hover:bg-pink group-hover:text-white',
      {
        'w-10 bg-dark-charcoal-10 md:w-12': route === 'search',
        'border-black focus:border-tx group-focus-within:border-tx group-hover:border-tx group-focus:border-tx':
          route === '404',
      },
      sizeClasses,
    ]"
  >
    <VIcon v-show="isIcon" :icon-path="searchIcon" />
    <span v-show="!isIcon">{{ $t("search.search") }}</span>
  </VButton>
</template>

<script lang="ts">
import { defineComponent, computed, PropType } from "@nuxtjs/composition-api"

import { useUiStore } from "~/stores/ui"

import VIcon from "~/components/VIcon/VIcon.vue"
import VButton from "~/components/VButton.vue"
import type { FieldSize } from "~/components/VInputField/VInputField.vue"

import searchIcon from "~/assets/icons/search.svg"
/**
 * The search button used in the search bar on the homepage and on the 404 page,
 * and on the search page.
 */
export default defineComponent({
  name: "VSearchButton",
  components: { VIcon, VButton },
  props: {
    size: {
      type: String as PropType<FieldSize>,
      required: true,
    },
    route: {
      type: String as PropType<"home" | "404" | "search">,
      validator: (v: string) => ["home", "404", "search"].includes(v),
    },
  },
  setup(props) {
    const uiStore = useUiStore()

    /**
     * The search button has a text label on the homepage with a desktop layout,
     * everywhere else it has an icon.
     */
    const isIcon = computed(() => {
      if (props.route !== "home") {
        return true
      } else {
        return !uiStore.isDesktopLayout
      }
    })

    const sizeClasses = computed(() =>
      isIcon.value
        ? {
            small: "w-10 md:w-12",
            medium: "w-12",
            large: "w-14",
            standalone: "w-[57px] md:w-[69px]",
          }[props.size]
        : undefined
    )

    return { searchIcon, sizeClasses, isIcon }
  },
})
</script>

<style scoped>
.search-button {
  border-inline-start-width: 0;
}
</style>
