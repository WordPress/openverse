<template>
  <div id="content-report-form" class="p-4 arrow-popup">
    <button
      :aria-label="$t('photo-details.aria.close-form')"
      class="button close-button is-text tiny float-right block bg-white"
      @click="closeForm()"
      @keyup.enter="closeForm()"
    >
      <i class="icon cross" />
    </button>
    <DmcaNotice
      v-if="selectedCopyright"
      :image-u-r-l="image.url"
      :provider-name="providerName"
      :dmca-form-url="dmcaFormUrl"
      @onBackClick="onBackClick()"
    />
    <DoneMessage
      v-else-if="!selectedCopyright && isReportSent"
      :image-u-r-l="image.url"
      :provider-name="providerName"
    />
    <ReportError v-else-if="reportFailed" />

    <OtherIssueForm
      v-else-if="selectedOther"
      @onBackClick="onBackClick()"
      @sendContentReport="sendContentReport"
    />
    <form v-else>
      <h5 class="b-header mb-4">
        {{ $t('photo-details.content-report.title') }}
      </h5>
      <fieldset class="mb-4">
        <legend class="mb-4">
          {{ $t('photo-details.content-report.issue') }}
        </legend>

        <div>
          <label for="dmca" class="ml-2">
            <input
              id="dmca"
              v-model="selectedReason"
              type="radio"
              name="type"
              value="dmca"
            />
            {{ $t('photo-details.content-report.copyright') }}
          </label>
        </div>

        <div>
          <label for="mature" class="ml-2">
            <input
              id="mature"
              v-model="selectedReason"
              type="radio"
              name="type"
              value="mature"
            />
            {{ $t('photo-details.content-report.mature') }}
          </label>
        </div>

        <div>
          <label for="other" class="ml-2">
            <input
              id="other"
              v-model="selectedReason"
              type="radio"
              name="type"
              value="other"
            />
            {{ $t('photo-details.content-report.other') }}
          </label>
        </div>
      </fieldset>

      <p class="caption font-semibold text-gray mb-4">
        {{ $t('photo-details.content-report.caption') }}
      </p>

      <button
        type="button"
        :disabled="selectedReason === null"
        class="button next-button tiny is-success float-right"
        @click="onIssueSelected()"
        @keyup.enter="onIssueSelected()"
      >
        {{ $t('photo-details.content-report.next') }}
      </button>
    </form>
  </div>
</template>

<script>
import getProviderName from '~/utils/get-provider-name'
import dmcaNotice from './DmcaNotice'
import OtherIssueForm from './OtherIssueForm'
import DoneMessage from './DoneMessage'
import ReportError from './ReportError'
import { SEND_CONTENT_REPORT } from '~/constants/action-types'
import { REPORT_FORM_CLOSED } from '~/constants/mutation-types'
import { PROVIDER, REPORT_CONTENT } from '~/constants/store-modules'

const dmcaFormUrl =
  'https://docs.google.com/forms/d/e/1FAIpQLSd0I8GsEbGQLdaX4K_F6V2NbHZqN137WMZgnptUpzwd-kbDKA/viewform'

export default {
  name: 'ContentReportForm',
  components: {
    DoneMessage,
    dmcaNotice,
    ReportError,
    OtherIssueForm,
  },
  props: ['image'],
  data() {
    return {
      selectedReason: null,
      selectedOther: false,
      selectedCopyright: false,
      dmcaFormUrl,
    }
  },
  computed: {
    isReportSent() {
      return this.$store.state[REPORT_CONTENT].isReportSent
    },
    reportFailed() {
      return this.$store.state[REPORT_CONTENT].reportFailed
    },
    providerName() {
      return getProviderName(
        this.$store.state[PROVIDER].imageProviders,
        this.image.provider
      )
    },
  },
  methods: {
    onIssueSelected() {
      if (this.selectedReason === 'other') {
        this.selectedOther = true
      } else if (this.selectedReason === 'dmca') {
        this.selectedCopyright = true
      } else {
        console.log('sending content report')
        this.sendContentReport()
      }
    },
    onBackClick() {
      this.selectedOther = false
      this.selectedCopyright = false
    },
    sendContentReport(description = '') {
      this.$store.dispatch(`${REPORT_CONTENT}/${SEND_CONTENT_REPORT}`, {
        identifier: this.$props.image.id,
        reason: this.selectedReason,
        description,
      })
    },
    closeForm() {
      this.$store.commit(`${REPORT_CONTENT}/${REPORT_FORM_CLOSED}`)
    },
  },
}
</script>
