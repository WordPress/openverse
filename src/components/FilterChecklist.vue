<template>
  <fieldset>
    <legend class="filters-title">{{ title }}</legend>

    <div v-for="(item, index) in options" :key="index">
      <input type="checkbox"
             class="filter-checkbox"
             :id="item.code"
             :key="index"
             :checked="item.checked"
             @change="onValueChange" />
      <label class="filter-label" :for="item.code">{{ item.name }}</label>
    </div>
  </fieldset>
</template>

<script>
export default {
  name: 'filter-check-list',
  props: ['options', 'title'],
  methods: {
    onValueChange(e) {
      const option = this.$props.options.filter(opt => opt.code === e.target.id);
      if (option) {
        this.$emit('filterChanged', { option: option[0] });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.filters-title {
  font-size: 1.3em;
  font-weight: 700;
}

.filter-label {
  font-weight: 600;
}
</style>
