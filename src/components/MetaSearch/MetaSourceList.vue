<template>
  <div class="margin-bottom-large">
    <component :is="sourceHeadingLevel" class="b-header margin-bottom-normal"
      >Sources</component
    >
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
import getLegacySourceUrl, { legacySourceMap } from '@/utils/getLegacySourceUrl'

export default {
  name: 'meta-source-list',
  props: {
    type: { type: String },
    query: { type: String },
    sourceHeadingLevel: { type: String, default: 'h4' },
  },
  methods: {
    getSourceUrl(source) {
      return getLegacySourceUrl(this.type)(source, { query: this.query.q })
    },
  },
  mounted() {
    console.log(legacySourceMap)
  },
  data() {
    return {
      sources: Object.keys(legacySourceMap).filter(
        (sourceName) => legacySourceMap[sourceName][this.type]
      ),
    }
  },
}
</script>
