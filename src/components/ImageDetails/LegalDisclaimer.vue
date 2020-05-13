<template>
  <div class="margin-top-normal">
    <p class="caption has-text-left has-text-grey-dark has-text-weight-semibold">
      CC Search aggregates data from publicly available repositories of open content.
      CC does not host the content and does not verify that the content is properly
      CC-licensed or that the attribution information is accurate or complete.
      Please follow the link to the source of the content to independently verify before reuse.
    </p>
  </div>
</template>

<script>
export default {
  name: 'legal-disclaimer',
};
</script>

<style lang="scss" scoped>
  li:before{
    content: "\2022";
    color: #CCC;
    font-weight: bold;
    display: inline-block;
    margin-right: .5rem;
    font-size: 1rem;
  }
</style>
