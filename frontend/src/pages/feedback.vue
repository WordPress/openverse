<template>
  <VContentPage>
    <h1 id="feedback">
      {{ $t("feedback.title") }}
    </h1>
    <i18n-t scope="global" keypath="feedback.intro" tag="p">
      <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
      <template #openverse>Openverse</template>
      <template #slack>
        <VLink href="https://wordpress.slack.com/messages/openverse/"
          >#openverse</VLink
        >
      </template>
      <template #makingWordpress>
        <VLink href="https://make.wordpress.org/chat/">Making WordPress</VLink>
      </template>
      <!-- eslint-enable @intlify/vue-i18n/no-raw-text -->
    </i18n-t>
    <section>
      <VTabs label="#feedback" variant="plain" :selected-id="tabs[0]" manual>
        <template #tabs>
          <VTab v-for="tab in tabs" :id="tab" :key="tab">
            {{ $t(`feedback.${tab}`) }}
          </VTab>
        </template>
        <VTabPanel v-for="tab in tabs" :id="tab" :key="tab">
          <iframe
            class="h-[1200px] w-full border-0"
            :src="forms[tab]"
            :aria-label="$t(`feedback.aria.${tab}`)"
            :title="$t(`feedback.aria.${tab}`)"
          >
            {{ $t("feedback.loading") }}
          </iframe>
        </VTabPanel>
      </VTabs>
    </section>
  </VContentPage>
</template>

<script setup lang="ts">
import { definePageMeta, useHead, useI18n } from "#imports"

import VLink from "~/components/VLink.vue"
import VContentPage from "~/components/VContentPage.vue"
import VTabs from "~/components/VTabs/VTabs.vue"
import VTab from "~/components/VTabs/VTab.vue"
import VTabPanel from "~/components/VTabs/VTabPanel.vue"

const bugForm =
  "https://docs.google.com/forms/d/e/1FAIpQLSenCn-3HoZlCz4vlL2621wjezfu1sPZDaWGe_FtQ1R5-5qR4Q/viewform"
const suggestionForm =
  "https://docs.google.com/forms/d/e/1FAIpQLSfGC7JWbNjGs-_pUNe3B2nzBW-YrIrmRd92t-7u0y7s8jMjzQ/viewform"

const forms = {
  report: `${bugForm}?embedded=true`,
  improve: `${suggestionForm}?embedded=true`,
} as const
const tabs = Object.keys(forms) as (keyof typeof forms)[]

definePageMeta({
  layout: "content-layout",
})

const { t } = useI18n({ useScope: "global" })

useHead({
  title: `${t("feedback.title")} | Openverse`,
  meta: [{ hid: "robots", name: "robots", content: "all" }],
})
</script>
