<template>
  
    <transition name="modal">
        <div class="overlay" @click.self="">
          <div class="modal">
         <div :class="{ 'search-filters': true,
                 'search-filters__visible': isFilterVisible, }">
    <slot>
    <form class="filters-form" role="filter">
    <button @click.prevent="close()">Close </button>
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

    <div class="filter-option small-filter search-filters_search-by">
      <input type="checkbox" id="creator-chk"
              :checked="filters.searchBy.creator"
              @change="onUpdateSearchByCreator">
      <label for="creator-chk">Search by Creator</label>
    </div>
    <div class="clear-filters"
          v-if="isFilterApplied">
      <button class="button tiny"
              @click="onClearFilters">
        Clear filters
      </button>
    </div>
        </slot>
   </div>
  </div>
</div>
 </transition>
</template>

<script>
import { SET_FILTER_IS_VISIBLE } from '@/store/mutation-types';
import { TOGGLE_FILTER } from '@/store/action-types';
import { CLEAR_FILTERS } from '@/store/mutation-types';
import FilterCheckList from './FilterChecklist';

export default {
  name: 'search-grid-filter',
  props: ['isCollectionsPage', 'provider'],
  components: {
    FilterCheckList,
  },
  data: function() {
    return {
      SET_FILTER_IS_VISIBLE: false
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
    close() {
        this.$store.commit(
        SET_FILTER_IS_VISIBLE,
        { isFilterVisible: !this.isFilterVisible },
      );  },
    onUpdateFilter({ code, filterType }) {
      this.$store.dispatch(TOGGLE_FILTER, {
        code,
        filterType,
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
    onClearFilters() {
      this.$store.commit(CLEAR_FILTERS, {
        isCollectionsPage: this.$props.isCollectionsPage,
        provider: this.$props.provider,
        shouldNavigate: true,
      });
    },
  },
};
</script>

<style lang="scss" scoped>

.modal {
  width: 500px;
  margin: 0px auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 2px;
  box-shadow: 0 2px 8px 3px;
  transition: all 0.2s ease-in;
  font-family: Helvetica, Arial, sans-serif;
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
button {
  padding: 7px;
  margin-top: 10px;
  margin-left: 370px;
  background-color: green;
  color: white;
  font-size: 1.1rem;
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



</style>
