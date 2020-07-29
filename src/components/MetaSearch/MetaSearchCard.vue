<template>
  <div class="meta-card">
    <p class="padding-left-bigger padding-right-bigger">
      Click on a source below to directly search other collections of
      CC-licensed images.<br />Please note that Use filters are not supported
      for Open Clip Art Library.
    </p>
    <hr class="margin-bottom-bigger" />
    <div
      class="padding-left-bigger padding-right-bigger padding-bottom-bigger meta-modal-content"
    >
      <h5 class="b-header margin-bottom-small">Search</h5>

      <div class="control has-icons-left margin-bottom-bigger">
        <input
          class="input"
          type="text"
          placeholder="Search"
          v-model="editableQuery.q"
          style="max-width: 400px;"
        />
        <span class="icon is-left">
          <!-- Style issue needs to be fixed for icons: -->
          <i class="icon search is-size-5" style="padding: 10px;" />
        </span>
      </div>

      <h5 for="metaUseCheckboxes" class="b-header margin-bottom-small">Use</h5>
      <div class="meta-filters margin-bottom-bigger flex">
        <label class="margin-right-big"
          ><input
            class="margin-right-smaller"
            type="checkbox"
            v-model="editableQuery.filters.commercial"
          />
          Use for commercial purposes</label
        >
        <label
          ><input
            class="margin-right-smaller"
            type="checkbox"
            v-model="editableQuery.filters.modify"
          />
          Modify or adapt</label
        >
      </div>

      <meta-source-list :type="type" :query="editableQuery" />
      <p class="caption has-text-weight-semibold">
        CC Search does not currently index the sources listed above, but through
        this interface is offering convenient access to search services provided
        by other independent organizations. CC has no control over the results
        that are returned. Do not assume that the results displayed in this
        search portal are under a CC license. Always verify that the work is
        actually under a CC license by following the link. If you are in doubt,
        you should contact the copyright holder directly, or try to contact the
        site where you found the content.
      </p>
    </div>
  </div>
</template>

<script>
import MetaSourceList from './MetaSourceList'

export default {
  name: 'meta-search-card',
  props: ['type', 'query'],
  data() {
    return {
      editableQuery: {
        q: this.query.q,
        filters: {
          commercial: this.$store.state.filters.licenseTypes[0].checked,
          modify: this.$store.state.filters.licenseTypes[1].checked,
        },
      },
    }
  },
  components: {
    MetaSourceList,
  },
}
</script>

<style lang="scss" scoped>
@import 'node_modules/bulma/sass/utilities/_all';

.meta-modal-content {
  max-width: 46rem;
}

@include touch {
  .meta-filters label {
    display: block;
    width: 100%;
  }
}

.meta-card {
  max-width: 100%;
  overflow-x: hidden;
}

.close-button {
  appearance: none;
  border: none;
  background-color: transparent;
  padding: 20px;
  line-height: 1;
  height: auto;
  position: absolute;
  top: 0;
  right: 0;
  cursor: pointer;
  .icon {
    height: auto;
  }
  &:hover {
    color: rgb(120, 120, 120);
  }
}
</style>
