<template>
  <section :key="type" class="p-6 meta-search">
    <header class="mb-10">
      <i18n
        :path="
          supported
            ? 'meta-search.form.supported-title'
            : 'meta-search.form.unsupported-title'
        "
        tag="h4"
        class="b-header mb-2"
      >
        <template #type>
          {{ type }}
        </template>
      </i18n>
      <i18n path="meta-search.form.caption" tag="p">
        <template #type>{{ type }}</template>
        <template #break>
          <br />
        </template>
        <template #filter>{{ unsupportedByUsefilter }}</template>
      </i18n>
    </header>

    <MetaSourceList :type="type" :query="metaQuery" />

    <p class="caption font-semibold max-w-lg">
      {{ $t('meta-search.caption') }}
    </p>
  </section>
</template>

<script>
import MetaSourceList from './MetaSourceList'
import { AUDIO, IMAGE, VIDEO } from '~/constants/media'

export default {
  name: 'MetaSearch',
  components: {
    MetaSourceList,
  },
  props: {
    type: { type: String, required: true },
    supported: { type: Boolean, default: false },
  },
  computed: {
    query() {
      return this.$store.state.query
    },
    unsupportedByUsefilter() {
      if (this.type === AUDIO) {
        return 'CC Mixter, Jamendo, or Wikimedia Commons'
      }
      if (this.type === VIDEO) return 'Wikimedia Commons or Youtube'
      if (this.type === IMAGE) return 'Google Images'
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
.meta-search {
  margin-top: 3rem;
  text-align: center;
}

.max-w-lg {
  max-width: 48rem;
  margin: 0 auto;
}
</style>
