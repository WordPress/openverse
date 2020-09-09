<template>
  <div class="page">
    <header-section showNavSearch="true" />
    <main role="main" class="section margin-bottom-large">
      <div class="container is-fluid">
        <div class="margin-bottom-large">
          <h1 class="title is-2">
            {{ $t('meta-search-page.title') }}
          </h1>
        </div>

        <i18n
          path="meta-search-page.intro"
          tag="p"
          class="margin-bottom-normal"
        >
          <template v-slot:link>
            <a aria-label="sources" href="/sources">sources</a>
          </template>
        </i18n>
        <p>{{ $t('meta-search-page.license') }}</p>
        <h4 class="b-header">
          {{ $t('meta-search-page.content') }}
        </h4>
        <p>{{ $t('meta-search-page.content-types') }}</p>
        <h4 class="b-header">
          {{ $t('meta-search-page.images.title') }}
        </h4>
        <p>{{ $t('meta-search-page.images.content') }}</p>
        <div class="content">
          <ol>
            <li>
              {{ $t('meta-search-page.images.continue') }}
            </li>
            <li>
              {{ $t('meta-search-page.images.not-finding') }}
            </li>
          </ol>
        </div>
        <i18n
          path="meta-search-page.images.info"
          tag="p"
          class="margin-bottom-small"
        >
          <template v-slot:use>
            <strong> Use </strong>
          </template>
        </i18n>
        <figure class="image margin-vertical-large">
          <img
            src="@/assets/meta-search-images.gif"
            alt="Meta Search Images - Cars"
          />
        </figure>
        <h4 class="b-header margin-top-large">
          {{ $t('meta-search-page.audio-video.title') }}
        </h4>
        <p>{{ $t('meta-search-page.audio-video.content') }}</p>
        <i18n
          path="meta-search-page.audio-video.filter"
          tag="p"
          class="margin-vertical-small"
        >
          <template v-slot:use>
            <strong> Use </strong>
          </template>
        </i18n>
        <figure class="image margin-vertical-large">
          <img
            src="@/assets/meta-search-audio.gif"
            alt="Meta Search Audio - Drums"
          />
        </figure>
        <h4 class="b-header margin-top-large">
          {{ $t('meta-search-page.new.title') }}
        </h4>
        <i18n
          path="meta-search-page.new.content"
          tag="p"
          class="margin-bottom-small"
        >
          <template v-slot:issue>
            <a
              aria-label="issue"
              href="https://github.com/creativecommons/cccatalog/issues/new?assignees=&labels=awaiting+triage%2C+ticket+work+required%2C+providers&template=new-source-suggestion.md&title=%5BSource+Suggestion%5D+Insert+source+name+here"
              >issue</a
            >
          </template>
          <template v-slot:email>
            <a
              aria-label="email"
              href="mailto:support-search@creativecommons.org"
              >email</a
            >
          </template>
        </i18n>
        <h4 class="b-header margin-top-large">
          {{ $t('meta-search-page.why.title') }}
        </h4>
        <p>{{ $t('meta-search-page.why.content') }}</p>
        <figure class="image margin-vertical-large">
          <img
            src="@/assets/cc-meta-search.gif"
            alt="Old CC Meta Search Portal Demo"
          />
        </figure>
        <p class="margin-vertical-small">
          {{ $t('meta-search-page.why.new') }}
        </p>
        <i18n path="meta-search-page.why.feedback" tag="p">
          <template v-slot:feedback>
            <a
              aria-label="sources"
              href="https://search.creativecommons.org/feedback"
              >feedback.</a
            >
          </template>
        </i18n>
      </div>
    </main>
    <footer-section />
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection'
import FooterSection from '@/components/FooterSection'
import ServerPrefetchProvidersMixin from '@/pages/mixins/ServerPrefetchProvidersMixin'

const SupportPage = {
  name: 'meta-search-page',
  mixins: [ServerPrefetchProvidersMixin],
  components: {
    HeaderSection,
    FooterSection,
  },
}

export default SupportPage
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
@import '../styles/text-only-page.scss';

figure {
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  border: 1px solid black;
}

h4 {
  margin: 1rem 0;
}
</style>
