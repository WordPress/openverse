<template>
  <main
    class="flex h-screen flex-col justify-center gap-6 overflow-hidden bg-yellow lg:flex-row lg:gap-0"
  >
    <!-- TODO: Refine min-width for different breakpoints, remove magic numbers -->
    <header
      class="box-border flex w-full flex-grow flex-col justify-between lg:w-auto lg:min-w-[32rem] lg:justify-center xl:min-w-[64rem]"
    >
      <VLogoButton
        class="ms-3 lg:hidden"
        :auto-resize-logo="false"
        :is-search-route="false"
      />

      <div class="z-10 mx-auto w-full px-6 lg:w-auto lg:pe-0 lg:ps-30 xl:px-40">
        <VLink
          href="/"
          class="relative -left-[6.25rem] hidden rtl:-right-[6.25rem] lg:block"
        >
          <h1>
            <span class="sr-only">Openverse</span>
            <!-- width and height chosen w.r.t. viewBox "0 0 280 42" -->
            <span
              aria-hidden="true"
              class="flex flex-row items-center text-dark-charcoal"
            >
              <OpenverseLogo class="h-[70px] w-[70px] me-6 xl:me-7" />
              <OpenverseBrand class="h-[60px] w-[315px]" />
            </span>
          </h1>
        </VLink>
        <h2 class="mt-auto text-4xl lg:mt-6 lg:text-6xl">
          {{ $t('hero.subtitle') }}
        </h2>
        <div class="mt-4 flex justify-start gap-4 md:hidden">
          <VSearchTypeRadio
            v-for="type in supportedSearchTypes"
            :key="type"
            :search-type="type"
            :selected="type === searchType"
            @select="setSearchType"
          />
        </div>
        <VSearchBar
          v-model.trim="searchTerm"
          class="group mt-4 max-w-[40rem] lg:mt-8"
          size="standalone"
          @submit="handleSearch"
        >
          <ClientOnly>
            <VSearchTypePopover
              v-if="isMinScreenMd"
              ref="contentSwitcher"
              class="mx-3"
              :active-item="searchType"
              placement="searchbar"
              @select="setSearchType"
            />
          </ClientOnly>
        </VSearchBar>

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
              >{{ $t('hero.disclaimer.license') }}</VLink
            >
          </template>
        </i18n>
      </div>
    </header>

    <!-- Image carousel -->
    <div
      class="w-full flex-grow overflow-hidden px-6 lg:h-full lg:w-auto"
      data-testid="image-carousel"
    >
      <!-- Height is 114.286vh i.e. 100vh * 8/7 (so that 0.75, 1, 1, 0.75 circles are visible) -->
      <!-- Width is 57.143vh i.e. half of height (because grid dimensions are 4 ⨯ 2) -->
      <div
        class="homepage-images flex min-h-[120px] flex-row items-center gap-4 lg:grid lg:h-[114.286vh] lg:w-[57.143vh] lg:grid-cols-2 lg:grid-rows-4 lg:gap-0"
        aria-hidden
      >
        <ClientOnly>
          <Transition
            v-for="(image, index) in featuredSearch.images"
            :key="image.identifier"
            name="fade"
            mode="out-in"
            appear
          >
            <VLink
              :href="image.url"
              class="homepage-image block aspect-square h-30 w-30 rounded-full lg:m-[2vh] lg:h-auto lg:w-auto"
              :style="{ '--transition-index': `${index * 0.05}s` }"
            >
              <img
                class="aspect-square h-full w-full rounded-full object-cover"
                :src="image.src"
                :alt="image.title"
                width="120"
                height="120"
                :title="image.title"
              />
            </VLink>
          </Transition>
        </ClientOnly>
      </div>
    </div>

    <!-- Disclaimer as footer for small screens -->
    <i18n
      path="hero.disclaimer.content"
      tag="p"
      class="mt-auto p-6 text-sr lg:hidden"
    >
      <template #openverse>Openverse</template>
      <template #license>
        <VLink
          href="https://creativecommons.org/licenses/"
          class="text-dark-charcoal underline hover:text-dark-charcoal"
          >{{ $t('hero.disclaimer.license') }}</VLink
        >
      </template>
    </i18n>
  </main>
</template>

<script lang="ts">
import {
  defineComponent,
  onMounted,
  ref,
  useContext,
  useRouter,
} from '@nuxtjs/composition-api'

import { ALL_MEDIA, searchPath, supportedSearchTypes } from '~/constants/media'
import { isMinScreen } from '~/composables/use-media-query'

import { useMediaStore } from '~/stores/media'
import { useSearchStore } from '~/stores/search'

import VLink from '~/components/VLink.vue'
import VLogoButton from '~/components/VHeader/VLogoButton.vue'
import VSearchBar from '~/components/VHeader/VSearchBar/VSearchBar.vue'
import VSearchTypeRadio from '~/components/VContentSwitcher/VSearchTypeRadio.vue'
import VSearchTypePopover from '~/components/VContentSwitcher/VSearchTypePopover.vue'

import imageInfo from '~/assets/homepage_images/image_info.json'
import OpenverseLogo from '~/assets/logo.svg?inline'
import OpenverseBrand from '~/assets/brand.svg?inline'

export default defineComponent({
  name: 'HomePage',
  components: {
    OpenverseLogo,
    OpenverseBrand,
    VSearchTypePopover,
    VSearchTypeRadio,
    VSearchBar,
    VLink,
    VLogoButton,
  },
  layout: 'blank',
  setup() {
    const { app } = useContext()
    const router = useRouter()
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    /**
     * Reset the search type, search term and filters when the user navigates [back] to the homepage.
     */
    onMounted(() => {
      searchStore.$reset()
      mediaStore.$reset()
    })

    const featuredSearches = imageInfo.sets.map((setItem) => ({
      ...setItem,
      images: setItem.images.map((imageItem) => ({
        ...imageItem,
        src: require(`~/assets/homepage_images/${setItem.prefix}-${imageItem.index}.jpg`),
        url: router.resolve(
          app.localePath({
            name: 'image-id',
            params: { id: imageItem.identifier },
          })
        ).href,
      })),
    }))

    const featuredSearchIdx = Math.floor(Math.random() * 3)
    const featuredSearch = featuredSearches[featuredSearchIdx]

    const isMinScreenMd = isMinScreen('md', { shouldPassInSSR: true })

    const contentSwitcher = ref(null)
    const searchType = ref(ALL_MEDIA)

    const setSearchType = (type) => {
      searchType.value = type
      contentSwitcher.value?.closeMenu()
      useSearchStore().setSearchType(type)
    }

    const searchTerm = ref('')
    const handleSearch = async () => {
      if (!searchTerm.value) return
      searchStore.setSearchTerm(searchTerm.value)
      searchStore.setSearchType(searchType.value)
      const query = searchStore.searchQueryParams
      const newPath = app.localePath({
        path: searchPath(searchType.value),
        query,
      })
      router.push(newPath)
    }

    return {
      featuredSearch,

      isMinScreenMd,

      contentSwitcher,
      searchType,
      setSearchType,
      supportedSearchTypes,

      searchTerm,
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
@screen lg {
  .homepage-images {
    transform: translateY(-7.143vh);
  }

  .homepage-image:nth-child(even) {
    transform: translateY(50%);
  }
}

.homepage-image {
  transition-delay: var(--transition-index) !important;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: 0.5s;
}
</style>
