<template>
  <div role="main" class="section margin-bottom-large">
    <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
    <div class="container is-fluid">
      <div class="margin-bottom-large">
        <h1 class="title is-2 margin-bottom-normal">
          {{ $t('support.title') }}
        </h1>
        <div class="margin-bottom-normal">
          <article
            class="card entry-post entry-image horizontal column is-half is-offset-one-quarter"
          >
            <header class="card-image">
              <figure class="image">
                <img src="~/assets/support.png" alt="Header image" />
              </figure>
            </header>
            <div class="card-content with-button">
              <div class="content">
                <h2>WP Photos</h2>
                <span class="subtitle is-italic margin-bottom-normal">
                  {{ $t('support.open') }}</span
                >
                <p>
                  {{ $t('support.cc') }}
                </p>
              </div>
              <a
                class="button normal donate margin-right-normal"
                :href="donationLink"
                @click="sendDonationEvent"
                @keypress.enter="sendDonationEvent"
              >
                <i
                  class="icon cc-letterheart-filled margin-right-small padding-top-smaller"
                />
                {{ $t('support.button.donate') }}</a
              >
            </div>
          </article>
          <i18n
            path="support.quote"
            tag="p"
            class="has-text-centered is-uppercase"
          >
            <template #joy>
              <a
                aria-label="licenses"
                href="https://www.flickr.com/photos/33363480@N05/14084531185"
                >"Joy is the simplest form of gratitude... Karl Barth"</a
              >
            </template>
            <template #writer>
              <a
                aria-label="public domain"
                href="https://www.flickr.com/photos/33363480@N05"
                >Nick Kenrick.</a
              >
            </template>
            <template #cc>
              <a
                aria-label="photograph"
                href="https://creativecommons.org/licenses/by/2.0/?ref=ccsearch&atype=rich"
                >CC BY 2.0
              </a>
            </template>
          </i18n>
        </div>
        <p class="margin-bottom-normal">{{ $t('support.inclusive') }}</p>
        <i18n path="support.work" tag="p" class="margin-bottom-normal">
          <template #license>
            <a
              aria-label="licenses"
              href="https://creativecommons.org/licenses/"
              >CC License Suite</a
            >
          </template>
          <template #public-domain>
            <a
              aria-label="public domain"
              href="https://creativecommons.org/publicdomain/"
              >public domain tools</a
            >
          </template>
          <template #photograph>
            <a
              aria-label="photograph"
              href="https://www.parismuseescollections.paris.fr/fr/musee-carnavalet/oeuvres/portrait-de-l-ecrivaine-libertaire-et-feministe-caroline-remy-dite-severine"
              >this photograph</a
            >
          </template>
          <template #guide>
            <a
              aria-label="guide"
              href="https://pressbooks.library.ryerson.ca/docs/"
              >this guide</a
            >
          </template>
        </i18n>
        <h2 class="title subtitle is-3 margin-bottom-normal">
          {{ $t('support.free') }}
        </h2>
        <p class="margin-bottom-normal">{{ $t('support.access') }}</p>
        <i18n path="support.public-good" tag="p" class="margin-bottom-normal">
          <template #public-good>
            <strong>public good</strong>
          </template>
        </i18n>
        <div class="field is-grouped is-grouped-centered">
          <a
            class="button normal donate margin-right-normal"
            :href="donationLink"
            @click="sendDonationEvent"
            @keypress.enter="sendDonationEvent"
          >
            <i
              class="icon cc-letterheart-filled margin-right-small padding-top-smaller"
            />
            {{ $t('support.button.donate') }}</a
          >
          <h2 class="title subtitle is-3">or</h2>
          <a
            class="button is-primary normal margin-left-normal"
            href=" https://github.com/sponsors/creativecommons"
            >{{ $t('support.button.sponsor') }}</a
          >
        </div>
        <h2 class="title subtitle is-3 margin-vertical-normal">
          {{ $t('support.launch.title') }}
        </h2>
        <p class="margin-bottom-normal">{{ $t('support.launch.first') }}</p>
        <div class="content">
          <ul>
            <li>
              {{ $t('support.launch.served') }}
            </li>
            <li>
              {{ $t('support.launch.host') }}
            </li>
            <li>
              {{ $t('support.launch.users') }}
            </li>
            <li>
              {{ $t('support.launch.visitors') }}
            </li>
          </ul>
        </div>
        <strong
          ><p class="margin-bottom-normal">
            {{ $t('support.launch.education') }}
          </p></strong
        >
        <h2 class="title subtitle is-3 margin-bottom-normal">
          {{ $t('support.future.title') }}
        </h2>
        <p class="margin-bottom-normal">{{ $t('support.future.more') }}</p>
        <div class="content">
          <ul>
            <li>
              {{ $t('support.future.culture') }}
            </li>
            <li>
              {{ $t('support.future.audio') }}
            </li>
            <li>
              {{ $t('support.future.video') }}
            </li>
            <li>
              {{ $t('support.future.text') }}
            </li>
            <li>
              {{ $t('support.future.internalize') }}
            </li>
            <li>
              {{ $t('support.future.translate') }}
            </li>
            <li>
              {{ $t('support.future.accessibility') }}
            </li>
            <li>
              {{ $t('support.future.smarter') }}
            </li>
          </ul>
        </div>
        <h2 class="title subtitle is-3 margin-bottom-normal has-text-centered">
          {{ $t('support.future.support') }}
        </h2>
        <div class="field is-grouped is-grouped-centered margin-bottom-medium">
          <a class="button normal donate" :href="donationLink">
            <i
              class="icon cc-letterheart-filled margin-right-small padding-top-smaller"
            />
            {{ $t('support.button.donate') }}</a
          >
        </div>
        <p class="margin-bottom-normal">{{ $t('support.grateful') }}</p>
      </div>
    </div>
    <!-- eslint-enable -->
  </div>
</template>

<script>
import { DonateLinkClick } from '@/analytics/events'
import GoogleAnalytics from '~/analytics/GoogleAnalytics'

export default {
  name: 'MetaSearchPage',
  data() {
    return {
      donationLink: 'https://www.classy.org/give/297881/#!/donation/checkout',
    }
  },
  methods: {
    sendDonationEvent() {
      GoogleAnalytics().sendEvent(DonateLinkClick('support-page'))
    },
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
@import '~/styles/text-only-page.scss';

h4 {
  margin: 1rem 0;
}
</style>
