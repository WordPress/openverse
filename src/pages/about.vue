<template>
  <div class="section" dir="ltr">
    <div class="container">
      <div>
        <h1 class="text-5xl mb-10">
          {{ $t('about.title') }}
        </h1>
        <div class="content">
          <p>{{ $t('about.description.content') }}</p>

          <i18n path="about.collection.content" tag="p">
            <template #common-crawl>
              <VLink
                :aria-label="$t('about.aria.common-crawl')"
                href="http://commoncrawl.org/"
                >{{ $t('about.collection.common-crawl') }}</VLink
              >
            </template>
          </i18n>

          <i18n path="about.planning.content" tag="p">
            <template #meta>
              <VLink :aria-label="$t('about.aria.meta')" href="/meta-search">{{
                $t('about.planning.meta')
              }}</VLink>
            </template>
            <template #search>
              <VLink
                :aria-label="$t('about.aria.search')"
                href="https://github.com/wordpress/openverse-frontend/"
                >{{ $t('about.planning.search') }}</VLink
              >
            </template>
            <template #api>
              <VLink
                :aria-label="$t('about.aria.api')"
                href="https://github.com/wordpress/openverse-api/"
                >{{ $t('about.planning.api') }}</VLink
              >
            </template>
            <template #catalog>
              <VLink
                :aria-label="$t('about.aria.catalog')"
                href="https://github.com/wordpress/openverse-catalog/"
                >{{ $t('about.planning.catalog') }}</VLink
              >
            </template>
            <template #community>
              <VLink
                :aria-label="$t('about.aria.community')"
                href="https://make.wordpress.org/openverse/"
                >{{ $t('about.planning.community') }}</VLink
              >
            </template>
            <template #working>
              <VLink
                :aria-label="$t('about.aria.projects')"
                href="https://github.com/orgs/WordPress/projects/3"
                >{{ $t('about.planning.working') }}</VLink
              >
            </template>
          </i18n>

          <i18n path="about.transfer.content" tag="p">
            <template #creative-commons>
              <VLink
                :aria-label="$t('about.aria.creative-commons')"
                href="https://creativecommons.org/2021/05/03/cc-search-to-join-wordpress/"
                >{{ $t('about.transfer.creative-commons') }}</VLink
              >
            </template>
            <template #wordpress>
              <VLink
                :aria-label="$t('about.aria.wordpress')"
                href="https://ma.tt/2021/04/cc-search-to-join-wordpress-org/"
                >{{ $t('about.transfer.wordpress') }}</VLink
              >
            </template>
          </i18n>

          <i18n path="about.declaration.content" tag="p">
            <template #terms>
              <VLink
                :aria-label="$t('about.aria.terms')"
                href="https://creativecommons.org/terms/"
                >{{ $t('about.declaration.terms') }}</VLink
              >
            </template>
          </i18n>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import VLink from '~/components/VLink.vue'
import { defineComponent } from '@nuxtjs/composition-api'

const AboutPage = defineComponent({
  name: 'AboutPage',
  components: { VLink },
  head() {
    return {
      title: `${this.$t('about.title')} | ${this.$t('hero.brand')}`,
    }
  },
})

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
