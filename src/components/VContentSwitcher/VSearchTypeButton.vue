<template>
  <VButton
    class="group flex h-12 w-12 flex-row xl:w-auto xl:px-2 xl:ps-3"
    variant="action-menu"
    size="disabled"
    :aria-label="buttonLabel"
    v-bind="a11yProps"
    @click="$emit('click')"
  >
    <VIcon :icon-path="icon" />
    <span
      class="label-regular hidden truncate xl:block xl:ms-2 xl:text-start"
      >{{ buttonLabel }}</span
    >
    <VIcon class="hidden xl:block xl:ms-2" :icon-path="caretDownIcon" />
  </VButton>
</template>
<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api"

import { ALL_MEDIA, AUDIO, IMAGE, MODEL_3D, VIDEO } from "~/constants/media"
import useSearchType from "~/composables/use-search-type"
import { useI18n } from "~/composables/use-i18n"

import VIcon from "~/components/VIcon/VIcon.vue"
import VButton from "~/components/VButton.vue"

import caretDownIcon from "~/assets/icons/caret-down.svg"

const labels = {
  [ALL_MEDIA]: "search-type.all",
  [IMAGE]: "search-type.image",
  [AUDIO]: "search-type.audio",
  [VIDEO]: "search-type.video",
  [MODEL_3D]: "search-type.model-3d",
}

/**
 * This is the search type button that appears in the header, not on the homepage.
 */
export default defineComponent({
  name: "VSearchTypeButton",
  components: { VButton, VIcon },
  props: {
    a11yProps: {
      type: Object,
      default: () => ({
        "aria-expanded": false,
        "aria-haspopup": "dialog",
      }),
    },
  },
  setup() {
    const i18n = useI18n()
    const { icons, activeType } = useSearchType()

    const activeItem = computed(() => activeType.value)

    const buttonLabel = computed(() => i18n.t(labels[activeItem.value]))

    const icon = computed(() => icons[activeItem.value])

    return {
      buttonLabel,
      caretDownIcon,
      icon,
    }
  },
})
</script>
