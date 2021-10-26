<!-- noresult is hardcoded since it does not yet support built-in video search -->
<template>
  <MetaSearchForm
    id="type-video"
    type="video"
    role="tabpanel"
    :noresult="false"
    aria-labelledby="video"
  />
</template>

<script>
export default {
  name: 'VideoSearch',
}
</script>
