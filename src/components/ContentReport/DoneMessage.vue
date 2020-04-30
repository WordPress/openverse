<template>
  <div class="margin-vertical-large">
    <span class="is-block padding-horizontal-big">
      Thank you for reporting an issue with the results of CC Search!
    </span>
    <span class="is-block padding-horizontal-big margin-top-small">
      We recommend doing the same
      <a :href="imageURL" target="_blank" rel="noopener">at the source  {{ providerName }}</a>.
    </span>
  </div>
</template>

<script>
export default {
  name: 'done-message',
  props: ['imageURL', 'providerName'],
};
</script>
