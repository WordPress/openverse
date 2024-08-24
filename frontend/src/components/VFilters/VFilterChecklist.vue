<script setup lang="ts">
import { useI18n } from "#imports"

import { useSearchStore } from "~/stores/search"

import type { FilterItem, FilterCategory } from "~/constants/filters"
import type { License } from "~/constants/license"

import { getElements } from "~/utils/license"

import VButton from "~/components/VButton.vue"
import VCheckbox from "~/components/VCheckbox/VCheckbox.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VLicense from "~/components/VLicense/VLicense.vue"
import VLicenseExplanation from "~/components/VFilters/VLicenseExplanation.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"

type toggleFilterPayload = {
  filterType: FilterCategory
  code: string
}

const props = withDefaults(
  defineProps<{
    options?: FilterItem[]
    title?: string
    filterType: FilterCategory
    disabled?: boolean
  }>(),
  {
    disabled: false,
  }
)

const emit = defineEmits<{
  "toggle-filter": [toggleFilterPayload]
}>()

const { t } = useI18n({ useScope: "global" })

const itemLabel = (item: FilterItem) =>
  ["audioProviders", "imageProviders"].indexOf(props.filterType) > -1
    ? item.name
    : t(item.name)

const onValueChange = ({ value }: { value: string }) => {
  emit("toggle-filter", {
    code: value,
    filterType: props.filterType,
  })
}
const getLicenseExplanationCloseAria = (license: License) => {
  const elements = getElements(license).filter((icon) => icon !== "cc")
  const descriptions = elements
    .map((element) => t(`browsePage.licenseDescription.${element}`))
    .join(" ")
  const close = t("modal.closeNamed", {
    name: t("browsePage.aria.licenseExplanation"),
  })
  return `${descriptions} - ${close}`
}

const isDisabled = (item: FilterItem) =>
  useSearchStore().isFilterDisabled(item, props.filterType) ?? props.disabled

const isLicense = (code: string): code is License => {
  // Quick check that also prevents "`code` is declared but its value is never read" warning.
  return !!code && props.filterType === "licenses"
}

const getTitle = (code: string) => {
  return isLicense(code)
    ? t("filters.licenseExplanation.licenseDefinition")
    : t("filters.licenseExplanation.markDefinition", {
        mark: code.toUpperCase(),
      })
}
</script>

<template>
  <fieldset class="mb-8">
    <legend class="label-bold">{{ title }}</legend>
    <div
      v-for="item in options"
      :key="item.code"
      class="mt-4 flex items-center justify-between"
    >
      <VCheckbox
        :id="item.code"
        :key="item.code"
        :checked="item.checked"
        :name="title"
        :value="item.code"
        :disabled="isDisabled(item)"
        @change="onValueChange"
      >
        <VLicense v-if="isLicense(item.code)" :license="item.code" />
        <template v-else>{{ itemLabel(item) }}</template>
      </VCheckbox>

      <!-- License explanation -->
      <VModal
        v-if="isLicense(item.code)"
        :id="item.code"
        variant="centered"
        :hide-on-click-outside="true"
        :label="$t('browsePage.aria.licenseExplanation')"
      >
        <template #trigger="{ a11yProps }">
          <VButton
            v-bind="a11yProps"
            variant="transparent-tx"
            size="disabled"
            :aria-label="$t('browsePage.aria.licenseExplanation')"
            class="h-6 w-6"
          >
            <VIcon name="help" />
          </VButton>
        </template>
        <template #title>
          <h5 class="text-base font-semibold">
            {{ getTitle(item.code) }}
          </h5>
        </template>
        <template #close-button="{ close }">
          <VIconButton
            :label="getLicenseExplanationCloseAria(item.code)"
            :icon-props="{ name: 'close' }"
            variant="transparent-gray"
            size="small"
            @click="close"
          />
        </template>
        <template #default>
          <VLicenseExplanation :license="item.code" />
        </template>
      </VModal>
    </div>
  </fieldset>
</template>
