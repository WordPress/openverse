<template>
  <section :key="type" class="padding-normal">
    <header class="margin-bottom-large">
      <h3 class="b-header margin-bottom-small">
        CC Search does not yet support built-in {{ type }} search.
      </h3>
      <p>
        Click on a source below to directly search other collections of
        CC-licensed {{ type }}.
      </p>
    </header>

    <meta-source-list :type="type" :query="query" />

    <p class="caption has-text-weight-semibold has-color-dark-gray max-w-lg">
      CC Search does not currently index the sources listed above, but through
      this interface is offering convenient access to search services provided
      by other independent organizations. CC has no control over the results
      that are returned. Do not assume that the results displayed in this search
      portal are under a CC license. Always verify that the work is actually
      under a CC license by following the link. If you are in doubt, you should
      contact the copyright holder directly, or try to contact the site where
      you found the content.
    </p>
  </section>
</template>

<script>
import MetaSourceList from './MetaSourceList'

export default {
  name: 'meta-search',
  props: ['type', 'query'],
  components: {
    MetaSourceList,
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
