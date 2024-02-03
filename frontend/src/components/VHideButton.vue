<template>
  <div>
    <VButton
      v-if="isMd"
      variant="transparent-gray"
      class="label-bold"
      size="small"
      has-icon-end
      @click="emit('click')"
    >
      <span class="hidden md:block">{{
        t("sensitiveContent.singleResult.hide")
      }}</span>
      <VIcon name="eye-closed" />
    </VButton>
    <VIconButton
      v-else
      variant="transparent-gray"
      :icon-props="{ name: 'eye-closed' }"
      size="small"
      :label="t('sensitiveContent.singleResult.hide')"
      @click="emit('click')"
    />
  </div>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { computed } from "vue"

import { useUiStore } from "~/stores/ui"

const emit = defineEmits<{
  click: []
}>()

const {
  $i18n: { t },
} = useNuxtApp()

const uiStore = useUiStore()
const isMd = computed(() => uiStore.isBreakpoint("md"))
</script>
