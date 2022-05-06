<template>
  <ul class="flex flex-wrap justify-center items-center">
    <li v-for="(browser, key) in browsers" :key="key">
      <VButton
        as="VLink"
        variant="tertiary"
        :href="browser.extUrl"
        class="me-2"
      >
        {{ $t(`browsers.${key}`) }}
        <img
          class="ms-2 w-6 h-6"
          :src="browser.logo"
          :alt="$t(`browsers.${key}`).toString()"
        />
      </VButton>
    </li>
  </ul>
</template>

<script lang="ts">
import { defineComponent } from '@nuxtjs/composition-api'

import VButton from '~/components/VButton.vue'

import chromeLogo from '~/assets/browsers/chrome.svg'
import edgeLogo from '~/assets/browsers/edge.svg'
import firefoxLogo from '~/assets/browsers/firefox.svg'
import operaLogo from '~/assets/browsers/opera.svg'

export default defineComponent({
  name: 'ExtensionBrowsers',
  components: { VButton },
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
})
</script>
