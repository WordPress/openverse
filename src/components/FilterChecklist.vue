<template>
  <div class="filters padding-vertical-big padding-left-big padding-right-normal">
    <div class="filters-title" @click.prevent="toggleFilterVisibility">
      <span>{{ title }}</span>
      <button class="filter-visibility-toggle is-white">
        <img src="@/assets/arrow.svg"
          v-bind:class="{rotImg:filtersVisible}"
          alt="toggle filters visibility"/>
      </button>
    </div>
    <template v-if="filtersVisible">
    <div v-for="(item, index) in options" :key="index" class="margin-top-small">
      <label class="checkbox" :for="item.code">
        <input type="checkbox"
             class="filter-checkbox"
             :id="item.code"
             :key="index"
             :checked="item.checked"
             :disabled="disabled"
             @change="onValueChange" />
        {{ item.name }}
      </label>
    </div>
    </template>
  </div>
</template>
<script>
export default {
  name: 'filter-check-list',
  props: ['options', 'title', 'filterType', 'disabled'],
  data() {
    return { filtersVisible: false };
  },
  methods: {
    onValueChange(e) {
      this.$emit('filterChanged', { code: e.target.id, filterType: this.$props.filterType });
    },
    toggleFilterVisibility() {
      this.filtersVisible = !this.filtersVisible;
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
.rotImg{
  transform: rotate(180deg);
}
label {
  color: #333333;
}
</style>
