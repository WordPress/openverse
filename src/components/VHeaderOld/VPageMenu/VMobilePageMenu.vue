<template>
  <VModal
    class="flex justify-center"
    :label="$t('header.filter-button.simple').toString()"
  >
    <template #trigger="{ a11yProps, visible }">
      <VPageMenuButton :a11y-props="a11yProps" :visible="visible" />
    </template>
    <nav class="p-4">
      <VPageList layout="columns" />
    </nav>
  </VModal>
</template>

<script>
import { defineComponent } from "@nuxtjs/composition-api"

import VModal from "~/components/VModal/VModal.vue"
import VPageMenuButton from "~/components/VHeaderOld/VPageMenu/VPageMenuButton.vue"
import VPageList from "~/components/VHeaderOld/VPageMenu/VPageList.vue"

export default defineComponent({
  name: "VMobilePageMenu",
  components: { VModal, VPageMenuButton, VPageList },
})
</script>
