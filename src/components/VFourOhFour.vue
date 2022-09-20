<template>
  <div
    class="error relative flex min-h-screen flex-col overflow-x-hidden bg-yellow"
  >
    <Oops
      aria-hidden="true"
      class="pointer-events-none absolute top-20 z-0 -mt-[10%] -ml-[20%] w-[140%] fill-dark-charcoal px-6 opacity-5 lg:mx-auto lg:w-full lg:px-16"
    />

    <div>
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
          :placeholder="$t('404.search-placeholder').toString()"
          :is404="true"
          size="standalone"
          @input="setSearchTerm"
          @submit="handleSearch"
        />
      </div>
    </main>

    <VFooter v-if="isNewHeaderEnabled" mode="internal" />
  </div>
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

import { useFeatureFlagStore } from '~/stores/feature-flag'

import VSearchBar from '~/components/VHeaderOld/VSearchBar/VSearchBar.vue'
import VLink from '~/components/VLink.vue'
import VBrand from '~/components/VBrand/VBrand.vue'
import VFooter from '~/components/VFooter/VFooter.vue'

import Oops from '~/assets/oops.svg?inline'

export default defineComponent({
  name: 'VFourOhFour',
  components: {
    Oops,
    VLink,
    VSearchBar,
    VBrand,
    VFooter,
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

    const featureFlagStore = useFeatureFlagStore()
    const isNewHeaderEnabled = featureFlagStore.isOn('new_header')

    return {
      searchTerm,
      setSearchTerm,
      handleSearch,
      isNewHeaderEnabled,
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
