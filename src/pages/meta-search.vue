<template>
  <div class="section mb-10" dir="ltr">
    <div class="container">
      <div class="mb-10">
        <h1 class="text-5xl">
          {{ $t('meta-search-page.title') }}
        </h1>
      </div>

      <i18n path="meta-search-page.intro" tag="p" class="mb-4">
        <template #link>
          <a aria-label="sources" href="/sources">{{
            $t('meta-search-page.link')
          }}</a>
        </template>
      </i18n>
      <p>{{ $t('meta-search-page.license') }}</p>
      <h2 class="mt-10 mb-4 text-2xl">
        {{ $t('meta-search-page.content') }}
      </h2>
      <p>{{ $t('meta-search-page.content-types') }}</p>

      <h2 class="mt-10 mb-4 text-2xl">
        {{ $t('meta-search-page.images.title') }}
      </h2>
      <p>{{ $t('meta-search-page.images.content') }}</p>
      <div class="content">
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
      <i18n path="meta-search-page.images.info" tag="p" class="mb-2">
        <template #use>
          <strong>{{ $t('meta-search-page.use') }}</strong>
        </template>
        <template #not-finding>
          <strong>{{
            $t('meta-search.form.supported-title', { type: ' ' })
          }}</strong>
        </template>
      </i18n>
      <figure class="image my-10">
        <img
          :alt="$t('meta-search-page.images.demo-label', { type: ' ' })"
          src="~/assets/screenshots/supported.png"
          aria-hidden="true"
        />
      </figure>

      <h2 class="mt-10 mb-4 text-2xl">
        {{ $t('meta-search-page.audio-video.title') }}
      </h2>
      <p>{{ $t('meta-search-page.audio-video.content') }}</p>
      <i18n path="meta-search-page.audio-video.filter" tag="p" class="my-2">
        <template #use>
          <strong>{{ $t('meta-search-page.use') }}</strong>
        </template>
      </i18n>
      <figure class="image my-10">
        <img
          :alt="$t('meta-search-page.audio-video.demo-label', { type: ' ' })"
          src="~/assets/screenshots/unsupported.png"
          aria-hidden="true"
        />
      </figure>
      <h2 class="mt-10 mb-4 text-2xl">
        {{ $t('meta-search-page.new.title') }}
      </h2>
      <i18n path="meta-search-page.new.content" tag="p" class="mb-2">
        <template #issue>
          <a
            aria-label="issue"
            href="https://github.com/creativecommons/cccatalog/issues/new?assignees=&labels=awaiting+triage%2C+ticket+work+required%2C+providers&template=new-source-suggestion.md&title=%5BSource+Suggestion%5D+Insert+source+name+here"
            >{{ $t('meta-search-page.new.issue') }}</a
          >
        </template>
        <template #email>
          <a aria-label="email" href="mailto:openverse@wordpress.org">{{
            $t('meta-search-page.new.email')
          }}</a>
        </template>
      </i18n>
      <h2 class="mt-10 mb-4 text-2xl">
        {{ $t('meta-search-page.why.title') }}
      </h2>
      <p>{{ $t('meta-search-page.why.content') }}</p>
      <p class="my-2">
        {{ $t('meta-search-page.why.new') }}
      </p>
      <i18n path="meta-search-page.why.feedback-suggestions" tag="p">
        <template #feedback>
          <NuxtLink
            :aria-label="$t('meta-search-page.why.aria-label')"
            :to="localePath('/feedback')"
            >{{ $t('meta-search-page.why.feedback-link') }}</NuxtLink
          >
        </template>
      </i18n>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MetaSearchPage',
  layout: 'with-nav-search',
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
