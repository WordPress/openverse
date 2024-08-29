<script setup lang="ts">
import { computed } from "vue"

import { useUiStore } from "~/stores/ui"

import VButton from "~/components/VButton.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"

defineEmits<{ click: [] }>()

const uiStore = useUiStore()
const isMd = computed(() => uiStore.isBreakpoint("md"))
</script>

<template>
  <div>
    <VButton
      v-if="isMd"
      variant="transparent-gray"
      class="label-bold"
      size="small"
      has-icon-end
      @click="$emit('click')"
    >
      <span class="hidden md:block">{{
        $t("sensitiveContent.singleResult.hide")
      }}</span>
      <VIcon name="eye-closed" />
    </VButton>
    <VIconButton
      v-else
      variant="transparent-gray"
      :icon-props="{ name: 'eye-closed' }"
      size="small"
      :label="$t('sensitiveContent.singleResult.hide')"
      @click="$emit('click')"
    />
  </div>
</template>
