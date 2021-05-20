<template>
  <div class="section">
    <div class="container is-fluid">
      <div>
        <h1 class="title is-2 margin-bottom-large" role="article">
          {{ $t('about.title') }}
        </h1>
        <div class="content">
          <p>{{ $t('about.description.content') }}</p>

          <i18n path="about.collection.content" tag="p">
            <template #common-crawl>
              <a
                :aria-label="$t('about.aria.common-crawl')"
                href="http://commoncrawl.org/"
                >{{ $t('about.collection.common-crawl') }}</a
              >
            </template>
          </i18n>

          <i18n path="about.planning.content" tag="p">
            <template #meta>
              <NuxtLink
                :aria-label="$t('about.aria.meta')"
                :to="localePath('/meta-search')"
                >{{ $t('about.planning.meta') }}</NuxtLink
              >
            </template>
            <template #search>
              <a
                :aria-label="$t('about.aria.search')"
                href="https://github.com/wordpress/openverse-frontend/"
                >{{ $t('about.planning.search') }}</a
              >
            </template>
            <template #api>
              <a
                :aria-label="$t('about.aria.api')"
                href="https://github.com/wordpress/openverse-api/"
                >{{ $t('about.planning.api') }}</a
              >
            </template>
            <template #catalog>
              <a
                :aria-label="$t('about.aria.catalog')"
                href="https://github.com/wordpress/openverse-catalog/"
                >{{ $t('about.planning.catalog') }}</a
              >
            </template>
            <template #community>
              <!-- TODO: Update link to team page on Make WordPress -->
              <a
                :aria-label="$t('about.aria.community')"
                href="https://make.wordpress.org/"
                >{{ $t('about.planning.community') }}</a
              >
            </template>
            <template #working>
              <a
                :aria-label="$t('about.aria.projects')"
                href="https://github.com/orgs/WordPress/projects/3"
                >{{ $t('about.planning.working') }}</a
              >
            </template>
          </i18n>

          <i18n path="about.transfer.content" tag="p">
            <template #creative-commons>
              <a
                :aria-label="$t('about.aria.creative-commons')"
                href="https://creativecommons.org/2021/05/03/cc-search-to-join-wordpress/"
                >{{ $t('about.transfer.creative-commons') }}</a
              >
            </template>
            <template #wordpress>
              <a
                :aria-label="$t('about.aria.wordpress')"
                href="https://ma.tt/2021/04/cc-search-to-join-wordpress-org/"
                >{{ $t('about.transfer.wordpress') }}</a
              >
            </template>
          </i18n>

          <i18n path="about.declaration.content" tag="p">
            <template #terms>
              <a
                :aria-label="$t('about.aria.terms')"
                href="https://creativecommons.org/terms/"
                >{{ $t('about.declaration.terms') }}</a
              >
            </template>
          </i18n>

          <h2 class="margin-top-large margin-bottom-normal">
            {{ $t('about.sources') }}
          </h2>
          <table
            :aria-label="$t('about.aria.sources')"
            role="region"
            class="table is-bordered is-striped margin-bottom-large"
          >
            <thead>
              <tr>
                <th>{{ $t('about.providers.source') }}</th>
                <th>{{ $t('about.providers.domain') }}</th>
                <th>{{ $t('about.providers.work') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(imageProvider, index) in imageProviders" :key="index">
                <td>{{ imageProvider.display_name }}</td>
                <td>
                  <a
                    :aria-label="imageProvider.display_name"
                    :href="imageProvider.source_url"
                  >
                    {{ imageProvider.source_url }}
                  </a>
                </td>
                <td class="number-cell">
                  {{ getProviderImageCount(imageProvider.image_count) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const AboutPage = {
  name: 'about-page',
  layout({ store }) {
    return store.state.isEmbedded
      ? 'embedded-with-nav-search'
      : 'with-nav-search'
  },
  computed: {
    imageProviders() {
      return this.$store.state.imageProviders
    },
  },
  methods: {
    getProviderImageCount(imageCount) {
      return imageCount.toLocaleString(this.$i18n.locale)
    },
  },
}

export default AboutPage
</script>

<style lang="scss" scoped>
@import '~/styles/text-only-page.scss';

.table.is-bordered {
  td,
  th {
    word-break: initial;
  }
}
</style>
