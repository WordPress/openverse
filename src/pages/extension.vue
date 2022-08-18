<template>
  <section dir="ltr">
    <div class="border-b border-dark-charcoal-30 bg-dark-charcoal-06">
      <div class="flex flex-col items-center pt-20">
        <h1 class="mb-10 max-w-[700px] text-center text-5xl md:text-5xl">
          {{ $t('extension.description.intro') }}
        </h1>
        <ExtensionBrowsers class="mb-16" />
        <video
          ref="heroVid"
          class="block w-full max-w-7xl"
          autoplay
          loop
          muted
          @click="togglePlay"
          @keyup.enter="togglePlay"
        >
          <source
            src="~/assets/screenshots/extension_hero_vid.mp4"
            type="video/mp4"
          />
        </video>
      </div>
    </div>
    <div
      class="features mx-auto grid grid-cols-1 gap-x-12 gap-y-30 py-30 md:max-w-3xl md:grid-cols-2 md:px-6 lg:max-w-6xl"
    >
      <template v-for="(feature, index) in features">
        <figure
          :key="`figure-${index}`"
          :data-index="index"
          class="flex flex-col items-center justify-center"
          :style="{ '--cell-idx': index * 2 }"
        >
          <img
            class="w-full max-w-7xl rounded border"
            :src="feature.image"
            :alt="$t(`extension.features.${feature.key}.heading`).toString()"
          />
        </figure>
        <div
          :key="`description-${index}`"
          :data-index="index"
          class="description flex flex-col items-center justify-center text-left"
          :style="{ '--cell-idx': index * 2 + 1 }"
        >
          <h2 class="max-w=[30rem] mb-4 text-5xl md:text-5xl">
            {{ $t(`extension.features.${feature.key}.heading`) }}
          </h2>
          <p class="max-w=[30rem]">
            {{ $t(`extension.features.${feature.key}.content`) }}
          </p>
        </div>
      </template>
    </div>
    <div class="mb-30 flex flex-col items-center">
      <h2 class="max-w-[40rem] text-center text-6xl md:text-6xl">
        {{ $t('extension.conclusion') }}
      </h2>
      <ExtensionBrowsers class="mt-6" />
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent, ref } from '@nuxtjs/composition-api'

import ExtensionBrowsers from '~/components/ExtensionBrowsers.vue'

import feature1 from '~/assets/screenshots/extension_feat_1.png'
import feature2 from '~/assets/screenshots/extension_feat_2.png'
import feature3 from '~/assets/screenshots/extension_feat_3.png'

export default defineComponent({
  name: 'AboutPage',
  components: { ExtensionBrowsers },
  setup() {
    const heroVid = ref<HTMLVideoElement>()
    const features = [
      { key: 'search', image: feature1 },
      { key: 'bookmark', image: feature2 },
      { key: 'use', image: feature3 },
    ]
    const isPlaying = ref(true)

    const togglePlay = () => {
      if (isPlaying.value) {
        heroVid.value?.pause()
      } else {
        heroVid.value?.play()
      }
      isPlaying.value = !isPlaying.value
    }
    return { heroVid, togglePlay, features, isPlaying }
  },
  head() {
    return {
      title: `${this.$t('extension.title')} | Openverse`,
    }
  },
})
</script>

<style scoped>
.features figure,
.features .description {
  order: var(--cell-idx);
  @apply text-center;
}

@screen md {
  .features figure:nth-of-type(odd),
  .features .description:nth-of-type(odd) {
    @apply items-start text-left;
  }

  .features figure:nth-of-type(even),
  .features .description:nth-of-type(even) {
    @apply items-end text-right;
  }
}

figure img {
  border-color: rgba(30, 30, 30, 0.2);
  filter: drop-shadow(0px 4px 10px rgba(0, 0, 0, 0.1))
    drop-shadow(0px 20px 33px rgba(0, 0, 0, 0.07));
  max-width: 30rem;
}

@screen md {
  /** Rearrange middle row on two column layouts for zig-zag appearance **/
  figure[data-index='1'] {
    order: 4;
  }

  .description[data-index='1'] {
    order: 3;
  }
}
</style>
