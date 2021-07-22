<template>
  <div>
    <div class="hero-section">
      <div :class="['container', isEmbedded ? '' : 'is-fluid']">
        <div class="intro">
          <h2 class="title is-2 margin-bottom-large">
            {{ $t('extension.description.intro') }}
          </h2>
        </div>
        <ExtensionBrowsers />
        <img
          class="screenshot"
          src="https://via.placeholder.com/1200x600"
          alt="Extension usage"
        />
      </div>
    </div>
    <div class="section">
      <div :class="['container', 'features', isEmbedded ? '' : 'is-fluid']">
        <img
          class="screenshot"
          src="https://via.placeholder.com/520x400"
          alt="WIP"
        />
        <div class="caption">
          <h2>{{ $t('extension.features.search.heading') }}</h2>
          <p class="margin-top-normal">
            {{ $t('extension.features.search.content') }}
          </p>
        </div>

        <div class="caption">
          <h2>{{ $t('extension.features.bookmark.heading') }}</h2>
          <p class="margin-top-normal">
            {{ $t('extension.features.bookmark.content') }}
          </p>
        </div>
        <img
          class="screenshot"
          src="https://via.placeholder.com/520x400"
          alt="WIP"
        />

        <img
          class="screenshot"
          src="https://via.placeholder.com/520x400"
          alt="WIP"
        />
        <div class="caption">
          <h2>{{ $t('extension.features.use.heading') }}</h2>
          <p class="margin-top-normal">
            {{ $t('extension.features.use.content') }}
          </p>
        </div>
      </div>
    </div>
    <div class="section">
      <div :class="['container', 'conclusion', isEmbedded ? '' : 'is-fluid']">
        <h2>{{ $t('extension.conclusion') }}</h2>
        <ExtensionBrowsers class="margin-top-large" />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import iframeHeight from '~/mixins/iframeHeight'

import ExtensionBrowsers from '~/components/ExtensionBrowsers.vue'

const AboutPage = {
  name: 'about-page',
  components: { ExtensionBrowsers },
  mixins: [iframeHeight],
  layout({ store }) {
    return store.state.isEmbedded
      ? 'embedded-with-nav-search'
      : 'with-nav-search'
  },
  computed: {
    ...mapState(['isEmbedded']),
  },
}

export default AboutPage
</script>

<style lang="scss" scoped>
.hero-section {
  background-color: $color-wp-gray-0;
  border-bottom: 1px solid $color-transition-gray;

  $wp-max-width: 940px;

  .container {
    padding-top: 64px;

    .intro {
      text-align: center;
      max-width: 880px;
      margin: auto;
    }

    .screenshot {
      display: block;

      position: relative;
      bottom: -1px;

      width: 100%;
      max-width: $wp-max-width;
      margin: auto;

      filter: drop-shadow(0 -4px 10px rgba(0, 0, 0, 0.1))
        drop-shadow(0 -20px 33px rgba(0, 0, 0, 0.07));

      border-radius: 0.5rem 0.5rem 0 0;
    }
  }
}

.features {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(3, auto);
  gap: 3em;

  img {
    border-radius: 0.25rem;

    filter: drop-shadow(0px 4px 10px rgba(0, 0, 0, 0.1))
      drop-shadow(0px 20px 33px rgba(0, 0, 0, 0.07));
  }

  .caption {
    display: flex;
    flex-direction: column;
    justify-content: center;

    h2,
    p {
      max-width: 30rem;
    }

    &:nth-of-type(even) {
      align-items: flex-end;

      h2,
      p {
        text-align: right;
      }
    }
  }
}

.conclusion {
  h2 {
    text-align: center;

    max-width: 40rem;
    margin: auto;
  }
}
</style>
