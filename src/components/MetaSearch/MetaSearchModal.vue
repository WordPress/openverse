<template>
  <app-modal id="meta-search-modal" @close="$emit('close')">
      <header class="padding-top-bigger
        padding-left-bigger padding-righr-bigger padding-bottom-small">
        <h2>Search images from other sources</h2>
        <p>Click on a source below to directly search other collections of CC-licensed images</p>
      </header>
      <hr />
      <div class="padding-left-bigger
        padding-right-bigger padding-bottom-bigger meta-modal-content">
        <meta-source-list :type="type" :query="query" />
        <p class="caption has-text-weight-semibold">
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
  </app-modal>
</template>

<script>
import AppModal from '@/components/AppModal';
import MetaSourceList from './MetaSourceList';

export default {
  name: 'meta-search-modal',
  props: ['type', 'query'],
  components: {
    AppModal,
    MetaSourceList,
  },
};
</script>

<style>
.meta-modal-content {
  max-width: 46rem;
}
</style>
