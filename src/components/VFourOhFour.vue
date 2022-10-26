<template>
  <div
    class="error relative flex min-h-screen flex-col overflow-x-hidden bg-yellow"
  >
    <svg
      class="pointer-events-none absolute top-20 z-0 -mt-[10%] -ml-[20%] w-[140%] fill-dark-charcoal px-6 opacity-5 lg:mx-auto lg:ml-0 lg:w-full lg:px-16"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 1320 569"
      aria-hidden="true"
      focusable="false"
    >
      <use :href="`${Oops}#oops`" />
    </svg>
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
        <h1 class="heading-5 lg:heading-2 mb-6 lg:mb-10 lg:leading-tight">
          {{ $t('404.title') }}
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
        <VStandaloneSearchBarOld route="404" @submit="handleSearch" />
      </div>
    </main>

    <VFooter
      v-if="isNewHeaderEnabled"
      mode="internal"
      :language-props="{ variant: 'yellow' }"
    />
  </div>
</template>

<script>
import { defineComponent, useContext, useRouter } from '@nuxtjs/composition-api'

import { useSearchStore } from '~/stores/search'

import { useFeatureFlagStore } from '~/stores/feature-flag'

import { ALL_MEDIA, searchPath } from '~/constants/media'

import VStandaloneSearchBarOld from '~/components/VHeaderOld/VSearchBar/VStandaloneSearchBarOld.vue'
import VLink from '~/components/VLink.vue'
import VBrand from '~/components/VBrand/VBrand.vue'
import VFooter from '~/components/VFooter/VFooter.vue'

import Oops from '~/assets/oops.svg'

export default defineComponent({
  name: 'VFourOhFour',
  components: {
    VLink,
    VStandaloneSearchBarOld,
    VBrand,
    VFooter,
  },
  props: ['error'],
  setup() {
    const searchStore = useSearchStore()
    const { app } = useContext()
    const router = useRouter()

    const handleSearch = async (searchTerm) => {
      if (!searchTerm) return

      searchStore.setSearchTerm(searchTerm.value)
      searchStore.setSearchType(ALL_MEDIA)

      router.push(
        app.localePath({
          path: searchPath(ALL_MEDIA),
          query: { q: searchTerm.value },
        })
      )
    }

    const featureFlagStore = useFeatureFlagStore()
    const isNewHeaderEnabled = featureFlagStore.isOn('new_header')

    return {
      handleSearch,
      isNewHeaderEnabled,
      Oops,
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
</style>
