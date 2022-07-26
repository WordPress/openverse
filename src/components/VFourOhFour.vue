<template>
  <main class="page-404 relative h-screen overflow-x-hidden bg-yellow">
    <VLink href="/" class="relative z-10 text-dark-charcoal">
      <span class="sr-only">Openverse</span>
      <span
        class="flex h-auto w-30 flex-row pt-6 text-dark-charcoal ms-6 lg:pt-8 lg:ms-10"
        aria-hidden="true"
      >
        <OpenverseLogo />
        <OpenverseBrand class="ms-1" />
      </span>
    </VLink>
    <Oops
      aria-hidden="true"
      class="pointer-events-none absolute z-0 -mt-[10%] -ml-[20%] w-[140%] fill-dark-charcoal px-6 opacity-5 lg:mx-auto lg:w-full lg:px-16"
    />
    <header
      class="absolute top-1/4 left-0 right-0 z-10 mx-auto space-y-4 px-6 lg:max-w-2xl lg:space-y-6 lg:px-0"
    >
      <h1 class="mb-6 text-3xl lg:mb-10 lg:text-6xl lg:leading-tight">
        {{ $t('404.title') }}
      </h1>
      <p class="font-semibold">
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
      <VSearchBar
        :value="searchTerm"
        :label-text="$t('404.search-placeholder')"
        field-id="404-search"
        :placeholder="$t('404.search-placeholder')"
        size="standalone"
        @input="setSearchTerm"
        @submit="handleSearch"
      />
    </header>
  </main>
</template>

<script>
import {
  defineComponent,
  ref,
  useContext,
  useRouter,
} from '@nuxtjs/composition-api'

import { useMediaStore } from '~/stores/media'
import { useSearchStore } from '~/stores/search'

import VSearchBar from '~/components/VHeader/VSearchBar/VSearchBar.vue'
import VLink from '~/components/VLink.vue'

import Oops from '~/assets/oops.svg?inline'
import OpenverseLogo from '~/assets/logo.svg?inline'
import OpenverseBrand from '~/assets/brand.svg?inline'

export default defineComponent({
  name: 'VFourOhFour',
  components: {
    OpenverseLogo,
    OpenverseBrand,
    Oops,
    VLink,
    VSearchBar,
  },
  props: ['error'],
  setup() {
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()
    const { app } = useContext()
    const router = useRouter()

    const searchTerm = ref('')
    const setSearchTerm = (value) => {
      searchTerm.value = value
    }

    const handleSearch = async () => {
      if (searchTerm.value === '') return

      searchStore.setSearchTerm(searchTerm.value)
      await mediaStore.fetchMedia()

      router.push(
        app.localePath({
          path: `/search`,
          query: { q: searchTerm.value },
        })
      )
    }

    return {
      searchTerm,
      setSearchTerm,
      handleSearch,
    }
  },
  head: {
    meta: [
      {
        hid: 'theme-color',
        name: 'theme-color',
        content: '#ffe033',
      },
    ],
  },
})
</script>

<style>
/* Override the default search bar styles.
   Maybe in the future this would warrant a
   variant of the searchbar, but that seems
   excessive for this one-off usage.
*/
.page-404 .search-bar > div:not(:focus):not(:focus-within) {
  border-color: black;
}
.page-404
  .search-bar:not(:hover)
  button:not(:hover):not(:focus):not(:focus-within) {
  border-color: black;
  border-inline-start-color: transparent;
}
.page-404 .search-bar button {
  border-width: 1px;
}
</style>
