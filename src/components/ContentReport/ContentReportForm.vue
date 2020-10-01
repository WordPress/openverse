<template>
  <div id="content-report-form" class="padding-normal is-clearfix arrow-popup">
    <button
      :aria-label="$t('photo-details.aria.close-form')"
      class="button close-button is-text tiny is-pulled-right is-block has-background-white"
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
      <h5 class="b-header margin-bottom-normal">
        {{ $t('photo-details.content-report.title') }}
      </h5>
      <fieldset class="margin-bottom-normal">
        <legend class="margin-bottom-normal">
          {{ $t('photo-details.content-report.issue') }}
        </legend>

        <div>
          <label for="dmca" class="margin-left-small">
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
          <label for="mature" class="margin-left-small">
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
          <label for="other" class="margin-left-small">
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

      <p
        class="caption has-text-weight-semibold has-text-grey margin-bottom-normal"
      >
        {{ $t('photo-details.content-report.caption') }}
      </p>

      <button
        type="button"
        :disabled="selectedReason === null"
        class="button next-button tiny is-success is-pulled-right"
        @click="onIssueSelected()"
        @keyup.enter="onIssueSelected()"
      >
        {{ $t('photo-details.content-report.next') }}
      </button>
    </form>
  </div>
</template>

<script>
import getProviderName from '~/utils/getProviderName'
import dmcaNotice from './DmcaNotice'
import OtherIssueForm from './OtherIssueForm'
import DoneMessage from './DoneMessage'
import ReportError from './ReportError'
import { SEND_CONTENT_REPORT } from '~/store-modules/action-types'
import { REPORT_FORM_CLOSED } from '~/store-modules/mutation-types'

const dmcaFormUrl =
  'https://docs.google.com/forms/d/e/1FAIpQLSdZLZpYJGegL8G2FsEAHNsR1nqVx1Wxfp-oj3o0h8rqe9j8dg/viewform'

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
      return this.$store.state.isReportSent
    },
    reportFailed() {
      return this.$store.state.reportFailed
    },
    providerName() {
      return getProviderName(
        this.$store.state.imageProviders,
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
        this.sendContentReport()
      }
    },
    onBackClick() {
      this.selectedOther = false
      this.selectedCopyright = false
    },
    sendContentReport(description = '') {
      this.$store.dispatch(SEND_CONTENT_REPORT, {
        identifier: this.$props.image.id,
        reason: this.selectedReason,
        description,
      })
    },
    closeForm() {
      this.$store.commit(REPORT_FORM_CLOSED)
    },
  },
}
</script>
