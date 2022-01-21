<template>
  <main
    class="flex flex-col lg:flex-row justify-center gap-6 lg:gap-0 bg-yellow h-screen overflow-hidden"
  >
    <!-- TODO: Refine min-width for different breakpoints, remove magic numbers -->
    <header
      class="flex-grow w-full lg:w-auto lg:min-w-[32rem] xl:min-w-[64rem] box-border px-6 lg:pl-30 lg:pr-0 xl:px-40 mx-auto flex flex-col justify-center"
    >
      <NuxtLink to="/" class="relative z-10">
        <h1>
          <span class="sr-only">{{ $t('hero.brand') }}</span>
          <!-- width and height chosen w.r.t. viewBox "0 0 280 42" -->
          <OpenverseLogo
            aria-hidden="true"
            class="lg:-translate-x-24 w-30 lg:h-[63px] lg:w-auto pt-6 lg:pt-0"
          />
        </h1>
      </NuxtLink>

      <h2 class="text-4xl lg:text-6xl mt-auto lg:mt-6">
        {{ $t('hero.subtitle') }}
      </h2>
      <VSearchBar
        v-model.trim="searchTerm"
        class="max-w-[40rem] mt-4 lg:mt-8"
        :placeholder="featuredSearchText"
        @submit="handleSearch"
      >
        <VContentSwitcherPopover
          v-if="isMounted && isMinScreenMd"
          ref="contentSwitcher"
          class="mx-3"
          :active-item="contentType"
          @select="setContentType"
        />
      </VSearchBar>

      <!-- Disclaimer for large screens -->
      <i18n
        path="hero.disclaimer.content"
        tag="p"
        class="hidden lg:block text-sr mt-4"
      >
        <template #license>
          <a
            href="https://creativecommons.org/licenses/"
            class="text-dark-charcoal hover:text-dark-charcoal underline"
            >{{ $t('hero.disclaimer.license') }}</a
          >
        </template>
      </i18n>
    </header>

    <!-- Image carousel -->
    <div class="flex-grow overflow-hidden w-full lg:w-auto lg:h-full px-6">
      <!-- Height is 114.286vh i.e. 100vh * 8/7 (so that 0.75, 1, 1, 0.75 circles are visible) -->
      <!-- Width is 57.143vh i.e. half of height (because grid dimensions are 4 ⨯ 2) -->
      <div
        class="homepage-images flex flex-row gap-4 lg:gap-0 items-center lg:grid lg:grid-cols-2 lg:grid-rows-4 lg:w-[57.143vh] lg:h-[114.286vh]"
      >
        <Transition
          v-for="(image, index) in featuredSearchImages"
          :key="image.identifier"
          name="fade"
          mode="out-in"
          appear
        >
          <NuxtLink
            :key="image.identifier"
            :to="image.url"
            class="homepage-image block aspect-square h-30 w-30 lg:h-auto lg:w-auto lg:m-[2vh] rounded-full"
            :style="{ '--transition-index': `${index * 0.05}s` }"
          >
            <img
              class="object-cover h-full w-full rounded-full"
              :src="image.src"
              :alt="image.title"
              :title="image.title"
            />
          </NuxtLink>
        </Transition>
      </div>
    </div>

    <!-- Disclaimer as footer for small screens -->
    <i18n
      path="hero.disclaimer.content"
      tag="p"
      class="lg:hidden text-sr p-6 mt-auto"
    >
      <template #license>
        <a
          href="https://creativecommons.org/licenses/"
          class="text-dark-charcoal hover:text-dark-charcoal underline"
          >{{ $t('hero.disclaimer.license') }}</a
        >
      </template>
    </i18n>
  </main>
</template>

<script>
import {
  ref,
  onMounted,
  onBeforeUnmount,
  useRouter,
  useStore,
  useContext,
} from '@nuxtjs/composition-api'

import VContentSwitcherPopover from '~/components/VContentSwitcher/VContentSwitcherPopover.vue'

