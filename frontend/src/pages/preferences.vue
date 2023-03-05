<template>
  <VContentPage>
    <h1>{{ $t("pref-page.title") }}</h1>

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
        {{ $t(`pref-page.groups.${group.title}.title`) }}
      </h2>
      <p class="label-regular mb-4">
        {{ $t(`pref-page.groups.${group.title}.desc`) }}
      </p>
      <ul>
        <li
          v-for="(name, featureIndex) in group.features"
          :key="featureIndex"
          class="mb-4 last:mb-0"
        >
          <VCheckbox
            v-if="getFlagStatus(featureData.features[name]) === SWITCHABLE"
            :id="name"
            class="flex-row items-center"
            :checked="featureState(name) === ON"
            is-switch
            @change="handleChange"
            >{{ $t(`pref-page.features.${name}`) }}</VCheckbox
          >
        </li>
      </ul>
    </div>

    <div
      v-for="isSwitchable in [false, true]"
      :key="isSwitchable"
      class="not-prose border-b border-dark-charcoal-20 py-6 last-of-type:border-b-0"
    >
      <h2 class="label-bold mb-2">
        {{ $t(`pref-page.${isSwitchable ? "" : "non-"}switchable.title`) }}
      </h2>
      <p class="label-regular mb-4">
        {{ $t(`pref-page.${isSwitchable ? "" : "non-"}switchable.desc`) }}
      </p>
      <ul>
        <template v-for="(feature, name) in flags">
          <li
            v-if="(getFlagStatus(feature) === SWITCHABLE) === isSwitchable"
            :key="name"
            class="mb-4 flex flex-row items-center last:mb-0"
          >
            <VCheckbox
              :id="name"
              class="flex-row items-center"
              :checked="featureState(name) === ON"
              :disabled="!isSwitchable"
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
        </template>
      </ul>
    </div>

    <h2>{{ $t("pref-page.store-state") }}</h2>
    <pre><code>{{ flags }}</code></pre>

    <h2>{{ $t("pref-page.content-filtering") }}</h2>
    <ul>
      <template v-for="(_, featName) in flags">
        <template v-for="featState in FEATURE_STATES">
          <i18n
            v-if="featureState(featName) === featState"
            :key="`${featName}-${featState}`"
            path="pref-page.explanation"
            tag="li"
          >
            <template #feat-name
              ><code>{{ featName }}</code></template
            >
            <template #feat-state
              ><code>{{ featState }}</code></template
            >
          </i18n>
        </template>
      </template>
      <!--<i18n
        v-if="featureState('feat_nonexistent') === ON"
        path="pref-page.explanation"
        tag="li"
      >
        <template #feat-name
          ><code>{{ $t('flag-status.nonexistent') }}</code></template
        >
        <template #feat-state
          ><code>{{ $t(`flag-status.${ON}`) }}</code></template
        >
      </i18n>-->
    </ul>
  </VContentPage>
</template>

<script lang="ts">
import { computed, defineComponent } from "vue"
import { useContext } from "@nuxtjs/composition-api"

import featureData from "~~/feat/feature-flags.json"

import { useFeatureFlagStore, getFlagStatus } from "~/stores/feature-flag"
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
    const { $cookies } = useContext()
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
      checked: boolean
    }) => {
      featureFlagStore.toggleFeature(name, checked ? ON : OFF)
      $cookies.set("features", featureFlagStore.flagStateMap)
    }

    return {
      ON,
      OFF,
      SWITCHABLE,
      FEATURE_STATES,

      flags,
      featureState: featureFlagStore.featureState,

      handleChange,
      getFlagStatus,

      featureData,
    }
  },
})
</script>
