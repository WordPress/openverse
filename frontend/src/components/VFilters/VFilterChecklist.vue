<template>
  <fieldset class="mb-8">
    <legend class="label-bold">{{ title }}</legend>
    <div
      v-for="(item, index) in options"
      :key="index"
      class="mt-4 flex items-center justify-between"
    >
      <VCheckbox
        :id="item.code"
        :key="index"
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
      <VPopover
        v-if="isLicense(item.code)"
        strategy="fixed"
        :label="$t('browse-page.aria.license-explanation').toString()"
        :trap-focus="false"
      >
        <template #trigger="{ a11yProps }">
          <VButton
            v-bind="a11yProps"
            variant="transparent-tx"
            size="disabled"
            :aria-label="$t('browse-page.aria.license-explanation')"
            class="h-6 w-6"
          >
            <VIcon name="help" />
          </VButton>
        </template>
        <template #default="{ close }">
          <div class="relative">
            <VCloseButton
              :label="getLicenseExplanationCloseAria(item.code)"
              class="!absolute end-0 top-0"
              @close="close"
            />
            <VLicenseExplanation :license="item.code" />
          </div>
        </template>
      </VPopover>
    </div>
  </fieldset>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import { useSearchStore } from "~/stores/search"
import { useI18n } from "~/composables/use-i18n"

import type { NonMatureFilterCategory, FilterItem } from "~/constants/filters"

import type { License } from "~/constants/license"

import { defineEvent } from "~/types/emits"
import { getElements } from "~/utils/license"

import VButton from "~/components/VButton.vue"
import VCheckbox from "~/components/VCheckbox/VCheckbox.vue"
import VCloseButton from "~/components/VCloseButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VLicense from "~/components/VLicense/VLicense.vue"
import VLicenseExplanation from "~/components/VFilters/VLicenseExplanation.vue"
import VPopover from "~/components/VPopover/VPopover.vue"

type toggleFilterPayload = {
  filterType: NonMatureFilterCategory
  code: string
}

export default defineComponent({
  name: "VFilterCheckList",
  components: {
    VCloseButton,
    VCheckbox,
    VButton,
    VIcon,
    VLicense,
    VLicenseExplanation,
    VPopover,
  },
  props: {
    options: {
      type: Array as PropType<FilterItem[]>,
      required: false,
    },
    title: {
      type: String,
    },
    filterType: {
      type: String as PropType<NonMatureFilterCategory>,
      required: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: {
    "toggle-filter": defineEvent<[toggleFilterPayload]>(),
  },
  setup(props, { emit }) {
    const i18n = useI18n()

    const itemLabel = (item: FilterItem) =>
      ["audioProviders", "imageProviders"].indexOf(props.filterType) > -1
        ? item.name
        : i18n.t(item.name)

    const onValueChange = ({ value }: { value: string }) => {
      emit("toggle-filter", {
        code: value,
        filterType: props.filterType,
      })
    }
    const getLicenseExplanationCloseAria = (license: License) => {
      const elements = getElements(license).filter((icon) => icon !== "cc")
      const descriptions = elements
        .map((element) => i18n.t(`browse-page.license-description.${element}`))
        .join(" ")
      const close = i18n.t("modal.closeNamed", {
        name: i18n.t("browse-page.aria.license-explanation"),
      })
      return `${descriptions} - ${close}`
    }

    const isDisabled = (item: FilterItem) =>
      useSearchStore().isFilterDisabled(item, props.filterType) ??
      props.disabled

    const isLicense = (code: string): code is License => {
      // Quick check that also prevents "`code` is declared but its value is never read" warning.
      return !!code && props.filterType === "licenses"
    }

    return {
      isDisabled,
      itemLabel,
      onValueChange,
      getLicenseExplanationCloseAria,
      isLicense,
    }
  },
})
</script>
