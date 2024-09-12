<script setup lang="ts">
import VLink from "~/components/VLink.vue"

defineProps<{
  seeMoreHref: string
}>()

const emit = defineEmits<{
  click: [MouseEvent]
}>()

const handleClick = (e: MouseEvent) => {
  emit("click", e)
}
</script>

<template>
  <div
    class="border-gradient flex h-10 w-[23.125rem] flex-row items-center gap-2 rounded-full border border-double border-tx bg-origin-border pe-4 ps-2"
  >
    <div
      class="flex h-6 items-center rounded-full bg-primary px-2 text-xs font-semibold uppercase text-over-negative"
    >
      {{ $t("notification.new") }}
    </div>
    <div class="label-regular flex-grow">
      <!-- @slot Content goes here. -->
      <slot />
    </div>
    <VLink
      :href="seeMoreHref"
      class="label-bold cursor-pointer text-default"
      @click="handleClick"
      >{{ $t("notification.more") }}</VLink
    >
  </div>
</template>

<style>
/**
 * To get the border gradient we use two backgrounds:
 * - one gradient sized to the border box
 * - one flat color sized to the padding box
 */
.border-gradient {
  background-image: linear-gradient(
      var(--color-bg-curr-page),
      var(--color-bg-curr-page)
    ),
    linear-gradient(
      to right,
      var(--color-new-highlight),
      var(--color-gray-new-highlight)
    );
  background-clip: padding-box, border-box;
}
</style>
