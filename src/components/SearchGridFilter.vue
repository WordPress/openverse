<template>
<div>
  <div class="is-hidden-desktop">
    <transition name="modal">
        <div class="overlay">
          <div class="is-touch modal">
          <h4 class="padding-top-big padding-left-big padding-bottom-big padding-right-normal">
           Filters
          <i class="icon cross close" @click.prevent="close()" />
           </h4>

         <div :class="{ 'search-filters': true,
                 'search-filters__visible': isFilterVisible, }">
    <slot class="is-touch">
    <form class="filters-form" role="filter">
      <filter-check-list :options="filters.licenseTypes"
                         :disabled="licenseTypesDisabled"
                         title="I want something that I can"
                         filterType="licenseTypes"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.licenses"
                         :disabled="licensesDisabled"
                         title="Licenses"
                         filterType="licenses"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list v-if="renderProvidersFilter"
                         :options="filters.providers"
                         title="Collections"
                         filterType="providers"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.categories"
                         title="Image Type"
                         filterType="categories"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.extensions"
                         title="File Type"
                         filterType="extensions"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.aspectRatios"
                         title="Aspect Ratio"
                         filterType="aspectRatios"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.sizes"
                         title="Image Size"
                         filterType="sizes"
                         @filterChanged="onUpdateFilter" />
    </form>
    </slot>
    <div class="is-flex bottom-filters">
    <div class="clear-filters padding-top-normal
         padding-left-larger padding-bottom-normal
         padding-right-normal margin-top-small">
      <button class="button tiny"
              @click="onClearFilters">
        Clear filters
      </button>
    </div>
    <div class="apply-filters padding-top-normal
         padding-left-large padding-bottom-normal
         padding-right-larger margin-top-small"
         v-if="isFilterApplied">
      <button class="button is-primary tiny"
              @click.prevent="apply()">
        Apply filters
      </button>
    </div>
    </div>
   </div>
  </div>
</div>
</transition>
</div>
 <div class="is-hidden-touch">
 <div :class="{ 'search-filters': true,
                 'search-filters__visible': isFilterVisible, }">
    <form class="filters-form" role="filter">
      <filter-check-list :options="filters.licenseTypes"
                         title="I want something that I can"
                         filterType="licenseTypes"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.licenses"
                         :disabled="licensesDisabled"
                         title="Licenses"
                         filterType="licenses"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list v-if="renderProvidersFilter"
                         :options="filters.providers"
                         title="Collections"
                         filterType="providers"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.categories"
                         title="Image Type"
                         filterType="categories"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.extensions"
                         title="File Type"
                         filterType="extensions"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.aspectRatios"
                         title="Aspect Ratio"
                         filterType="aspectRatios"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.sizes"
                         title="Image Size"
                         filterType="sizes"
                         @filterChanged="onUpdateFilter" />
    </form>
    <div class="margin-normal filter-option small-filter search-filters_search-by">
      <input type="checkbox" id="creator-chk"
              :checked="filters.searchBy.creator"
              @change="onUpdateSearchByCreator">
      <label for="creator-chk">Search by Creator</label>
    </div>
    <div class="margin-big padding-bottom-normal clear-filters"
          v-if="isFilterApplied">
      <button class="button tiny"
              @click="onClearFilters">
        Clear filters
      </button>
    </div>
  </div>
</div>
</div>
</template>

<script>
import { SET_FILTER_IS_VISIBLE, CLEAR_FILTERS } from '@/store/mutation-types';
import { TOGGLE_FILTER } from '@/store/action-types';
import FilterCheckList from './FilterChecklist';

export default {
  name: 'search-grid-filter',
  props: ['isCollectionsPage', 'provider'],
  components: {
    FilterCheckList,
  },
  data() {
    return {
      SET_FILTER_IS_VISIBLE: false,
    };
  },
  computed: {
    isFilterApplied() {
      return this.$store.state.isFilterApplied;
    },
    isFilterVisible() {
      return this.$store.state.isFilterVisible;
    },
    filters() {
      return this.$store.state.filters;
    },
    renderProvidersFilter() {
      return !this.$props.isCollectionsPage;
    },
    licensesDisabled() {
      return this.$store.state.filters.licenseTypes.some(li => li.checked);
    },
    licenseTypesDisabled() {
      return this.$store.state.filters.licenses.some(li => li.checked);
    },
  },
  methods: {
    onUpdateFilter({ code, filterType }) {
      this.$store.dispatch(TOGGLE_FILTER, {
        code,
        filterType,
        isCollectionsPage: this.$props.isCollectionsPage,
        provider: this.$props.provider,
        shouldNavigate: true,
      });
    },
    onClearFilters() {
      this.$store.commit(CLEAR_FILTERS, {
        isCollectionsPage: this.$props.isCollectionsPage,
        provider: this.$props.provider,
        shouldNavigate: true,
      });
    },
    onUpdateSearchByCreator() {
      this.$store.dispatch(TOGGLE_FILTER, {
        filterType: 'searchBy',
        isCollectionsPage: this.$props.isCollectionsPage,
        provider: this.$props.provider,
        shouldNavigate: true,
      });
    },
    close() {
      this.$store.commit(
        SET_FILTER_IS_VISIBLE,
        { isFilterVisible: !this.isFilterVisible },
      );
    },
    apply() {
      this.$store.commit(
        SET_FILTER_IS_VISIBLE,
        { isFilterVisible: !this.isFilterVisible },
      );
    },
  },
};
</script>

<style lang="scss" scoped>

.close {
  float: right;
  background: none;
}

.modal {
  width: 500px;
  max-height: 600px;
  margin: 0px auto;
  background-color: #F5F5F5;
  border-radius: 2px;
  overflow-y: scroll;
  box-shadow: 0 2px 8px 3px;
  transition: all 0.2s ease-in;
  color: #000000;
}

.fadeIn-enter {
  opacity: 0;
}

.fadeIn-leave-active {
  opacity: 0;
  transition: all 0.2s step-end;
}

.fadeIn-enter .modal,
.fadeIn-leave-active.modal {
  transform: scale(1.1);
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #00000094;
  z-index: 999;
  transition: opacity 0.2s ease;
}

h4 {
  text-transform: none;
}

.search-filters {
  display: none;
  height: auto;
  top: 0;
  position: sticky;
  label {
    color: #333333;
  }
  &__visible {
    border-top: 1px solid #e8e8e8;
    display: block;
  }
}

.bottom-filters {
  background: white;
  position:sticky;
  align-self:flex-end;
  bottom:0rem;
  padding:10px;
    }

</style>
