<template>
  <div
    class="column is-narrow margin-normal has-background-white provider-card"
  >
    <div>
      <router-link
        :to="'/collections/' + provider.source_name"
        class="provider-name has-text-weight-normal has-text-black"
      >
        {{ provider.display_name }}
      </router-link>
    </div>
    <div class="provider-logo">
      <router-link :to="'/collections/' + provider.source_name">
        <img
          :alt="provider.display_name"
          :src="getProviderLogo(provider.source_name)"
        />
      </router-link>
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
import ImageProviderService from '@/api/ImageProviderService'

export default {
  name: 'collection-item',
  props: ['provider'],
  methods: {
    getProviderImageCount(imageCount) {
      return imageCount.toLocaleString('en')
    },
    getProviderLogo(providerName) {
      const provider = ImageProviderService.getProviderInfo(providerName)
      const logoUrl =
        this.provider.logo_url ||
        (provider ? require(`@/assets/${provider.logo}`) : '') // eslint-disable-line global-require, import/no-dynamic-require

      return logoUrl
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

  a {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }

  img {
    max-height: 10rem;
  }
}

// Fallback styles in the rare event logos don't display
.provider-logo img[src=''] {
  word-wrap: break-word;
  white-space: pre-line;
  text-align: center;
  font-size: 15px;
  display: block;
}
</style>
