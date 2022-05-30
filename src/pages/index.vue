<template>
  <main
    class="flex flex-col lg:flex-row justify-center gap-6 lg:gap-0 bg-yellow h-screen overflow-hidden"
  >
    <!-- TODO: Refine min-width for different breakpoints, remove magic numbers -->
    <header
      class="flex-grow w-full lg:w-auto lg:min-w-[32rem] xl:min-w-[64rem] box-border flex flex-col justify-between lg:justify-center"
    >
      <VLogoButton
        class="lg:hidden ms-3"
        :auto-resize-logo="false"
        :is-search-route="false"
      />

      <div class="px-6 lg:ps-30 lg:pe-0 xl:px-40 mx-auto w-full lg:w-auto z-10">
        <VLink
          href="/"
          class="relative hidden lg:block -left-[6.25rem] rtl:-right-[6.25rem]"
        >
          <h1>
            <span class="sr-only">Openverse</span>
            <!-- width and height chosen w.r.t. viewBox "0 0 280 42" -->
            <span
              aria-hidden="true"
              class="flex flex-row items-center text-dark-charcoal"
            >
              <OpenverseLogo class="w-[70px] h-[70px] me-6 xl:me-7" />
              <OpenverseBrand class="w-[315px] h-[60px]" />
            </span>
          </h1>
        </VLink>
        <h2 class="text-4xl lg:text-6xl mt-auto lg:mt-6">
          {{ $t('hero.subtitle') }}
        </h2>
        <div class="flex justify-start gap-4 mt-4 md:hidden">
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
          class="max-w-[40rem] mt-4 lg:mt-8 group h-[57px] md:h-[69px]"
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
          class="hidden lg:block text-sr mt-4"
        >
          <template #openverse>Openverse</template>
          <template #license>
            <VLink
              href="https://creativecommons.org/licenses/"
              class="text-dark-charcoal hover:text-dark-charcoal underline"
              >{{ $t('hero.disclaimer.license') }}</VLink
            >
          </template>
        </i18n>
      </div>
    </header>

    <!-- Image carousel -->
    <div
      class="flex-grow overflow-hidden w-full lg:w-auto lg:h-full px-6"
      data-testid="image-carousel"
    >
      <!-- Height is 114.286vh i.e. 100vh * 8/7 (so that 0.75, 1, 1, 0.75 circles are visible) -->
      <!-- Width is 57.143vh i.e. half of height (because grid dimensions are 4 ⨯ 2) -->
      <div
        class="homepage-images flex flex-row gap-4 lg:gap-0 items-center lg:grid lg:grid-cols-2 lg:grid-rows-4 lg:w-[57.143vh] lg:h-[114.286vh] min-h-[120px]"
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
              class="homepage-image block aspect-square h-30 w-30 lg:h-auto lg:w-auto lg:m-[2vh] rounded-full"
              :style="{ '--transition-index': `${index * 0.05}s` }"
            >
              <img
                class="object-cover h-full w-full rounded-full aspect-square"
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
      class="lg:hidden text-sr p-6 mt-auto"
    >
      <template #openverse>Openverse</template>
      <template #license>
        <VLink
          href="https://creativecommons.org/licenses/"
          class="text-dark-charcoal hover:text-dark-charcoal underline"
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

import { ALL_MEDIA, supportedSearchTypes } from '~/constants/media'
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
        path: `/search/${
          searchType.value === ALL_MEDIA ? '' : searchType.value
        }`,
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
