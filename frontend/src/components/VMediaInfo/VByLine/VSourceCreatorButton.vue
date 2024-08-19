<script setup lang="ts">
import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"

defineProps<{
  href: string
  iconName: "person" | "institution"
  title: string
}>()
</script>

<template>
  <VButton
    as="VLink"
    size="small"
    has-icon-start
    class="label-bold !bg-secondary hover:!bg-tertiary hover:!text-over-dark sm:!bg-tx"
    variant="transparent-gray"
    :href="href"
  >
    <VIcon :name="iconName" />
    <span class="w-max">{{ title }}</span>
  </VButton>
</template>
