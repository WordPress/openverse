<template>
  <VContentPage>
    <h1>{{ $t("prefPage.title") }}</h1>

    <!-- TODO: Extract this to preferences modal. -->
    <!--
    This area only lists switchable flags because if the flag is not switchable,
    it doesn't count as a user preference.
    -->
    <div
      v-for="(group, groupIndex) in featureData.groups"
      :key="groupIndex"
      class="not-prose border-b border-dark-charcoal-20 py-6 last-of-type:border-b-0"
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
          v-for="(name, featureIndex) in group.features"
          :key="featureIndex"
          class="mb-4 last:mb-0"
        >
          <VCheckbox
            v-if="isFlagName(name) && isSwitchable(name)"
            :id="name"
            class="flex-row items-center"
            :checked="isOn(name)"
            is-switch
            @change="handleChange"
            >{{ $t(`prefPage.features.${name}`) }}</VCheckbox
          >
        </li>
      </ul>
    </div>

    <div
      v-for="isFlagSwitchable in [false, true]"
      :key="`${isFlagSwitchable}`"
      class="not-prose border-b border-dark-charcoal-20 py-6 last-of-type:border-b-0"
    >
      <h2 class="label-bold mb-2">
        {{ $t(`prefPage.${isFlagSwitchable ? "s" : "nonS"}witchable.title`) }}
      </h2>
      <p class="label-regular mb-4">
        {{ $t(`prefPage.${isFlagSwitchable ? "s" : "nonS"}witchable.desc`) }}
      </p>
      <ul>
        <li
          v-for="[name, feature] in getFlagsBySwitchable(isFlagSwitchable)"
          :key="name"
          class="mb-4 flex flex-row items-center last:mb-0"
        >
          <VCheckbox
            :id="name"
            class="flex-row items-center"
            :checked="isOn(name)"
            :disabled="!isFlagSwitchable"
            is-switch
            @change="handleChange"
          >
            <div>
              <strong>{{ name }}</strong>
              <br />
              {{ feature.description }}
            </div>
          </VCheckbox>
        </li>
      </ul>
    </div>

    <h2>{{ $t("prefPage.storeState") }}</h2>
    <pre><code>{{ flags }}</code></pre>
  </VContentPage>
</template>

<script lang="ts">
import { computed } from "vue"
import { defineComponent } from "@nuxtjs/composition-api"

import featureData from "~~/feat/feature-flags.json"

import { useFeatureFlagStore, isFlagName } from "~/stores/feature-flag"
import { SWITCHABLE, ON, OFF, FEATURE_STATES } from "~/constants/feature-flag"

import VContentPage from "~/components/VContentPage.vue"
import VCheckbox from "~/components/VCheckbox/VCheckbox.vue"

export default defineComponent({
  name: "VPreferences",
  components: {
    VContentPage,
    VCheckbox,
  },
  layout: "content-layout",
  setup() {
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
      if (!isFlagName(name)) {
        throw new Error(
          `Cannot change the state of flag ${name}: it does not exist.`
        )
      }
      featureFlagStore.toggleFeature(name, checked ? ON : OFF)
    }

    const isOn = (name: string) => {
      if (!isFlagName(name)) {
        throw new Error(
          `Cannot check the state of flag ${name}: it does not exist.`
        )
      }
      return featureFlagStore.isOn(name)
    }

    const isSwitchable = (name: string) => {
      if (!isFlagName(name)) {
        throw new Error(
          `Cannot check the switchability of flag ${name}: it does not exist.`
        )
      }
      return featureFlagStore.isSwitchable(name)
    }

    const getFlagsBySwitchable = (switchable: boolean) => {
      return Object.entries(flags.value).filter(
        ([name]) => isSwitchable(name) === switchable
      )
    }

    return {
      ON,
      OFF,
      SWITCHABLE,
      FEATURE_STATES,

      flags,
      isOn,
      isSwitchable,

      handleChange,
      isFlagName,

      featureData,
      getFlagsBySwitchable,
    }
  },
})
</script>
