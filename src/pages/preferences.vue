<template>
  <VContentPage>
    <h1>{{ $t('pref-page.title') }}</h1>

    <div v-for="isSwitchable in [false, true]" :key="isSwitchable">
      <h2>
        {{ $t(`pref-page.${isSwitchable ? '' : 'non-'}switchable.title`) }}
      </h2>
      <p>
        {{ $t(`pref-page.${isSwitchable ? '' : 'non-'}switchable.desc`) }}
      </p>
      <ul class="!ps-0">
        <template v-for="(feature, name) in flags">
          <li
            v-if="(feature.status === SWITCHABLE) === isSwitchable"
            :key="name"
            class="flex flex-row items-center"
          >
            <VCheckbox
              :id="name"
              class="flex-row items-center"
              :checked="featureState(name) === ON"
              :disabled="!isSwitchable"
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

    <h2>{{ $t('pref-page.store-state') }}</h2>
    <pre><code>{{ flags }}</code></pre>

    <h2>{{ $t('pref-page.content-filtering') }}</h2>
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
      <i18n
        v-if="featureState('feat_nonexistent') === ON"
        path="pref-page.explanation"
        tag="li"
      >
        <template #feat-name
          ><code>{{ $t('feat_nonexistent') }}</code></template
        >
        <template #feat-state
          ><code>{{ $t(ON) }}</code></template
        >
      </i18n>
    </ul>
  </VContentPage>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from '@nuxtjs/composition-api'

import { useFeatureFlagStore } from '~/stores/feature-flag'
import { SWITCHABLE, ON, OFF, FEATURE_STATES } from '~/constants/feature-flag'

import VContentPage from '~/components/VContentPage.vue'
import VCheckbox from '~/components/VCheckbox/VCheckbox.vue'

export default defineComponent({
  name: 'VPreferences',
  components: {
    VContentPage,
    VCheckbox,
  },
  setup() {
    const { app } = useContext()
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
      app.$cookies.set('features', featureFlagStore.flagStateMap)
    }

    return {
      ON,
      OFF,
      SWITCHABLE,
      FEATURE_STATES,

      flags,
      featureState: featureFlagStore.featureState,

      handleChange,
    }
  },
})
</script>
