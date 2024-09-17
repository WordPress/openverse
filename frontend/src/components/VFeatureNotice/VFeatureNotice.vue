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
    class="group flex h-10 w-full flex-row items-center gap-2 rounded-full border border-secondary pe-4 ps-2 hover:no-underline sm:w-[23.125rem]"
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
