<template>
  <ul class="buttons is-centered">
    <li v-for="(browser, key) in browsers" :key="key">
      <a
        target="_blank"
        rel="nofollow noreferrer"
        :href="browser.extUrl"
        class="browser-button button small me-2 is-opaque"
      >
        {{ $t(`browsers.${key}`) }}
        <img class="ms-2" :src="browser.logo" :alt="$t(`browsers.${key}`)" />
      </a>
    </li>
  </ul>
</template>

<script>
import chromeLogo from '~/assets/browsers/chrome.svg'
import edgeLogo from '~/assets/browsers/edge.svg'
import firefoxLogo from '~/assets/browsers/firefox.svg'
import operaLogo from '~/assets/browsers/opera.svg'

export default {
  name: 'ExtensionBrowsers',
  data() {
    return {
      browsers: {
        chrome: {
          extUrl:
            'https://chrome.google.com/webstore/detail/cc-search/agohkbfananbebiaphblgcfhcclklfnh',
          logo: chromeLogo,
        },
        firefox: {
          extUrl:
            'https://addons.mozilla.org/en-US/firefox/addon/cc-search-extension/',
          logo: firefoxLogo,
        },
        opera: {
          extUrl: 'https://addons.opera.com/en/extensions/details/cc-search/',
          logo: operaLogo,
        },
        edge: {
          extUrl:
            'https://microsoftedge.microsoft.com/addons/detail/cc-search/djolilnbndifmlfmcdnifdfjfbglipgc',
          logo: edgeLogo,
        },
      },
    }
  },
}
</script>

<style scoped lang="scss">
.browser-button {
  background-color: $color-white;

  img {
    height: 1.5em;
    width: 1.5em;
  }
}
</style>
