<script setup lang="ts">
import { useI18n, useNuxtApp } from "#imports"

import { onBeforeUnmount, onMounted, ref } from "vue"

import { AttributionOptions, getAttribution } from "~/utils/attribution-html"
import type { Media } from "~/types/media"

import VTabs from "~/components/VTabs/VTabs.vue"
import VTab from "~/components/VTabs/VTab.vue"
import VLicenseTabPanel from "~/components/VMediaInfo/VLicenseTabPanel.vue"

const tabs = ["rich", "html", "plain", "xml"] as const

const props = defineProps<{ media: Media }>()

const richRef = ref<HTMLElement | null>(null)

const i18n = useI18n({ useScope: "global" })
const getAttributionMarkup = (options?: AttributionOptions) =>
  getAttribution(props.media, i18n, options)

const { $sendCustomEvent } = useNuxtApp()

const sendAnalyticsEvent = (event: MouseEvent) => {
  if (!event.currentTarget) {
    return
  }

  const url = (event.currentTarget as HTMLAnchorElement).href
  $sendCustomEvent("EXTERNAL_LINK_CLICK", { url })
}

onMounted(() => {
  richRef.value?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", sendAnalyticsEvent)
  })
})

onBeforeUnmount(() => {
  richRef.value?.querySelectorAll("a").forEach((link) => {
    link.removeEventListener("click", sendAnalyticsEvent)
  })
})
</script>

<template>
  <div>
    <h3 id="copy-license-title" class="description-bold md:heading-6 mb-4">
      {{ $t("mediaDetails.reuse.copyLicense.title") }}
    </h3>

    <VTabs label="#copy-license-title" :selected-id="tabs[0]">
      <template #tabs>
        <VTab v-for="tab in tabs" :id="tab" :key="tab">
          {{ $t(`mediaDetails.reuse.copyLicense.${tab}`) }}
        </VTab>
      </template>
      <VLicenseTabPanel
        :tab="tabs[0]"
        :media-id="media.id"
        :media-type="media.frontendMediaType"
      >
        <!-- Disable reason: We control the attribution HTML generation so this is safe and will not lead to XSS attacks -->
        <!-- eslint-disable vue/no-v-html -->
        <div
          ref="richRef"
          v-html="getAttributionMarkup({ includeIcons: false })"
        />
        <!-- eslint-enable vue/no-v-html -->
      </VLicenseTabPanel>
      <VLicenseTabPanel
        :tab="tabs[1]"
        :media-id="media.id"
        :media-type="media.frontendMediaType"
      >
        <!-- Ignore reason: the interpolated string cannot have any whitespace around it when inside <p>, else there will be unwanted whitespace -->
        <!-- prettier-ignore -->
        <p id="attribution-html" class="break-all font-mono" dir="ltr">{{ getAttributionMarkup() }}</p>
      </VLicenseTabPanel>
      <VLicenseTabPanel
        :tab="tabs[2]"
        :media-id="media.id"
        :media-type="media.frontendMediaType"
      >
        <p>{{ getAttributionMarkup({ isPlaintext: true }) }}</p>
      </VLicenseTabPanel>
      <VLicenseTabPanel
        :tab="tabs[3]"
        :media-id="media.id"
        :media-type="media.frontendMediaType"
      >
        <pre
          id="attribution-xml"
          class="whitespace-pre-wrap break-all"
          dir="ltr"
          >{{ getAttributionMarkup({ isXml: true }) }}</pre
        >
      </VLicenseTabPanel>
    </VTabs>
  </div>
</template>
