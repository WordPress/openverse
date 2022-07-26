<template>
  <VContentPage>
    <h1>
      {{ $t('meta-search-page.title') }}
    </h1>

    <i18n path="meta-search-page.intro" tag="p">
      <template #openverse>Openverse</template>
      <template #link>
        <VLink href="/sources">{{ $t('meta-search-page.link') }}</VLink>
      </template>
    </i18n>
    <p>{{ $t('meta-search-page.license', { openverse: 'Openverse' }) }}</p>
    <h2>
      {{ $t('meta-search-page.content') }}
    </h2>
    <p>
      {{ $t('meta-search-page.content-types', { openverse: 'Openverse' }) }}
    </p>

    <h2>
      {{ $t('meta-search-page.images.title') }}
    </h2>
    <p>
      {{ $t('meta-search-page.images.content', { openverse: 'Openverse' }) }}
    </p>
    <div>
      <ol>
        <li>
          <i18n path="meta-search-page.images.continue">
            <template #load-more>
              <strong>{{ $t('browse-page.load') }}</strong>
            </template>
          </i18n>
        </li>
        <li>
          <i18n path="meta-search-page.images.not-finding">
            <template #not-finding>
              <strong>{{
                $t('meta-search.form.supported-title', { type: ' ' })
              }}</strong>
            </template>
          </i18n>
        </li>
      </ol>
    </div>
    <i18n path="meta-search-page.images.info" tag="p">
      <template #use>
        <strong>{{ $t('meta-search-page.use') }}</strong>
      </template>
      <template #not-finding>
        <strong>{{
          $t('meta-search.form.supported-title', { type: ' ' })
        }}</strong>
      </template>
    </i18n>
    <figure>
      <img
        :alt="$t('meta-search-page.images.demo-label', { type: ' ' })"
        src="~/assets/screenshots/supported.png"
        aria-hidden="true"
      />
    </figure>

    <h2>
      {{ $t('meta-search-page.audio-video.title') }}
    </h2>
    <p>
      {{
        $t('meta-search-page.audio-video.content', { openverse: 'Openverse' })
      }}
    </p>
    <i18n path="meta-search-page.audio-video.filter" tag="p">
      <template #use>
        <strong>{{ $t('meta-search-page.use') }}</strong>
      </template>
    </i18n>
    <figure>
      <img
        :alt="$t('meta-search-page.audio-video.demo-label', { type: ' ' })"
        src="~/assets/screenshots/unsupported.png"
        aria-hidden="true"
      />
    </figure>
    <h2>
      {{ $t('meta-search-page.new.title') }}
    </h2>
    <i18n path="meta-search-page.new.content" tag="p">
      <template #issue>
        <VLink
          aria-label="issue"
          href="https://github.com/WordPress/openverse-catalog/issues/new?assignees=&labels=%F0%9F%9A%A6+status%3A+awaiting+triage%2C%F0%9F%A7%B9+status%3A+ticket+work+required%2C%E2%98%81%EF%B8%8F+provider%3A+any&template=new_source_suggestion.yml&title=%3CSource+name+here%3E"
          >{{ $t('meta-search-page.new.issue') }}</VLink
        >
      </template>
      <template #email>
        <VLink aria-label="email" href="mailto:openverse@wordpress.org">{{
          $t('meta-search-page.new.email')
        }}</VLink>
      </template>
    </i18n>
    <h2>
      {{ $t('meta-search-page.why.title') }}
    </h2>
    <p>{{ $t('meta-search-page.why.content') }}</p>
    <p>
      {{ $t('meta-search-page.why.new', { openverse: 'Openverse' }) }}
    </p>
    <i18n path="meta-search-page.why.feedback-suggestions" tag="p">
      <template #feedback>
        <VLink
          :aria-label="$t('meta-search-page.why.aria-label')"
          href="/feedback"
          >{{ $t('meta-search-page.why.feedback-link') }}</VLink
        >
      </template>
    </i18n>
  </VContentPage>
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'

import VContentPage from '~/components/VContentPage.vue'
import VLink from '~/components/VLink.vue'

export default defineComponent({
  name: 'MetaSearchPage',
  components: { VContentPage, VLink },
  head() {
    return {
      title: `${this.$t('meta-search-page.title')} | Openverse`,
    }
  },
})
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
figure {
  @apply mx-auto max-w-full border border-black md:w-[800px];
}
</style>
