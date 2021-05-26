<template>
  <div class="section margin-bottom-large">
    <div :class="['container', isEmbedded ? '' : 'is-fluid']">
      <div class="margin-bottom-large">
        <h1 class="title is-2">
          {{ $t('meta-search-page.title') }}
        </h1>
      </div>

      <i18n path="meta-search-page.intro" tag="p" class="margin-bottom-normal">
        <template #link>
          <a aria-label="sources" href="/sources">{{
            $t('meta-search-page.link')
          }}</a>
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
        <template #use>
          <strong>{{ $t('meta-search-page.use') }}</strong>
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
        <template #use>
          <strong>{{ $t('meta-search-page.use') }}</strong>
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
        <template #issue>
          <a
            aria-label="issue"
            href="https://github.com/creativecommons/cccatalog/issues/new?assignees=&labels=awaiting+triage%2C+ticket+work+required%2C+providers&template=new-source-suggestion.md&title=%5BSource+Suggestion%5D+Insert+source+name+here"
            >{{ $t('meta-search-page.new.issue') }}</a
          >
        </template>
        <template #email>
          <a
            aria-label="email"
            href="mailto:support-search@creativecommons.org"
            >{{ $t('meta-search-page.new.email') }}</a
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
        <template #feedback>
          <a
            aria-label="sources"
            href="https://search.creativecommons.org/feedback"
            >{{ $t('meta-search-page.why.feedback-link') }}</a
          >
        </template>
      </i18n>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import iframeHeight from '~/mixins/iframeHeight'

export default {
  name: 'MetaSearchPage',
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
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
@import '~/styles/text-only-page.scss';

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
