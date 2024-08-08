<script setup lang="ts">
import { definePageMeta } from "#imports"

import { computed } from "vue"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { SWITCHABLE, ON, OFF } from "~/constants/feature-flag"

import VContentPage from "~/components/VContentPage.vue"
import VCheckbox from "~/components/VCheckbox/VCheckbox.vue"

defineOptions({
  name: "PreferencesPage",
})

definePageMeta({
  layout: "content-layout",
})

const featureFlagStore = useFeatureFlagStore()

const flags = computed(() => featureFlagStore.flags)

/**
 * Toggle the state of the switchable flag to the preferred value.
 * @param name
 * @param checked
 */
const handleChange = ({
  name,
  checked,
}: {
  name: string
  checked?: boolean
}) => {
  featureFlagStore.toggleFeature(name, checked ? ON : OFF)
}

const flagsBySwitchable = computed(() => {
  return {
    true: featureFlagStore.getFlagsBySwitchable(true),
    false: featureFlagStore.getFlagsBySwitchable(false),
  }
})

const featureGroups = computed(() => {
  return featureFlagStore.getFeatureGroups()
})
</script>

<template>
  <VContentPage>
    <h1>{{ $t("prefPage.title") }}</h1>

    <!-- TODO: Extract this to preferences modal. -->
    <!--
    This area only lists switchable flags because if the flag is not switchable,
    it doesn't count as a user preference.
    -->
    <div
      v-for="group in featureGroups"
      :key="group.title"
      class="not-prose border-b border-default py-6 last-of-type:border-b-0"
    >
      <h2 class="label-bold mb-2">
        {{ $t(`prefPage.groups.${group.title}.title`) }}
      </h2>
      <p class="label-regular mb-4">
        {{
          $t(`prefPage.groups.${group.title}.desc`, { openverse: "Openverse" })
        }}
      </p>
      <ul>
        <li
          v-for="flag in group.features"
          :key="flag.name"
          class="mb-4 last:mb-0"
        >
          <VCheckbox
            v-if="flag.status === SWITCHABLE"
            :id="flag.name"
            class="flex-row items-center"
            :checked="flag.state === ON"
            is-switch
            @change="handleChange"
            >{{ $t(`prefPage.features.${flag.name}`) }}</VCheckbox
          >
        </li>
      </ul>
    </div>

    <div
      v-for="isSwitchable in [false, true]"
      :key="`${isSwitchable}`"
      class="not-prose border-b border-default py-6 last-of-type:border-b-0"
    >
      <h2 class="label-bold mb-2">
        {{ $t(`prefPage.${isSwitchable ? "s" : "nonS"}witchable.title`) }}
      </h2>
      <p class="label-regular mb-4">
        {{ $t(`prefPage.${isSwitchable ? "s" : "nonS"}witchable.desc`) }}
      </p>
      <ul>
        <li
          v-for="flag in flagsBySwitchable[`${isSwitchable}`]"
          :key="flag.name"
          class="mb-4 flex flex-row items-center last:mb-0"
        >
          <VCheckbox
            :id="flag.name"
            class="flex-row items-center"
            :checked="flag.state === ON"
            :disabled="flag.status !== SWITCHABLE"
            is-switch
            @change="handleChange"
          >
            <div>
              <strong>{{ flag.name }}</strong>
              <br />
              {{ flag.description }}
            </div>
          </VCheckbox>
        </li>
      </ul>
    </div>

    <h2>{{ $t("prefPage.storeState") }}</h2>
    <pre><code>{{ flags }}</code></pre>
  </VContentPage>
</template>
