<template>
  <div dir="ltr">
    <div class="hero-section border-b">
      <div class="container pt-16">
        <div class="intro text-center mx-auto">
          <h2 class="text-5xl mb-10">
            {{ $t('extension.description.intro') }}
          </h2>
        </div>
        <ExtensionBrowsers />
        <!-- eslint-disable vuejs-accessibility/media-has-caption -->
        <video
          ref="heroVid"
          class="screenshot block w-full mx-auto"
          autoplay
          loop
          muted
          @click="togglePlay"
        >
          <source
            src="~/assets/screenshots/extension_hero_vid.mp4"
            type="video/mp4"
          />
        </video>
        <!-- eslint-enable vuejs-accessibility/media-has-caption -->
      </div>
    </div>
    <div
      class="features grid grid-cols-1 tab:grid-cols-2 gap-x-12 gap-y-30 py-30 mx-auto"
    >
      <template v-for="(feature, index) in features">
        <figure
          :key="`figure-${index}`"
          :data-index="index"
          class="flex flex-col justify-center items-center"
          :style="{ '--cell-idx': index * 2 }"
        >
          <img
            class="screenshot w-full rounded border"
            :src="feature.image"
            :alt="$t(`extension.features.${feature.key}.heading`)"
          />
        </figure>
        <div
          :key="`description-${index}`"
          :data-index="index"
          class="description flex flex-col justify-center items-center"
          :style="{ '--cell-idx': index * 2 + 1 }"
        >
          <h2 class="text-5xl">
            {{ $t(`extension.features.${feature.key}.heading`) }}
          </h2>
          <p class="mt-4">
            {{ $t(`extension.features.${feature.key}.content`) }}
          </p>
        </div>
      </template>
    </div>
    <div class="section">
      <div class="container conclusion mb-24">
        <h2 class="text-center mx-auto">{{ $t('extension.conclusion') }}</h2>
        <ExtensionBrowsers class="mt-6" />
      </div>
    </div>
  </div>
</template>

<script>
import ExtensionBrowsers from '~/components/ExtensionBrowsers'

import feature1 from '~/assets/screenshots/extension_feat_1.png'
import feature2 from '~/assets/screenshots/extension_feat_2.png'
import feature3 from '~/assets/screenshots/extension_feat_3.png'

const AboutPage = {
  name: 'about-page',
  components: { ExtensionBrowsers },
  data() {
    const features = [
      { key: 'search', image: feature1 },
      { key: 'bookmark', image: feature2 },
      { key: 'use', image: feature3 },
    ]
    return {
      features,
      isPlaying: true,
    }
  },
  methods: {
    togglePlay() {
      if (this.isPlaying) {
        this.$refs.heroVid.pause()
      } else {
        this.$refs.heroVid.play()
      }
      this.isPlaying = !this.isPlaying
    },
  },
}

export default AboutPage
</script>

<style lang="scss" scoped>
$video-max-width: 1200px;
$video-actual-width: 1140px; // Video has internal padding

.hero-section {
  background-color: $color-wp-gray-0;
  border-color: $color-transition-gray;

  .container {
    .intro {
      max-width: 880px;
    }

    .screenshot {
      max-width: $video-max-width;
    }
  }
}

.features {
  max-width: $video-actual-width;

  figure,
  .description {
    order: var(--cell-idx);
    @apply text-center;

    @include from($tablet) {
      &:nth-of-type(odd) {
        @apply text-left items-start;
      }

      &:nth-of-type(even) {
        @apply text-right items-end;
      }
    }
  }

  figure {
    img {
      border-color: rgba(30, 30, 30, 0.2);
      filter: drop-shadow(0px 4px 10px rgba(0, 0, 0, 0.1))
        drop-shadow(0px 20px 33px rgba(0, 0, 0, 0.07));
      max-width: 30rem;
    }
  }

  .description {
    h2,
    p {
      max-width: 30rem;
    }
  }

  @include from($tablet) {
    // Rearrange middle row on two column layouts for zig-zag appearance
    figure[data-index='1'] {
      order: 4;
    }

    .description[data-index='1'] {
      order: 3;
    }
  }
}

.conclusion {
  h2 {
    max-width: 40rem;
  }
}
</style>
