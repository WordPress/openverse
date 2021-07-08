<template>
  <div class="margin-bottom-large">
    <ul class="buttons is-centered margin-top-big">
      <li v-for="source in sources" :key="source">
        <a
          target="_blank"
          rel="nofollow noreferrer"
          :href="getSourceUrl(source)"
          class="button small margin-right-small is-opaque"
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
