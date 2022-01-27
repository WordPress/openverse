<template>
  <div id="content-report-form" class="p-4">
    <button
      :aria-label="$t('photo-details.aria.close-form')"
      class="button close-button is-text tiny float-right block bg-white"
      type="button"
      @click="closeForm"
    >
      <VIcon :icon-path="closeIcon" />
    </button>
    <VDmcaNotice
      v-if="showDmcaForm"
      :image-url="image.foreign_landing_url"
      :provider="providerName"
      :dmca-form-url="dmcaFormUrl"
      @back-click="onBackClick"
    />
    <VDoneMessage
      v-else-if="isDone"
      :image-url="image.foreign_landing_url"
      :provider="providerName"
    />
    <VReportError v-else-if="reportFailed" @back-click="backToReportStart" />

    <VOtherIssueForm
      v-else-if="showOtherForm"
      @back-click="onBackClick"
      @send-report="sendContentReport"
    />
    <form v-else>
      <h5 class="b-header mb-4">
        {{ $t('photo-details.content-report.title') }}
      </h5>
      <fieldset class="mb-4 flex flex-col">
        <legend class="mb-4">
          {{ $t('photo-details.content-report.issue') }}
        </legend>
        <label
          v-for="reason in reasons"
          :key="reason"
          :for="reason"
          class="ms-2 mb-2"
        >
          <input
            :id="reason"
            v-model="reasonSelected"
            type="radio"
            name="type"
            :value="reason"
          />
          {{ $t(`photo-details.content-report.reasons.${reason}`) }}
        </label>
      </fieldset>

      <p class="caption font-semibold text-gray mb-4">
        {{ $t('photo-details.content-report.caption') }}
      </p>

      <VButton
        :disabled="!reasonSelected"
        variant="secondary"
        class="float-end bg-trans-blue"
        @click="onIssueSelected"
      >
        {{ $t('photo-details.content-report.next') }}
      </VButton>
    </form>
  </div>
</template>

<script>
import { computed, defineComponent, ref } from '@nuxtjs/composition-api'
import VDmcaNotice from './VDmcaNotice'
import VOtherIssueForm from './VOtherIssueForm'
import VDoneMessage from './VDoneMessage'
import VReportError from './VReportError'
import ReportService from '~/data/report-service'

import closeIcon from '~/assets/icons/close.svg'
import VIcon from '~/components/VIcon/VIcon.vue'
import VButton from '~/components/VButton.vue'

const dmcaFormUrl =
  'https://docs.google.com/forms/d/e/1FAIpQLSd0I8GsEbGQLdaX4K_F6V2NbHZqN137WMZgnptUpzwd-kbDKA/viewform'
const reasons = {
  DMCA: 'dmca',
  MATURE: 'mature',
  OTHER: 'other',
}
const statuses = {
  SENT: 'sent',
  FAILED: 'failed',
  ADDING_DETAILS: 'adding_details',
  OPEN: 'open',
  CLOSED: 'closed',
}

export default defineComponent({
  name: 'VContentReportForm',
  components: {
    VDoneMessage,
    VDmcaNotice,
    VReportError,
    VOtherIssueForm,
    VButton,
    VIcon,
  },
  props: ['image', 'providerName', 'reportService'],
  setup(props, { emit }) {
    const reportStatus = ref(statuses.OPEN)
    /** @type {import('@nuxtjs/composition-api').Ref<string|null>} */
    const reasonSelected = ref(null)

    const service = props.reportService || ReportService
    const onIssueSelected = () => {
      if (
        reasonSelected.value &&
        ![reasons.OTHER, reasons.DMCA].includes(reasonSelected.value)
      ) {
        sendContentReport()
      } else {
        reportStatus.value = statuses.ADDING_DETAILS
      }
    }
    const onBackClick = () => {
      reportStatus.value = statuses.OPEN
    }
    const backToReportStart = () => {
      reasonSelected.value = null
      reportStatus.value = statuses.OPEN
    }
    const sendContentReport = async ({ description = '' } = {}) => {
      try {
        await service.sendReport({
          identifier: props.image.id,
          reason: reasonSelected.value,
          description,
        })
        reportStatus.value = statuses.SENT
      } catch (error) {
        reportStatus.value = statuses.FAILED
      }
    }
    const closeForm = () => {
      reportStatus.value = statuses.CLOSED
      emit('close-form')
    }
    const reportFailed = computed(() => reportStatus.value === statuses.FAILED)
    const isDone = computed(
      () =>
        reportStatus.value === statuses.SENT &&
        !(reasonSelected.value === reasons.DMCA)
    )
    const showOtherForm = computed(
      () =>
        reportStatus.value === statuses.ADDING_DETAILS &&
        reasonSelected.value === reasons.OTHER
    )
    const showDmcaForm = computed(
      () =>
        reportStatus.value === statuses.ADDING_DETAILS &&
        reasonSelected.value === reasons.DMCA
    )
    return {
      reasonSelected,
      closeIcon,
      dmcaFormUrl,
      isDone,
      reportFailed,
      closeForm,
      onIssueSelected,
      onBackClick,
      sendContentReport,
      backToReportStart,
      showOtherForm,
      showDmcaForm,
      reasons: Object.values(reasons),
    }
  },
})
</script>
