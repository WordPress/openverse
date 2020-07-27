<template>
  <div
    class="column is-narrow margin-normal has-background-white provider-card"
  >
    <div>
      <span
        class="link provider-name has-text-weight-normal has-text-black"
        @click="setQuery(provider.source_name)"
      >
        {{ provider.display_name }}
      </span>
    </div>
    <div class="provider-logo">
      <span class="link" @click="setQuery(provider.source_name)">
        <img
          :alt="provider.display_name"
          :src="getProviderLogo(provider.source_name)"
        />
      </span>
    </div>
    <div>
      <i18n
        path="collections.collection-size"
        tag="span"
        class="has-text-grey-light has-text-weight-semibold"
      >
        <template v-slot:count>
          {{ getProviderImageCount(provider.image_count) }}
        </template>
      </i18n>
    </div>
  </div>
</template>

<script>
import { SET_QUERY } from '@/store/mutation-types'
import ImageProviderService from '@/api/ImageProviderService'

export default {
  name: 'collection-item',
  props: ['provider'],
  methods: {
    setQuery(providerName) {
      this.$store.commit(SET_QUERY, {
        query: { q: '', source: providerName },
        shouldNavigate: true,
      })
    },
    getProviderImageCount(imageCount) {
      return imageCount.toLocaleString('en')
    },
    getProviderLogo(providerName) {
      const provider = ImageProviderService.getProviderInfo(providerName)
      if (provider) {
        const logo = provider.logo
        const logoUrl = this.provider.logo_url || require(`@/assets/${logo}`) // eslint-disable-line global-require, import/no-dynamic-require

        return logoUrl
      }

      return ''
    },
  },
}
</script>

<style lang="scss" scoped>
.provider-card {
  width: 16.5rem;
  border: 2px solid rgb(216, 216, 216);
  &:hover {
    box-shadow: 10px 10px 2px -5px #e7e7e7;
  }
}

.provider-name {
  font-weight: 800;
}

.provider-logo {
  height: 12rem;
  white-space: nowrap;
  position: relative;

  .link {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }

  img {
    max-height: 10rem;
  }
}
</style>
