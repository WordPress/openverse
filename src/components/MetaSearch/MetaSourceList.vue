<template>
  <div class="mb-10">
    <ul class="buttons is-centered mt-6">
      <li v-for="source in sources" :key="source">
        <a
          target="_blank"
          rel="nofollow noreferrer"
          :href="getSourceUrl(source)"
          class="button small mr-2 is-opaque"
        >
          {{ source }}
          <sup class="">
            <i class="ml-2 icon external-link" />
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
