<script setup lang="ts">
import VButton from "~/components/VButton.vue"

const props = defineProps<{ href: string }>()
</script>

<template>
  <VButton
    as="VLink"
    size="small"
    variant="filled-gray"
    class="label-bold"
    v-bind="props"
    ><slot
  /></VButton>
</template>
