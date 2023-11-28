<template>
  <dt>
    {{ $t(datum.label) }}
    <VTooltip placement="top" :describedby="describedby" class="ms-2">
      <template #default>
        <p
          class="caption-regular rounded-sm bg-dark-charcoal px-2 py-1 text-white"
        >
          {{ description }}
        </p>
      </template>
    </VTooltip>
  </dt>
</template>
<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { Metadata } from "~/types/media"
import { useI18n } from "~/composables/use-i18n"

import VTooltip from "~/components/VTooltip/VTooltip.vue"

export default defineComponent({
  name: "VSourceProviderTooltip",
  components: { VTooltip },
  props: {
    datum: {
      type: Object as PropType<Metadata>,
      required: true,
    },
    describedby: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const i18n = useI18n()
    const description = computed(() => {
      if (!props.datum.name) {
        return ""
      }
      return i18n.t(
        props.datum.name === "source"
          ? "mediaDetails.sourceDescription"
          : "mediaDetails.providerDescription"
      )
    })

    return {
      description,
    }
  },
})
</script>
