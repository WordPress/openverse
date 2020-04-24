<template>
  <div class="card padding-normal is-clearfix">
    <dcma-notice v-if="selectedCopyright && isReportSent"
                      :imageURL="imageURL"
                      :dcmaFormUrl="dcmaFormUrl" />
    <done-message v-else-if="!selectedCopyright && isReportSent" :imageURL="imageURL" />
    <form v-else-if="!selectedOther">
      <h4 class="b-header">Report this content</h4>
      <fieldset>
        <legend class="margin-bottom-small">What's the issue?</legend>

        <div>
          <input type="radio" name="type" id="dcma" value="dcma" v-model="selectedReason">
          <label for="dcma" class="margin-left-small">Infringes Copyright</label>
        </div>

        <div>
          <input type="radio" name="type" id="adult" value="adult" v-model="selectedReason">
          <label for="adult" class="margin-left-small">Contains adult content</label>
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
              class="button tiny is-info is-block margin-top-normal is-pulled-right"
              @click="onIssueSelected()">
        Next
      </button>
    </form>
    <form v-else-if="selectedOther">
      <legend class="margin-bottom-small">Please describe the issue for us</legend>
      <textarea class="reason"
                v-model="otherReasonDescription"
                placeholder="Issue description required" />
      <div>
        <button class="button is-text tiny padding-top-normal is-shadowless"
                @click="onBackClick()">
          <i class="icon chevron-left margin-right-small"></i> Back
        </button>

        <button type="button"
                class="button tiny is-info is-block margin-top-normal is-pulled-right"
                @click="sendContentReport()">
          Submit report
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { SEND_CONTENT_REPORT } from '@/store/action-types';
import DcmaNotice from './DcmaNotice';
import DoneMessage from './DoneMessage';

const DCMA_FORM_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSdZLZpYJGegL8G2FsEAHNsR1nqVx1Wxfp-oj3o0h8rqe9j8dg/viewform';

export default {
  name: 'content-report-form',
  props: ['imageId', 'imageURL'],
  components: {
    DoneMessage,
    DcmaNotice,
  },
  data() {
    return {
      selectedReason: null,
      selectedOther: false,
      selectedCopyright: false,
      otherReasonDescription: '',
      dcmaFormUrl: DCMA_FORM_URL,
    };
  },
  computed: {
    isReportSent() {
      return this.$store.state.isReportSent;
    },
  },
  methods: {
    onIssueSelected() {
      if (this.selectedReason === 'other') {
        this.selectedOther = true;
      }
      else {
        this.selectedCopyright = this.selectedReason === 'dcma';
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
