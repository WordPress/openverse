<script setup lang="ts">
import { useRuntimeConfig } from "#imports"

import { computed, ref } from "vue"

import { ofetch } from "ofetch"

import {
  reasons,
  DMCA,
  OTHER,
  SENT,
  FAILED,
  WIP,
  DMCA_FORM_URL,
  type ReportReason,
} from "~/constants/content-report"

import type { AudioDetail, ImageDetail } from "~/types/media"
import { useAnalytics } from "~/composables/use-analytics"

import { mediaSlug } from "~/utils/query-utils"

import VButton from "~/components/VButton.vue"
import VRadio from "~/components/VRadio/VRadio.vue"
import VDmcaNotice from "~/components/VContentReport/VDmcaNotice.vue"
import VReportDescForm from "~/components/VContentReport/VReportDescForm.vue"
import VLink from "~/components/VLink.vue"

const props = withDefaults(
  defineProps<{
    media: AudioDetail | ImageDetail
    providerName: string
    closeFn: () => void
    allowCancel?: boolean
  }>(),
  {
    allowCancel: true,
  }
)

const description = ref("")

const status = ref<string | null>(WIP)

const selectedReason = ref<ReportReason>(DMCA)

/* Buttons */
const handleCancel = () => {
  selectedReason.value = DMCA
  description.value = ""
  props.closeFn()
}

const isSubmitDisabled = computed(
  () => selectedReason.value === OTHER && description.value.length < 20
)

const { sendCustomEvent } = useAnalytics()

const handleDmcaSubmit = () => {
  sendCustomEvent("REPORT_MEDIA", {
    id: props.media.id,
    mediaType: props.media.frontendMediaType,
    provider: props.media.provider,
    reason: selectedReason.value,
  })
  status.value = SENT
}
const handleSubmit = async (event: Event) => {
  event.preventDefault()
  // Submit report
  try {
    const mediaType = props.media.frontendMediaType
    const reason = selectedReason.value

    const {
      public: { apiUrl },
    } = useRuntimeConfig()

    await ofetch(
      `${apiUrl}v1/${mediaSlug(mediaType)}/${props.media.id}/report/`,
      {
        method: "POST",
        body: {
          mediaType,
          reason,
          identifier: props.media.id,
          description: description.value,
        },
      }
    )

    sendCustomEvent("REPORT_MEDIA", {
      mediaType,
      reason,
      id: props.media.id,
      provider: props.media.provider,
    })
    status.value = SENT
  } catch (error) {
    status.value = FAILED
  }
}
</script>

<template>
  <div id="content-report-form">
    <div v-if="status === SENT">
      <h2 class="heading-6 mb-4">
        {{ $t("mediaDetails.contentReport.success.title") }}
      </h2>
      <i18n-t
        scope="global"
        keypath="mediaDetails.contentReport.success.note"
        class="text-sm"
        tag="p"
      >
        <template #source>
          <VLink
            :href="media.foreign_landing_url"
            class="text-link hover:underline"
            >{{ providerName }}</VLink
          >
        </template>
      </i18n-t>
    </div>

    <div v-else-if="status === FAILED">
      <h2 class="heading-6 mb-4">
        {{ $t("mediaDetails.contentReport.failure.title") }}
      </h2>
      <p class="text-sm">
        {{ $t("mediaDetails.contentReport.failure.note") }}
      </p>
    </div>

    <!-- Main form -->
    <div v-else>
      <div class="heading-6 mb-4">
        {{ $t("mediaDetails.contentReport.long") }}
      </div>

      <p class="mb-4 text-sm">
        {{
          $t("mediaDetails.contentReport.form.disclaimer", {
            openverse: "Openverse",
          })
        }}
      </p>

      <form class="text-sm" @submit="handleSubmit">
        <fieldset class="flex flex-col">
          <legend class="label-bold mb-4">
            {{ $t("mediaDetails.contentReport.form.question") }}
          </legend>
          <VRadio
            v-for="reason in reasons"
            :id="reason"
            :key="reason"
            v-model="selectedReason"
            class="mb-4"
            name="reason"
            :value="reason"
          >
            {{ $t(`mediaDetails.contentReport.form.${reason}.option`) }}
          </VRadio>
        </fieldset>

        <div class="mb-4 min-h-[7rem]">
          <VDmcaNotice
            v-if="media.foreign_landing_url && selectedReason === DMCA"
            :provider="providerName"
            :foreign-landing-url="media.foreign_landing_url"
            @click="handleDmcaSubmit"
          />
          <VReportDescForm
            v-if="selectedReason !== DMCA"
            key="other"
            v-model:content="description"
            :reason="selectedReason"
            :is-required="selectedReason === OTHER"
          />
        </div>

        <div class="flex flex-row items-center justify-end gap-x-4">
          <VButton
            v-if="allowCancel"
            variant="bordered-gray"
            size="medium"
            class="label-bold"
            @click="handleCancel"
          >
            {{ $t("mediaDetails.contentReport.form.cancel") }}
          </VButton>

          <VButton
            v-if="selectedReason === DMCA"
            key="dmca"
            as="VLink"
            variant="filled-dark"
            size="medium"
            class="label-bold"
            has-icon-end
            show-external-icon
            :external-icon-size="6"
            :href="DMCA_FORM_URL"
            :send-external-link-click-event="false"
            @click="handleDmcaSubmit"
          >
            {{ $t("mediaDetails.contentReport.form.dmca.open") }}
          </VButton>
          <VButton
            v-else
            key="non-dmca"
            type="submit"
            :disabled="isSubmitDisabled"
            :focusable-when-disabled="true"
            variant="filled-dark"
            size="medium"
            class="label-bold"
            :value="$t('mediaDetails.contentReport.form.submit')"
          >
            {{ $t("mediaDetails.contentReport.form.submit") }}
          </VButton>
        </div>
      </form>
    </div>
  </div>
</template>
