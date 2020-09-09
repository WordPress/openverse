<template>
  <div class="margin-bottom-large">
    <h5 class="b-header margin-bottom-small">
      {{ $t('meta-search.sources') }}
    </h5>
    <ul class="buttons">
      <li v-for="source in sources" :key="source">
        <a
          target="_blank"
          rel="nofollow noreferrer"
          :href="getSourceUrl(source)"
          class="button small margin-right-small"
        >
          {{ source }}
          <sup class="">
            <i class="margin-left-small icon external-link" />
          </sup>
        </a>
      </li>
    </ul>
  </div>
</template>

<script>
import getLegacySourceUrl, { legacySourceMap } from '~/utils/getLegacySourceUrl'

export default {
  name: 'MetaSourceList',
  props: {
    type: { type: String },
    query: { type: Object },
  },
  data() {
    return {
      sources: Object.keys(legacySourceMap).filter(
        (sourceName) => legacySourceMap[sourceName][this.type]
      ),
    }
  },
  methods: {
    getSourceUrl(source) {
      return getLegacySourceUrl(this.type)(source, this.query)
    },
  },
}
</script>
