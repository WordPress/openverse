<script lang="ts">
import { useI18n } from "#imports"

import { computed, defineComponent, PropType } from "vue"

import { Metadata } from "~/types/media"

import VTooltip from "~/components/VTooltip/VTooltip.vue"

export default defineComponent({
  name: "VSourceProviderTooltip",
  components: { VTooltip },
  props: {
    datum: {
      type: Object as PropType<Metadata>,
      required: true,
    },
    describedBy: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const { t } = useI18n({ useScope: "global" })
    const description = computed(() => {
      if (!props.datum.name) {
        return ""
      }
      return t(
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

<template>
  <dt>
    {{ $t(datum.label) }}
    <VTooltip placement="top" :described-by="describedBy" class="ms-1">
      <template #default>
        <p
          class="caption-regular rounded-sm bg-tertiary px-2 py-1 text-over-dark"
        >
          {{ description }}
        </p>
      </template>
    </VTooltip>
  </dt>
</template>
