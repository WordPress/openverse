<template>
  <ul
    :class="
      mode === 'light' ? 'text-dark-charcoal' : 'bg-dark-charcoal text-white'
    "
  >
    <VNavLink
      v-for="page in allPages"
      :key="page.id"
      :link="page.link"
      :mode="mode"
      :is-active="currentPage === page.id"
      :class="navLinkClasses"
      @click="onClick(page.link)"
      >{{ $t(page.name) }}</VNavLink
    >
  </ul>
</template>

<script lang="ts">
import {
  type PropType,
  defineComponent,
  useRoute,
} from "@nuxtjs/composition-api"

import usePages from "~/composables/use-pages"

import VNavLink from "~/components/VNavLink/VNavLink.vue"

export default defineComponent({
  name: "VPageLinks",
  components: {
    VNavLink,
  },
  props: {
    /**
     * In `dark` mode (in the modal), the links are white and the background is dark charcoal.
     * In `light` mode, the links are dark charcoal and the background is transparent.
     *
     * @default 'light'
     */
    mode: {
      type: String as PropType<"light" | "dark">,
      default: "light",
    },
    /**
     * Pass the tailwind classes to style the nav links.
     *
     * @default ''
     */
    navLinkClasses: {
      type: String,
      default: "",
    },
  },
  setup(_, { emit }) {
    const { all: allPages, current: currentPage } = usePages(true)
    const route = useRoute()

    const onClick = (link: string) => {
      if (link === route.value.path) {
        emit("close")
      }
    }

    return {
      allPages,
      currentPage,
      onClick,
    }
  },
})
</script>
