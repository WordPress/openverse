<template>
  <div>
    <span class="is-block">
      Please fill out
      <a :href="dcmaFormUrl" target="_blank" rel="noopener">this DMCA form</a>
      to report dcma infringement.
    </span>
    <span>
      We recommend doing the same
      <a :href="imageURL" target="_blank" rel="noopener">at the source</a>.
    </span>
  </div>
</template>

<script>
export default {
  name: 'dcma-notice',
  props: ['dcmaFormUrl', 'imageURL'],
};
</script>
