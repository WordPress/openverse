<template>
  <div class="meta-card">
    <!-- <i18n
      path="meta-search.card.caption"
      tag="p"
      class="padding-left-bigger padding-right-bigger"
    >
      <template v-slot:break>
        <br />
      </template>
    </i18n> -->
    <hr class="margin-bottom-bigger" />
    <div
      class="padding-left-bigger padding-right-bigger padding-bottom-bigger meta-modal-content"
    >
      <h5 class="b-header margin-bottom-small">
        {{ $t('meta-search.card.search') }}
      </h5>

      <div class="control has-icons-left margin-bottom-bigger">
        <label for="searchTerm">
          <input
            id="searchTerm"
            class="input"
            type="text"
            placeholder="Search"
            v-model="editableQuery.q"
            style="max-width: 400px;"
          />
        </label>
        <span class="icon is-left">
          <!-- Style issue needs to be fixed for icons: -->
          <i class="icon search is-size-5" style="padding: 10px;" />
        </span>
      </div>

      <template v-if="type !== 'image'">
        <h5 for="metaUseCheckboxes" class="b-header margin-bottom-small">
          {{ $t('meta-search.card.checkboxes.title') }}
        </h5>
        <div class="meta-filters margin-bottom-bigger flex">
          <label for="commercial-chk" class="margin-right-big"
            ><input
              id="commercial-chk"
              class="margin-right-smaller"
              type="checkbox"
              v-model="editableQuery.filters.commercial"
            />
            {{ $t('meta-search.card.checkboxes.commercial') }}</label
          >
          <label for="modify-chk"
            ><input
              id="modify-chk"
              class="margin-right-smaller"
              type="checkbox"
              v-model="editableQuery.filters.modify"
            />
            {{ $t('meta-search.card.checkboxes.modify') }}</label
          >
        </div>
      </template>

      <meta-source-list :type="type" :query="editableQuery" />
      <p class="caption has-text-weight-semibold">
        {{ $t('meta-search.caption') }}
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
