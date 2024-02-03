<template>
  <VPopover
    ref="contentMenuPopover"
    :label="t('searchType.label')"
    placement="bottom-end"
    :clippable="true"
    :trap-focus="false"
  >
    <template #trigger="{ a11yProps }">
      <VSearchTypeButton
        id="search-type-button"
        v-bind="{ ...a11yProps, ...searchTypeProps }"
        :show-label="showLabel"
        aria-controls="content-switcher-popover"
      />
    </template>
    <VSearchTypes
      id="content-switcher-popover"
      size="small"
      :use-links="placement === 'header'"
      @select="handleSelect"
    />
  </VPopover>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { computed, ref } from "vue"

import useSearchType from "~/composables/use-search-type"

import type { SearchType } from "~/constants/media"

import VPopover from "~/components/VPopover/VPopover.vue"
import VSearchTypeButton from "~/components/VContentSwitcher/VSearchTypeButton.vue"
import VSearchTypes from "~/components/VContentSwitcher/VSearchTypes.vue"

withDefaults(
  defineProps<{
    showLabel?: boolean
    placement?: "header" | "searchbar"
  }>(),
  {
    showLabel: false,
    placement: "header",
  }
)

const emit = defineEmits<{
  select: [SearchType]
}>()
const {
  $i18n: { t },
} = useNuxtApp()
const contentMenuPopover = ref<InstanceType<typeof VPopover> | null>(null)

const { getSearchTypeProps } = useSearchType()

const searchTypeProps = computed(() => getSearchTypeProps())

const handleSelect = (searchType: SearchType) => {
  emit("select", searchType)
  contentMenuPopover.value?.close()
}
</script>
