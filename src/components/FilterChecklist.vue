<template>
  <fieldset>
    <legend class="filters-title">{{ title }}</legend>

    <div v-for="(item, index) in options" :key="index">
      <input type="checkbox"
             class="filter-checkbox"
             :id="item.code"
             :key="index"
             :checked="item.checked" />
      <label :for="item.code">{{ item.name }}</label>
    </div>
  </fieldset>
</template>

<script>
export default {
  name: 'filter-check-list',
  props: ['options', 'title'],
};
</script>

<style lang="scss" scoped>

</style>
