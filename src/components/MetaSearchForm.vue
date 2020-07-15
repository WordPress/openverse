<template>
  <div :key="type">
    <p>
      CC Search does not yet support built-in {{type}} search.
    </p>
    <p>
      Click on a source below to directly search other collections of CC-licensed {{type}}.
    </p>

    <p>Sources</p>
    <ul>
      <li v-for="source in sources" :key="source">
        <a target="_blank" rel="nofollow noreferrer" :href="getSourceUrl(source)">{{source}}</a>
      </li>
    </ul>
    <p>
      CC Search does not currently index the sources listed above, but through
      this interface is offering convenient access to search services provided
      by other independent organizations. CC has no control over the results
      that are returned. Do not assume that the results displayed in this search
      portal are under a CC license. Always verify that the work is actually
      under a CC license by following the link. If you are in doubt, you should
      contact the copyright holder directly, or try to contact the site where
      you found the content.
    </p>
  </div>
</template>

<script>
import getLegacySourceUrl, { legacySourceMap } from '@/utils/getLegacySourceUrl';

export default {
  name: 'meta-search',
  props: ['type', 'query'],
  methods: {
    getSourceUrl(source) {
      return getLegacySourceUrl(this.type)(source, { query: this.query.q });
    },
  },
  data() {
    return {
      sources: Object
        .keys(legacySourceMap)
        .filter(sourceName => legacySourceMap[sourceName][this.type]),
    };
  },
};
</script>
