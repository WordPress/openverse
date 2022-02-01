<template>
  <section
    :key="type"
    class="p-6 meta-search text-center mt-12"
    data-testid="meta-search-form"
  >
    <header class="mb-10">
      <i18n
        v-if="!noresult"
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
      <i18n
        v-else
        path="meta-search.form.no-results-title"
        tag="h4"
        class="b-header mb-2"
      >
        <template #type>{{ type }}</template>
        <template #query>{{ query.q }}</template>
      </i18n>
      <i18n path="meta-search.form.caption" tag="p">
        <template #type>{{ type }}</template>
        <template #break>
          <br />
        </template>
        <template #filter>{{ unsupportedByUsefilter }}</template>
      </i18n>
    </header>

    <VMetaSourceList :type="type" :query="metaQuery" />

    <p class="caption font-semibold max-w-3xl my-0 mx-auto">
      {{ $t('meta-search.caption') }}
    </p>
  </section>
</template>

<script>
import { AUDIO, IMAGE, VIDEO } from '~/constants/media'

import VMetaSourceList from './VMetaSourceList.vue'

export default {
  name: 'VMetaSearchForm',
  components: {
    VMetaSourceList,
  },
  props: {
    query: { type: Object, required: true },
    type: { type: String, required: true },
    supported: { type: Boolean, default: false },
    noresult: { type: Boolean, required: true },
  },
  computed: {
    unsupportedByUsefilter() {
      if (this.type === AUDIO) {
        return 'CC Mixter'
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
