<template>
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
</template>
<script lang="ts">
import { useContext, useRouter } from "@nuxtjs/composition-api"

import VLink from "~/components/VLink.vue"

import imageInfo from "~/assets/homepage_images/image_info.json"

export default {
  name: "VImageCarousel",
  components: {
    VLink,
  },
  props: {
    isNewHeaderEnabled: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const router = useRouter()
    const { app } = useContext()

    const featuredSearches = imageInfo.sets.map((setItem) => ({
      ...setItem,
      images: setItem.images
        .map((imageItem) => ({
          ...imageItem,
          src: require(`~/assets/homepage_images/${setItem.key}/${imageItem.index}.png`),
          url: router.resolve(
            app.localePath({
              name: "image-id",
              params: { id: imageItem.identifier },
            })
          ).href,
        }))
        .slice(0, 7),
    }))

    const featuredSearchIdx = Math.floor(Math.random() * 3)
    const featuredSearch = featuredSearches[featuredSearchIdx]

    return {
      featuredSearch,
    }
  },
}
</script>
<style>
@screen lg {
  .homepage-image:nth-child(even) {
    transform: translateY(50%);
  }
}

.homepage-image {
  transition-delay: var(--transition-index) !important;
}
</style>
