<template>
  <div>
    <span class="is-block">Thank you for reporting an issue with the results of CC Search!</span>
    <span>
      We recommend doing the same
      <a :href="imageURL" target="_blank" rel="noopener">at the source</a>.</span>
  </div>
</template>

<script>
export default {
  name: 'done-message',
  props: ['imageURL'],
};
</script>
