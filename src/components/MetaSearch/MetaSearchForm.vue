<template>
  <section :key="type" class="padding-normal">
    <header class="margin-bottom-large">
      <i18n
        path="meta-search.form.title"
        tag="h4"
        class="b-header margin-bottom-small"
      >
        <template v-slot:type>
          {{ type }}
        </template>
      </i18n>
      <i18n path="meta-search.form.caption" tag="p">
        <template v-slot:type>
          {{ type }}
        </template>
        <template v-slot:break>
          <br />
        </template>
        <template v-slot:filter>
          {{ unsupportedByUsefilter }}
        </template>
      </i18n>
    </header>

    <MetaSourceList :type="type" :query="metaQuery" />

    <p class="caption has-text-weight-semibold has-color-dark-gray max-w-lg">
      {{ $t('meta-search.caption') }}
    </p>
  </section>
</template>

<script>
import MetaSourceList from './MetaSourceList'

export default {
  name: 'MetaSearch',
  components: {
    MetaSourceList,
  },
  props: ['type'],
  computed: {
    query() {
      return this.$store.state.query
    },
    unsupportedByUsefilter() {
      if (this.type === 'audio') {
        return 'CC Mixter, Jamendo, or Wikimedia Commons'
      }
      if (this.type === 'video') return 'Wikimedia Commons or Youtube'
      return ''
    },
    metaQuery() {
      return {
        q: this.query.q,
        filters: {
          commercial: this.query.license_type
            ? this.query.license_type.includes('commercial')
            : false,
          modify: this.query.license_type
            ? this.query.license_type.includes('modification')
            : false,
        },
      }
    },
  },
}
</script>

<style>
/* @remove when this class is added to vocabulary by https://github.com/creativecommons/vocabulary/issues/515   */
.has-color-dark-gray {
  color: rgb(120, 120, 120);
}

.max-w-lg {
  max-width: 48rem;
}
</style>