import { isMinScreen } from '~/composables/use-media-query'

import { ALL_MEDIA } from '~/constants/media'
import { MEDIA, SEARCH } from '~/constants/store-modules'
import { FETCH_MEDIA, UPDATE_QUERY } from '~/constants/action-types'

import imageInfo from '~/assets/homepage_images/image_info.json'

import OpenverseLogo from '~/assets/logo.svg?inline'

const HomePage = {
  name: 'home-page',
  layout: 'blank',
  components: {
    OpenverseLogo,
    VContentSwitcherPopover,
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
  setup() {
    const { app } = useContext()
    const router = useRouter()
    const store = useStore()

    const featuredSearches = imageInfo.sets.map((setItem) => ({
      ...setItem,
      images: setItem.images.map((imageItem) => ({
        ...imageItem,
        src: require(`~/assets/homepage_images/${setItem.prefix}-${imageItem.index}.jpg`),
        url: router.resolve({
          name: 'image-id',
          params: { id: imageItem.identifier },
        }).href,
      })),
    }))

    const featuredSearchIdx = ref(-1) // immediately updates to 0 on mount
    const nextIdx = () => {
      featuredSearchIdx.value =
        (featuredSearchIdx.value + 1) % featuredSearches.length
      const featuredSearch = featuredSearches[featuredSearchIdx.value]
      typeText(featuredSearch.term, () => {
        setImages(featuredSearch.images)
      })
    }

    const rotationTime = 6e3 // ms
    let rotInterval = null
    onMounted(() => {
      nextIdx()
      rotInterval = setInterval(nextIdx, rotationTime)
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
          rotInterval = setInterval(nextIdx, rotationTime)
        } else if (document.visibilityState === 'hidden' && rotInterval) {
          clearInterval(rotInterval)
        }
      })
    })
    onBeforeUnmount(() => {
      if (rotInterval) {
        clearInterval(rotInterval)
      }
    })

    const featuredSearchText = ref('')
    const keystrokeTime = 100 // ms
    const typeText = (text, callback) => {
      let length = 0
      const typeInterval = setInterval(() => {
        length += 1
        featuredSearchText.value = text.substring(0, length)
        if (length === text.length) {
          clearInterval(typeInterval)
          callback()
        }
      }, keystrokeTime)
    }

    const featuredSearchImages = ref([])
    const setImages = (images) => {
      featuredSearchImages.value = images
    }

    const isMounted = ref(false)
    onMounted(() => {
      isMounted.value = true
    })
    onBeforeUnmount(() => {
      isMounted.value = false
    })

    const isMinScreenMd = isMinScreen('md', { shouldPassInSSR: true })

    const contentSwitcher = ref(null)
    const contentType = ref(ALL_MEDIA)

    const setContentType = async (type) => {
      contentType.value = type
      contentSwitcher.value?.closeMenu()
      await store.dispatch(`${SEARCH}/${UPDATE_QUERY}`, {
        searchType: type,
      })
    }

    const searchTerm = ref('')
    const handleSearch = async () => {
      await store.dispatch(`${SEARCH}/${UPDATE_QUERY}`, {
        q: searchTerm.value || featuredSearches[featuredSearchIdx.value].term,
        searchType: contentType.value,
      })
      const newPath = app.localePath({
        path: `/search/${
          contentType.value === ALL_MEDIA ? '' : contentType.value
        }`,
        query: store.getters['search/searchQueryParams'],
      })
      router.push(newPath)

      await store.dispatch(`${MEDIA}/${FETCH_MEDIA}`, {
        ...store.getters['search/searchQueryParams'],
      })
    }

    return {
      featuredSearchText,
      featuredSearchImages,

      isMounted,

      isMinScreenMd,

      contentSwitcher,
      contentType,
      setContentType,

      searchTerm,
      handleSearch,
    }
  },
}

export default HomePage
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
