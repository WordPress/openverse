<script setup lang="ts">
/**
 * Displays the icons for the license along with a readable display name for the
 * license.
 */
import { useI18n } from "#imports"

import { computed } from "vue"

import type { License } from "~/constants/license"
import { getFullLicenseName, getElements } from "~/utils/license"
import { camelCase } from "~/utils/case"

import VIcon from "~/components/VIcon/VIcon.vue"

const props = withDefaults(
  defineProps<{
    /**
     * the slug of the license
     * @values
     */
    license: License
    /**
     * Whether to display icons filled with a white background or leave them transparent.
     */
    bgFilled?: boolean
    /**
     * Either to show the license name next to the icons or hide it.
     */
    hideName?: boolean
  }>(),
  {
    bgFilled: false,
    hideName: false,
  }
)

const i18n = useI18n({ useScope: "global" })

const iconNames = computed(() => getElements(props.license))
const licenseName = computed(() => {
  const licenseKey =
    props.license === "sampling+" ? props.license : camelCase(props.license)
  return {
    readable: i18n.t(`licenseReadableNames.${licenseKey}`),
    full: getFullLicenseName(props.license, "", i18n),
  }
})
</script>

<template>
  <div class="license flex flex-row items-center gap-2">
    <div class="flex gap-1">
      <VIcon
        v-for="name in iconNames"
        :key="name"
        :class="{ 'license-bg text-black': bgFilled }"
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

<style scoped>
.license-bg {
  background-image: radial-gradient(circle, #ffffff 60%, transparent 60%);
}
</style>
