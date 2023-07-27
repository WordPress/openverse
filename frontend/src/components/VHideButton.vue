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
      :icon-props="{ name: 'eye-closed' }"
      size="small"
      :label="$t('sensitiveContent.singleResult.hide').toString()"
      @click="$emit('click')"
    />
  </div>
</template>

<script>
import { computed, defineComponent } from "@nuxtjs/composition-api"

import { useUiStore } from "~/stores/ui"

export default defineComponent({
  setup() {
    const uiStore = useUiStore()
    const isMd = computed(() => uiStore.isBreakpoint("md"))

    return {
      isMd,
    }
  },
})
</script>
