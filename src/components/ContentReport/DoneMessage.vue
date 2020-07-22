<template>
  <div class="margin-vertical-large">
    <span class="is-block padding-horizontal-big has-text-centered">
      Thank you for reporting an issue with the results of CC Search!
    </span>
    <span
      class="is-block padding-horizontal-big margin-top-small has-text-centered"
    >
      We recommend doing the same at the source,
      <a
        :aria-label="providerName + 'form'"
        :href="imageURL"
        target="_blank"
        rel="noopener"
        >{{ providerName }}</a
      >.
    </span>
  </div>
</template>

<script>
export default {
  name: 'done-message',
  props: ['imageURL', 'providerName'],
}
</script>
