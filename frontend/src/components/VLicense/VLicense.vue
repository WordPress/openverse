<template>
  <div class="license flex flex-row items-center gap-2">
    <div class="flex gap-1">
      <VIcon
        v-for="name in iconNames"
        :key="name"
        :class="{ 'bg-filled text-black': bgFilled }"
        view-box="0 0 30 30"
        :name="`licenses/${name}`"
        :size="4"
      />
    </div>
    <span v-show="!hideName" class="name" :aria-label="licenseName.readable">
      {{ licenseName.full }}
    </span>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { License } from "~/constants/license"
import { getFullLicenseName, getElements } from "~/utils/license"
import { camelCase } from "~/utils/case"
import { useNuxtI18n } from "~/composables/use-i18n"

import VIcon from "~/components/VIcon/VIcon.vue"

/**
 * Displays the icons for the license along with a readable display name for the
 * license.
 */
export default defineComponent({
  name: "VLicense",
  components: { VIcon },
  props: {
    /**
     * the slug of the license
     * @values
     */
    license: {
      type: String as PropType<License>,
      required: true,
    },
    /**
     * Whether to display icons filled with a white background or leave them transparent.
     */
    bgFilled: {
      type: Boolean,
      default: false,
    },
    /**
     * Either to show the license name next to the icons or hide it.
     */
    hideName: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const i18n = useNuxtI18n()

    const iconNames = computed(() => getElements(props.license))
    const licenseName = computed(() => {
      const licenseKey =
        props.license === "sampling+" ? props.license : camelCase(props.license)
      return {
        readable: i18n.t(`licenseReadableNames.${licenseKey}`).toString(),
        full: getFullLicenseName(props.license, "", i18n),
      }
    })

    return {
      iconNames,
      licenseName,
    }
  },
})
</script>

<style scoped>
.bg-filled {
  background-image: radial-gradient(circle, #ffffff 60%, transparent 60%);
}
</style>
