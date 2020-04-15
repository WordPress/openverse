<template>
    <span>
        {{ filter.name }}
    </span>
</template>
<script>
export default {
  name: 'filter-block',
  props: ['filter'],
};
</script>
