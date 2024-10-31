<script setup lang="ts">
import { useNuxtApp, useRuntimeConfig } from "#imports"

import { computed, ref } from "vue"

import { ofetch } from "ofetch"

import {
  reasons,
  DMCA,
  OTHER,
  SENT,
  FAILED,
  DMCA_FORM_URL,
  type ReportReason,
  type ReportStatus,
} from "~/constants/content-report"

import type { ReportableMedia } from "~/types/media"

import { mediaSlug } from "~/utils/query-utils"

import VButton from "~/components/VButton.vue"
import VRadio from "~/components/VRadio/VRadio.vue"
import VDmcaNotice from "~/components/VContentReport/VDmcaNotice.vue"
import VReportDescForm from "~/components/VContentReport/VReportDescForm.vue"
import VLink from "~/components/VLink.vue"

const props = defineProps<{
  media: ReportableMedia
  status: ReportStatus
  allowCancel: boolean
}>()

const emit = defineEmits<{
  close: []
  "update-status": [ReportStatus]
}>()

const selectedReason = ref<ReportReason>(DMCA)
const description = ref("")

const resetForm = () => {
  selectedReason.value = DMCA
  description.value = ""
}

const reportUrl = computed(() => {
  const apiUrl = useRuntimeConfig().public.apiUrl
  return `${apiUrl}v1/${mediaSlug(props.media.frontendMediaType)}/${props.media.id}/report/`
})
const dmcaFormUrl = computed(
  () =>
    `${DMCA_FORM_URL}?entry.917669540=https://openverse.org/${props.media.frontendMediaType}/${props.media.id}`
)

/* Buttons */
const handleCancel = () => {
  resetForm()
  emit("close")
}

const isSubmitDisabled = computed(
  () => selectedReason.value === OTHER && description.value.length < 20
)

const { $sendCustomEvent } = useNuxtApp()

const handleDmcaSubmit = () => {
  updateStatus(SENT)
}

const handleSubmit = async (event: Event) => {
  event.preventDefault()
  try {
    await ofetch(reportUrl.value, {
      method: "POST",
      body: {
        mediaType: props.media.frontendMediaType,
        reason: selectedReason.value,
        identifier: props.media.id,
        description: description.value,
      },
    })
    updateStatus(SENT)
  } catch {
    updateStatus(FAILED)
  }
}

const updateStatus = (newStatus: ReportStatus) => {
  if (newStatus === SENT) {
    $sendCustomEvent("REPORT_MEDIA", {
      id: props.media.id,
      mediaType: props.media.frontendMediaType,
      provider: props.media.provider,
      reason: selectedReason.value,
    })
  }
  emit("update-status", newStatus)
}

defineExpose({ resetForm })
</script>

<template>
  <div id="content-report-form">
    <div v-if="status === SENT">
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
            >{{ media.providerName }}</VLink
          >
        </template>
      </i18n-t>
    </div>

    <div v-else-if="status === FAILED">
      <p class="text-sm">
        {{ $t("mediaDetails.contentReport.failure.note") }}
      </p>
    </div>

    <!-- Main form -->
    <div v-else>
      <p class="mb-4 text-sm leading-normal">
        {{
          $t("mediaDetails.contentReport.form.disclaimer", {
            openverse: "Openverse",
          })
        }}
      </p>

      <form class="flex flex-col gap-y-4 text-sm" @submit="handleSubmit">
        <fieldset class="flex flex-col gap-y-4">
          <legend class="label-bold mb-4">
            {{ $t("mediaDetails.contentReport.form.question") }}
          </legend>
          <VRadio
            v-for="reason in reasons"
            :id="reason"
            :key="reason"
            v-model="selectedReason"
            name="reason"
            :value="reason"
          >
            {{ $t(`mediaDetails.contentReport.form.${reason}.option`) }}
          </VRadio>
        </fieldset>

        <div class="leading-normal">
          <VDmcaNotice
            v-if="selectedReason === DMCA"
            :provider="media.providerName"
            :foreign-landing-url="media.foreign_landing_url"
            @click="handleDmcaSubmit"
          />
          <VReportDescForm
            v-else
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
            :href="dmcaFormUrl"
            :send-external-link-click-event="false"
            target="_blank"
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
