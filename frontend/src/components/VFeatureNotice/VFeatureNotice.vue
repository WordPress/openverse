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
  <VLink
    :href="seeMoreHref"
    class="border-gradient group flex h-10 w-full flex-row items-center gap-2 rounded-full border border-double border-tx bg-origin-border pe-4 ps-2 hover:no-underline sm:w-[23.125rem]"
    @click="handleClick"
  >
    <div
      class="flex h-6 items-center rounded-full bg-primary px-2 text-xs font-semibold uppercase text-over-negative"
    >
      {{ $t("notification.new") }}
    </div>
    <div class="label-regular flex-grow text-default">
      <!-- @slot Content goes here. -->
      <slot />
    </div>
    <span
      class="label-bold text-default group-hover:underline group-focus:underline"
      >{{ $t("notification.more") }}</span
    >
  </VLink>
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
