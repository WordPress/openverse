<template>
  <ul
    class="flex"
    :class="[
      mode === 'dark' ? 'text-dark-charcoal' : 'bg-dark-charcoal text-white',
      variant === 'inline'
        ? 'flex-row items-center gap-8 text-sm'
        : 'mt-3 flex-col items-end',
    ]"
  >
    <li
      v-for="page in allPages"
      :key="page.id"
      :class="{ 'heading-5': variant === 'column' }"
    >
      <VLink
        class="rounded-sm py-3 focus-visible:outline-none focus-visible:ring focus-visible:ring-pink focus-visible:ring-offset-1 focus-visible:ring-offset-tx"
        :class="[
          { 'font-bold': currentPage === page.id },
          mode === 'dark' ? 'text-dark-charcoal' : 'text-white',
          variant === 'inline' ? '' : 'ps-3',
        ]"
        :href="page.link"
        show-external-icon
        @click="onClick(page.link)"
        >{{ $t(page.name) }}</VLink
      >
    </li>
  </ul>
</template>

<script lang="ts">
import {
  type PropType,
  defineComponent,
  useRoute,
} from '@nuxtjs/composition-api'

import usePages from '~/composables/use-pages'

import VLink from '~/components/VLink.vue'

export default defineComponent({
  name: 'VPageLinks',
  components: {
    VLink,
  },
  props: {
    /**
     * In `light` mode, the links are white and the background is dark charcoal.
     * In `dark` mode (in the modal), the links are dark charcoal and the background is transparent.
     *
     * @default 'light'
     */
    mode: {
      type: String as PropType<'light' | 'dark'>,
      default: 'light',
    },
    /**
     * In `inline` mode, the links are displayed horizontally. It is used in the desktop header.
     * In `column` mode, the links are displayed vertically. It is used in the mobile modal.
     *
     * @default 'inline'
     */
    variant: {
      type: String as PropType<'inline' | 'column'>,
      default: 'inline',
    },
  },
  setup(_, { emit }) {
    const { all: allPages, current: currentPage } = usePages(true)
    const route = useRoute()

    const onClick = (link: string) => {
      if (link === route.value.path) {
        emit('close')
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
