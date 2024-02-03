<template>
  <section id="safe-browsing" aria-labelledby="safe-browsing-heading">
    <header class="relative mb-6 flex items-center justify-between">
      <h4 id="safe-browsing-heading" class="caption-bold uppercase">
        {{ t("filters.safeBrowsing.title") }}
      </h4>
    </header>
    <i18n-t
      scope="global"
      tag="p"
      keypath="filters.safeBrowsing.desc"
      class="label-regular"
    >
      <template #sensitive>
        <VLink :href="sensitivityPath">{{
          t("filters.safeBrowsing.sensitive")
        }}</VLink>
      </template>
    </i18n-t>
    <form class="safe-browsing-form">
      <fieldset class="mb-10 mt-8 flex flex-col gap-8">
        <div v-for="toggle in toggles" :key="toggle.name">
          <VCheckbox
            :id="toggle.name"
            class="flex-row-reverse justify-between"
            :value="toggle.name"
            :checked="toggle.state.value"
            :disabled="isDisabled(toggle.name)"
            is-switch
            @change="toggle.switchFn"
          >
            <span class="label-bold">{{
              t(`filters.safeBrowsing.toggles.${toggle.name}.title`)
            }}</span>
          </VCheckbox>
          <p
            class="label-regular mt-2"
            :class="{ 'text-dark-charcoal-40': isDisabled(toggle.name) }"
          >
            {{ t(`filters.safeBrowsing.toggles.${toggle.name}.desc`) }}
          </p>
        </div>
      </fieldset>
    </form>
  </section>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { computed } from "vue"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useUiStore } from "~/stores/ui"
import { useAnalytics } from "~/composables/use-analytics"
import { ON, OFF } from "~/constants/feature-flag"

import VCheckbox from "~/components/VCheckbox/VCheckbox.vue"
import VLink from "~/components/VLink.vue"

/**
 * Contains toggles to determine the users preferences towards fetching results
 * that may contain sensitive content and subsequently blurring them to prevent
 * accidental exposure or showing them directly.
 */
const {
  $i18n: { t },
  $localePath,
} = useNuxtApp()

const sensitivityPath = computed(() => $localePath("/sensitive-content"))

const featureFlagStore = useFeatureFlagStore()
const { sendCustomEvent } = useAnalytics()

let fetchSensitive = computed(() => featureFlagStore.isOn("fetch_sensitive"))
let setFetchSensitive = ({ checked }: { checked: boolean }) => {
  featureFlagStore.toggleFeature("fetch_sensitive", checked ? ON : OFF)
  sendCustomEvent("TOGGLE_FETCH_SENSITIVE", { checked })

  if (!checked) {
    // If sensitive content is not fetched, there is nothing to blur/unblur.
    // In this case, we reset blurring to its default value.
    setBlurSensitive({ checked: true })
  }
}

const uiStore = useUiStore()
let blurSensitive = computed(() => uiStore.shouldBlurSensitive)
let setBlurSensitive = ({ checked }: { checked: boolean }) => {
  uiStore.setShouldBlurSensitive(checked)
  sendCustomEvent("TOGGLE_BLUR_SENSITIVE", { checked })
}

const toggles = [
  {
    name: "fetchSensitive",
    state: fetchSensitive,
    switchFn: setFetchSensitive,
  },
  {
    name: "blurSensitive",
    state: blurSensitive,
    switchFn: setBlurSensitive,
  },
]

const isDisabled = (name: string) => {
  return name === "blurSensitive" && !fetchSensitive.value
}
</script>
