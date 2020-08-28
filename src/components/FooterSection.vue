<template>
  <footer class="main-footer">
    <div class="container">
      <div class="columns">
        <section
          role="complementary"
          :aria-label="$t('footer.aria.contact')"
          class="column"
        >
          <a
            :aria-label="$t('footer.aria.homepage')"
            href="https://creativecommons.org"
            class="main-logo margin-bottom-bigger has-text-white"
          >
            <IconCCLogo focusable="false" aria-hidden="true" />
          </a>
          <address class="margin-bottom-normal">
            <span class="is-block">{{ $t('footer.address.title') }}</span>
            <span>{{ $t('footer.address.address') }}</span>
          </address>
          <a href="mailto:info@creativecommons.org" class="mail is-block">
            info@creativecommons.org
          </a>
          <a href="tel://+1-415-429-6753" class="phone">+1-415-429-6753</a>

          <div class="margin-vertical-large">
            <a
              href="https://www.instagram.com/creativecommons"
              aria-label="instagram"
              class="social has-text-white"
              target="_blank"
              rel="noopener"
            >
              <i class="icon instagram margin-right-small is-size-4" />
            </a>
            <a
              href="https://www.twitter.com/creativecommons"
              aria-label="twitter"
              class="social has-text-white"
              target="_blank"
              rel="noopener"
            >
              <i class="icon twitter margin-right-small is-size-4" />
            </a>
            <a
              href="https://www.facebook.com/creativecommons"
              aria-label="facebook"
              class="social has-text-white"
              target="_blank"
              rel="noopener"
            >
              <i class="icon facebook margin-right-small is-size-4" />
            </a>
          </div>
        </section>
        <div class="column is-half">
          <nav class="footer-navigation">
            <ul class="menu">
              <li>
                <a
                  class="menu-item"
                  href="https://creativecommons.org/about/contact/"
                  >{{ $t('footer.navigation.contact') }}</a
                >
              </li>
              <li>
                <a
                  class="menu-item"
                  href="https://creativecommons.org/privacy/"
                  >{{ $t('footer.navigation.privacy') }}</a
                >
              </li>
              <li>
                <a
                  class="menu-item"
                  href="https://creativecommons.org/policies/"
                  >{{ $t('footer.navigation.policies') }}</a
                >
              </li>
              <li>
                <a
                  class="menu-item"
                  href="https://creativecommons.org/terms/"
                  >{{ $t('footer.navigation.terms') }}</a
                >
              </li>
            </ul>
          </nav>
          <div class="attribution margin-top-bigger">
            <i18n path="footer.caption.label" tag="p" class="caption">
              <template v-slot:noted>
                <a
                  href="https://creativecommons.org/policies#license"
                  target="_blank"
                  rel="noopener"
                  >{{ $t('footer.caption.noted') }}</a
                >
              </template>
              <template v-slot:attribution>
                <a
                  href="https://creativecommons.org/licenses/by/4.0/"
                  target="_blank"
                  rel="noopener"
                >
                  {{ $t('footer.caption.attribution') }}
                </a>
              </template>
              <template v-slot:icons>
                <a
                  href="https://fontawesome.com/"
                  target="_blank"
                  rel="noopener"
                  class="has-text-white"
                >
                  {{ $t('footer.caption.icons') }}
                </a>
              </template>
            </i18n>
            <div class="margin-top-smaller">
              <i
                class="icon cc-logo margin-right-small is-size-4 is-color-white"
              />
              <i
                class="icon cc-by margin-right-small is-size-4 is-color-white"
              />
            </div>
          </div>
        </div>
        <div class="column">
          <section
            role="complementary"
            :aria-label="$t('footer.aria.donate')"
            class="donate-section"
          >
            <span class="title is-5 has-text-white">{{
              $t('footer.donate.work')
            }}</span>
            <p>{{ $t('footer.donate.help') }}</p>
            <a
              class="button small donate"
              href="http://creativecommons.org/donate"
            >
              <i
                class="icon cc-letterheart-filled margin-right-small is-size-5 padding-top-smaller"
              />
              {{ $t('footer.donate.link') }}
            </a>
          </section>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
import IconCCLogo from '@creativecommons/vocabulary/assets/logos/cc/logomark.svg?inline'

export default {
  name: 'FooterSection',
  components: {
    IconCCLogo,
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
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
