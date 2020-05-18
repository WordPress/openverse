<template>
  <div class="padding-normal is-clearfix report-form">
    <button class="button close-button is-text tiny is-pulled-right is-block has-text-grey-light"
            @click="closeForm()">
      <i class="icon cross"></i>
    </button>
    <dmca-notice v-if="selectedCopyright"
                      :imageURL="imageURL"
                      :providerName="providerName"
                      :dmcaFormUrl="dmcaFormUrl"
                      @onBackClick="onBackClick()"/>
    <done-message v-else-if="!selectedCopyright && isReportSent"
                  :imageURL="imageURL"
                  :providerName="providerName" />
    <report-error v-else-if="reportFailed"/>
    <other-issue-form v-else-if="selectedOther"
                      @onBackClick="onBackClick()"
                      @sendContentReport="sendContentReport" />
    <form v-else>
      <h4 class="b-header">Report this content</h4>
      <fieldset class="margin-bottom-normal">
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
      </fieldset>

      <span class="caption has-text-weight-semibold has-text-grey">
        For security purposes, CC collects and retains anonymized IP
        addresses of those who complete and submit this form.
      </span>

      <button type="button"
              :disabled="selectedReason === null"
              class="button next-button tiny is-info margin-top-normal is-pulled-right"
              @click="onIssueSelected()">
        Next
      </button>
    </form>
  </div>
</template>

<script>
import { SEND_CONTENT_REPORT } from '@/store/action-types';
import { REPORT_FORM_CLOSED } from '@/store/mutation-types';
import dmcaNotice from './DmcaNotice';
import OtherIssueForm from './OtherIssueForm';
import DoneMessage from './DoneMessage';
import ReportError from './ReportError';

const dmcaFormUrl = 'https://docs.google.com/forms/d/e/1FAIpQLSdZLZpYJGegL8G2FsEAHNsR1nqVx1Wxfp-oj3o0h8rqe9j8dg/viewform';

export default {
  name: 'content-report-form',
  props: ['imageId', 'imageURL', 'providerName'],
  components: {
    DoneMessage,
    dmcaNotice,
    ReportError,
    OtherIssueForm,
  },
  data() {
    return {
      selectedReason: null,
      selectedOther: false,
      selectedCopyright: false,
      dmcaFormUrl,
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
      else if (this.selectedReason === 'dmca') {
        this.selectedCopyright = true;
      }
      else {
        this.sendContentReport();
      }
    },
    onBackClick() {
      this.selectedOther = false;
      this.selectedCopyright = false;
    },
    sendContentReport(description = '') {
      this.$store.dispatch(SEND_CONTENT_REPORT, {
        identifier: this.$props.imageId,
        reason: this.selectedReason,
        description,
      });
    },
    closeForm() {
      this.$store.commit(REPORT_FORM_CLOSED);
    },
  },
};
</script>


