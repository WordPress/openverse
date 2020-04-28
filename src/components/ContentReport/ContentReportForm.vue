<template>
  <div class="card padding-normal is-clearfix report-form">
    <button class="button close-button is-text tiny is-shadowless is-pulled-right"
            @click="closeForm()">
      <i class="icon cross"></i>
    </button>
    <dmca-notice v-if="selectedCopyright && isReportSent"
                      :imageURL="imageURL"
                      :dmcaFormUrl="dmcaFormUrl" />
    <done-message v-else-if="!selectedCopyright && isReportSent" :imageURL="imageURL" />
    <report-error v-else-if="reportFailed"/>
    <form v-else-if="!selectedOther">
      <h4 class="b-header">Report this content</h4>
      <fieldset>
        <legend class="margin-bottom-small">What's the issue?</legend>

        <div>
          <input type="radio" name="type" id="dmca" value="dmca" v-model="selectedReason">
          <label for="dmca" class="margin-left-small">Infringes Copyright</label>
        </div>

        <div>
          <input type="radio" name="type" id="mature" value="mature" v-model="selectedReason">
          <label for="mature" class="margin-left-small">Contains mature content</label>
        </div>

        <div>
          <input type="radio" name="type" id="other" value="other" v-model="selectedReason">
          <label for="other" class="margin-left-small">Other</label>
        </div>

        <span class="caption has-text-weight-semibold has-text-grey">
          For security purposes, CC collects and retains anonymized IP
          addresses of those who complete and submit this form.
        </span>
      </fieldset>

      <button type="button"
              :disabled="selectedReason === null"
              class="button next-button tiny is-info margin-top-normal is-pulled-right"
              @click="onIssueSelected()">
        Next
      </button>
    </form>
    <form class="other-form" v-else-if="selectedOther">
      <legend class="margin-bottom-small">Please describe the issue for us</legend>
      <textarea class="reason"
                v-model="otherReasonDescription"
                placeholder="Issue description required" />
      <div>
        <button class="button other-back-button is-text tiny margin-top-normal is-shadowless"
                @click="onBackClick()">
          <span><i class="icon chevron-left margin-right-small"></i> Back</span>
        </button>

        <button type="button"
                :disabled="otherReasonDescription === ''"
                class="button submit-other-button tiny is-info margin-top-normal is-pulled-right"
                @click="sendContentReport()">
          Submit report
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { SEND_CONTENT_REPORT } from '@/store/action-types';
import { REPORT_FORM_CLOSED } from '@/store/mutation-types';
import dmcaNotice from './DmcaNotice';
import DoneMessage from './DoneMessage';
import ReportError from './ReportError';

const dmca_FORM_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSdZLZpYJGegL8G2FsEAHNsR1nqVx1Wxfp-oj3o0h8rqe9j8dg/viewform';

export default {
  name: 'content-report-form',
  props: ['imageId', 'imageURL'],
  components: {
    DoneMessage,
    dmcaNotice,
    ReportError,
  },
  data() {
    return {
      selectedReason: null,
      selectedOther: false,
      selectedCopyright: false,
      otherReasonDescription: '',
      dmcaFormUrl: dmca_FORM_URL,
    };
  },
  computed: {
    isReportSent() {
      return this.$store.state.isReportSent;
    },
    reportFailed() {
      return this.$store.state.reportFailed;
    },
  },
  methods: {
    onIssueSelected() {
      if (this.selectedReason === 'other') {
        this.selectedOther = true;
      }
      else {
        this.selectedCopyright = this.selectedReason === 'dmca';
        this.sendContentReport();
      }
    },
    onBackClick() {
      this.selectedOther = false;
    },
    sendContentReport() {
      this.$store.dispatch(SEND_CONTENT_REPORT, {
        identifier: this.$props.imageId,
        reason: this.selectedReason,
        description: this.otherReasonDescription,
      });
    },
    closeForm() {
      this.$store.commit(REPORT_FORM_CLOSED);
    },
  },
};
</script>

<style lang="scss" scoped>
.card {
  width: 22rem;
}
.reason {
  width: 100%;
  height: 6rem;
}
</style>
