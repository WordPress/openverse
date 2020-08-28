<template>
  <a
    :href="`/search?source=${provider.source_name}`"
    class="column is-narrow margin-normal has-background-white provider-card"
  >
    <div>
      <span class="link provider-name has-text-weight-normal has-text-black">
        {{ provider.display_name }}
      </span>
    </div>
    <div class="provider-logo">
      <span class="link">
        <img
          :alt="provider.display_name"
          :src="getProviderLogo(provider.source_name)"
        />
      </span>
    </div>
    <div>
      <I18n
        path="collections.collection-size"
        tag="span"
        class="has-text-grey-light has-text-weight-semibold"
      >
        <template v-slot:count>
          {{ getProviderImageCount(provider.image_count) }}
        </template>
      </I18n>
    </div>
  </a>
</template>

<script>
import { TOGGLE_FILTER } from '~/store-modules/action-types'
import { CLEAR_FILTERS } from '~/store-modules/mutation-types'
import ImageProviderService from '~/data/ImageProviderService'

export default {
  name: 'CollectionItem',
  props: ['provider'],
  methods: {
    setFilterAndQuery(providerName) {
      this.$store.commit(CLEAR_FILTERS, { provider: null })
      this.$store.dispatch(TOGGLE_FILTER, {
        filterType: 'providers',
        code: providerName,
      })
    },
    getProviderImageCount(imageCount) {
      return imageCount.toLocaleString('en')
    },
    getProviderLogo(providerName) {
      const provider = ImageProviderService.getProviderInfo(providerName)
      const logoUrl =
        this.provider.logo_url ||
        (provider ? require(`@/assets/${provider.logo}`) : '')

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
    cursor: pointer;
    text-decoration: none;
    box-shadow: 10px 10px 2px -5px #e7e7e7;
  }
}

.provider-card:hover * {
  text-decoration: none !important;
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

// Fallback styles in the rare event logos don't display
.provider-logo img[src=''] {
  word-wrap: break-word;
  white-space: pre-line;
  text-align: center;
  font-size: 15px;
  display: block;
}
</style>
