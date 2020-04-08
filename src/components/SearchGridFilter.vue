/* eslint-disable no-useless-escape */
<template>
<div>
  <div v-if="isMobile()">
    <transition name="modal" v-if="isMobile()">
        <div class="overlay">
          <div class="modal" ref="progressbar">
          <div class="is-flex">
          <div class="text"> Filter </div>
          <button class="button tiny" @click.prevent="close()">Close</button>
          </div>
         <div :class="{ 'search-filters': true,
                 'search-filters__visible': isFilterVisible, }">
    <slot>
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
    <div class="is-flex filter-down">
    <div class="clear-filters">
      <button class="button tiny"
              @click="onClearFilters">
        Clear filters
      </button>
    </div>
    <div class="apply-filters">
      <button class="button tiny">
        Apply filters
      </button>
    </div>
    </div>
   </div>
  </div>
</div>
</transition>
</div>
<div v-if="!isMobile()">
 <div :class="{ 'search-filters': true,
                 'search-filters__visible': isFilterVisible, }">
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
      percentage: 0,
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
      );
    },
    isMobile() {
      let check = false;
      // eslint-disable-next-line
      (function (a) { if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0, 4))) check = true; }(navigator.userAgent || navigator.vendor || window.opera));
      return check;
    },
  },
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
  checkScrollBar() {
    const element = this.$refs.progressbar;
    const clientHeight = element.clientHeight;
    const scrollHeight = element.scrollHeight;
    const scrollTop = element.scrollTop;
    const res = (scrollTop / (scrollHeight - clientHeight)) * 100;
    if (scrollHeight <= clientHeight) {
      this.percentage = 100;
    }
    else {
      this.percentage = res.toFixed(2);
    }
  },
  mounted() {
    this.$refs.progressbar.addEventListener('scroll', this.checkScrollBar);
  },
  beforeDestroy() {
    this.$refs.progressbar.removeEventListener('scroll', this.checkScrollBar);
  },
};
</script>

<style lang="scss" scoped>
.icon, .text {
  display:inline;
  font-size: 25px;
  margin-left: 10px;
}
.modal {
  width: 500px;
  max-height: 600px;
  margin: 0px auto;
  background-color: #fff;
  border-radius: 2px;
  overflow-y: scroll;
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
  margin-left: 62px;
  background-color: grey;
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
.search-filters_search-by,
.clear-filters {
  margin-top: 0.4em;
  margin-left: 24px;
}
.search-filters_search-by,
.apply-filters {
  margin-top: 0.4em;
}
.is-flex {
  padding:15px;
}
.filter-down {
  background: white;
  position:sticky;
  align-self:flex-end;
  bottom:.1rem;
  padding:10px;
    }
</style>
