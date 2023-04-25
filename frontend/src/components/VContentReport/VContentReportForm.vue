<template>
  <div id="content-report-form">
    <div v-if="status === SENT">
      <p class="heading-6 mb-4">
        {{ $t("media-details.content-report.success.title") }}
      </p>
      <i18n
        path="media-details.content-report.success.note"
        class="text-sm"
        tag="p"
      >
        <template #source>
          <VLink
            :href="media.foreign_landing_url"
            class="text-pink hover:underline"
            >{{ providerName }}</VLink
          >
        </template>
      </i18n>
    </div>

    <div v-else-if="status === FAILED">
      <p class="heading-6 mb-4">
        {{ $t("media-details.content-report.failure.title") }}
      </p>
      <p class="text-sm">
        {{ $t("media-details.content-report.failure.note") }}
      </p>
    </div>

    <!-- Main form -->
    <div v-else>
      <div class="heading-6 mb-4">
        {{ $t("media-details.content-report.long") }}
      </div>

      <p class="mb-4 text-sm">
        {{
          $t("media-details.content-report.form.disclaimer", {
            openverse: "Openverse",
          })
        }}
      </p>

      <form class="text-sm" @submit="handleSubmit">
        <fieldset class="flex flex-col">
          <legend class="label-bold mb-4">
            {{ $t("media-details.content-report.form.question") }}
          </legend>
          <VRadio
            v-for="reason in reasons"
            :id="reason"
            :key="reason"
            v-model="selectedReason"
            class="mb-4"
            name="reason"
            :value_="reason"
          >
            {{ $t(`media-details.content-report.form.${reason}.option`) }}
          </VRadio>
        </fieldset>

        <div class="mb-4 min-h-[7rem]">
          <VDmcaNotice
            v-if="media.foreign_landing_url && selectedReason === DMCA"
            :provider="providerName"
            :foreign-landing-url="media.foreign_landing_url"
          />
          <VReportDescForm
            v-if="selectedReason !== DMCA"
            key="other"
            v-model="description"
            :reason="selectedReason"
            :is-required="selectedReason === OTHER"
          />
        </div>

        <div class="flex flex-row items-center justify-end gap-4">
          <VButton
            v-if="allowCancel"
            variant="secondary-bordered"
            @click="handleCancel"
          >
            {{ $t("media-details.content-report.form.cancel") }}
          </VButton>

          <VButton
            v-if="selectedReason === DMCA"
            key="dmca"
            as="VLink"
            variant="secondary-filled"
            :href="DMCA_FORM_URL"
          >
            {{ $t("media-details.content-report.form.dmca.open") }}
            <VIcon :size="4" class="ms-1" name="external-link" />
          </VButton>
          <VButton
            v-else
            key="non-dmca"
            type="submit"
            :disabled="isSubmitDisabled"
            :focusable-when-disabled="true"
            variant="secondary-filled"
            :value="$t('media-details.content-report.form.submit')"
          >
            {{ $t("media-details.content-report.form.submit") }}
          </VButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType, ref } from "vue"

import ReportService from "~/data/report-service"

import {
  reasons,
  DMCA,
  OTHER,
  SENT,
  FAILED,
  WIP,
  DMCA_FORM_URL,
  ReportReason,
} from "~/constants/content-report"

import type { AudioDetail, ImageDetail } from "~/types/media"

import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VRadio from "~/components/VRadio/VRadio.vue"
import VDmcaNotice from "~/components/VContentReport/VDmcaNotice.vue"
import VReportDescForm from "~/components/VContentReport/VReportDescForm.vue"
import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "VContentReportForm",
  components: {
    VButton,
    VIcon,
    VLink,
    VRadio,
    VDmcaNotice,
    VReportDescForm,
  },
  props: {
    media: {
      type: Object as PropType<AudioDetail | ImageDetail>,
      required: true,
    },
    providerName: {
      type: String as PropType<string>,
      required: true,
    },
    closeFn: {
      type: Function,
      required: true,
    },
    allowCancel: {
      type: Boolean,
      default: true,
    },
  },
  setup(props) {
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
    const handleSubmit = async (event: Event) => {
      event.preventDefault()
      if (selectedReason.value === DMCA) return
      // Submit report
      try {
        await ReportService.sendReport({
          mediaType: props.media.frontendMediaType,
          identifier: props.media.id,
          reason: selectedReason.value,
          description: description.value,
        })
        status.value = SENT
      } catch (error) {
        status.value = FAILED
      }
    }

    return {
      reasons,
      DMCA,
      OTHER,
      SENT,
      FAILED,
      DMCA_FORM_URL,

      selectedReason,
      status,
      description,

      handleCancel,

      isSubmitDisabled,
      handleSubmit,
    }
  },
})
</script>
