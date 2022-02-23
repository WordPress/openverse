<template>
  <div class="section" dir="ltr">
    <div class="container">
      <div>
        <h1 class="text-5xl mb-10">
          {{ $t('about.title', { openverse: 'Openverse' }) }}
        </h1>
        <div class="content">
          <p>
            {{ $t('about.description.content', { openverse: 'Openverse' }) }}
          </p>

          <i18n path="about.collection.content" tag="p">
            <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
            <template #openverse>Openverse</template>
            <template #common-crawl>
              <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
              <VLink href="https://commoncrawl.org/">Common Crawl</VLink>
            </template>
          </i18n>

          <i18n path="about.planning.content" tag="p">
            <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
            <template #openverse>Openverse</template>
            <template #meta>
              <VLink href="/meta-search">{{ $t('about.planning.meta') }}</VLink>
            </template>
            <template #search>
              <VLink href="https://github.com/wordpress/openverse-frontend/">{{
                $t('about.planning.meta')
              }}</VLink>
            </template>
            <template #api>
              <VLink href="https://github.com/wordpress/openverse-api/">{{
                $t('about.planning.api', { openverse: 'Openverse' })
              }}</VLink>
            </template>
            <template #catalog>
              <VLink href="https://github.com/wordpress/openverse-catalog/">{{
                $t('about.planning.catalog', { openverse: 'Openverse' })
              }}</VLink>
            </template>
            <template #community>
              <VLink href="https://make.wordpress.org/openverse/">{{
                $t('about.planning.community')
              }}</VLink>
            </template>
            <template #working>
              <VLink href="https://github.com/orgs/WordPress/projects/3">{{
                $t('about.planning.working')
              }}</VLink>
            </template>
          </i18n>

          <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
          <i18n path="about.transfer.content" tag="p">
            <template #openverse>Openverse</template>
            <template #creative-commons>
              <VLink
                href="https://creativecommons.org/2021/05/03/cc-search-to-join-wordpress/"
                >Creative Commons</VLink
              >
            </template>
            <template #wordpress>
              <VLink
                href="https://ma.tt/2021/04/cc-search-to-join-wordpress-org/"
                >WordPress</VLink
              >
            </template>
          </i18n>
          <!-- eslint-enable @intlify/vue-i18n/no-raw-text -->

          <i18n path="about.declaration.content" tag="p">
            <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
            <template #openverse>Openverse</template>
            <template #terms>
              <VLink href="https://creativecommons.org/terms/">{{
                $t('about.declaration.terms', { openverse: 'Openverse' })
              }}</VLink>
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
      title: `${this.$t('about.title', {
        openverse: 'Openverse',
      })} | Openverse`,
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
