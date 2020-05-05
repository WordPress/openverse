<template>
  <div class="filters padding-vertical-big padding-left-big padding-right-normal">
    <div class="filters-title" @click.prevent="toggleFilterVisibility">
      <span>{{ title }}</span>
      <button class="filter-visibility-toggle is-white padding-vertical-small">
        <i v-if="filtersVisible"
           class="icon angle-up rotImg is-size-5 has-text-grey-light"
           title="toggle filters visibility" />
        <i v-else
           class="icon angle-down is-size-5 has-text-grey-light"
           title="toggle filters visibility" />
      </button>
    </div>
    <template v-if="filtersVisible && options">
    <div v-for="(item, index) in options" :key="index" class="margin-top-small">
      <label class="checkbox" :disabled="isDisabled(item)" :for="item.code">
        <input type="checkbox"
             class="filter-checkbox"
             :id="item.code"
             :key="index"
             :checked="item.checked"
             :disabled="isDisabled(item)"
             @change="onValueChange" />
        {{ item.name }}
      </label>
    </div>
    </template>
    <template v-if="filtersVisible && filterType === 'mature'">
        <label class="checkbox margin-top-small" for="mature">
          <input id="mature"
                 class="filter-checkbox"
                 type="checkbox"
                 :checked="checked"
                 @change="onValueChange">
          Enable Mature Content
        </label>
    </template>
  </div>
</template>
<script>
export default {
  name: 'filter-check-list',
  props: ['options', 'title', 'filterType', 'disabled', 'checked'],
  data() {
    return { filtersVisible: false };
  },
  // computed: {

  // },
  methods: {
    onValueChange(e) {
      this.$emit('filterChanged', { code: e.target.id, filterType: this.$props.filterType });
    },
    toggleFilterVisibility() {
      this.filtersVisible = !this.filtersVisible;
    },
    isDisabled(e) {
      if (this.$props.filterType === 'licenses') {
        const commercial = this.$store.state.filters.licenseTypes.find(
          item => item.code === 'commercial',
        );
        const modification = this.$store.state.filters.licenseTypes.find(
          item => item.code === 'modification',
        );
        return (commercial.checked && e.code.includes('nc')) ||
              (modification.checked && e.code.includes('nd'));
      }
      if (this.$props.filterType === 'licenseTypes') {
        const nc = this.$store.state.filters.licenses.filter(item => item.code.includes('nc'));
        const nd = this.$store.state.filters.licenses.filter(item => item.code.includes('nd'));
        return (e.code === 'commercial' && nc.some(li => li.checked)) ||
              (e.code === 'modification' && nd.some(li => li.checked));
      }
      return this.$props.disabled;
    },
  },
};
</script>

<style lang="scss" scoped>
.filters {
  border-bottom: 2px solid rgb(245, 245, 245);
}
.filters-title {
  font-size: 1.250em;
  font-weight: 600;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.5;
  letter-spacing: normal;
  cursor: pointer;
}
.filter-visibility-toggle {
  float: right;
  cursor: pointer;
  background: none;
  border: none;
}
label {
  color: #333333;
}
</style>
