<template>
  <footer class="main-footer">
    <div class="container">
      <div class="columns">
        <section
          role="complementary"
          :aria-label="$t('footer.aria.contact')"
          class="column"
        >
          <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
          <NuxtLink class="logo" to="/">Openverse</NuxtLink>
          <!-- eslint-enable @intlify/vue-i18n/no-raw-text -->
          <LocaleSelector />
        </section>
        <div class="column is-half">
          <div class="attribution mt-8">
            <i18n path="footer.caption.label" tag="p" class="caption">
              <template #noted>
                <a
                  href="https://creativecommons.org/policies#license"
                  target="_blank"
                  rel="noopener"
                  >{{ $t('footer.caption.noted') }}</a
                >
              </template>
              <template #attribution>
                <a
                  href="https://creativecommons.org/licenses/by/4.0/"
                  target="_blank"
                  rel="noopener"
                >
                  {{ $t('footer.caption.attribution') }}
                </a>
              </template>
              <template #icons>
                <a
                  href="https://fontawesome.com/"
                  target="_blank"
                  rel="noopener"
                  class="text-white"
                >
                  {{ $t('footer.caption.icons') }}
                </a>
              </template>
            </i18n>
            <div class="mt-1">
              <i class="icon cc-logo mr-2 text-lgr" />
              <i class="icon cc-by mr-2 text-lgr" />
            </div>
          </div>
        </div>
        <div class="column">
          <section
            role="complementary"
            :aria-label="$t('footer.aria.donate')"
            class="donate-section"
          >
            <span class="title is-5 text-white">{{
              $t('footer.donate.work')
            }}</span>
            <p>{{ $t('footer.donate.help') }}</p>
          </section>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
import GoogleAnalytics from '@/analytics/GoogleAnalytics'
import { DonateLinkClick } from '@/analytics/events'

export default {
  name: 'FooterSection',
  methods: {
    sendClickEvent() {
      GoogleAnalytics().sendEvent(DonateLinkClick('footer'))
    },
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.logo {
  color: white;
  font-size: 2rem;
  font-weight: bold;
  &:link,
  &:visited,
  &:hover,
  &:active {
    text-decoration: none;
  }
}
.donate,
.social {
  &:hover {
    text-decoration: none;
  }
}
.icon {
  vertical-align: middle;
}
</style>
