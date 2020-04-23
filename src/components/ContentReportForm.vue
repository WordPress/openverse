<template>
  <div class="card padding-normal is-clearfix">
    <copyright-notice v-if="selectedCopyright"
                      :imageURL="imageURL"
                      :dcmaFormUrl="dcmaFormUrl" />
    <form v-else-if="!selectedOther">
      <h4 class="b-header">Report this content</h4>
      <fieldset>
        <legend class="margin-bottom-small">What's the issue?</legend>

        <div>
          <input type="radio" name="type" id="copyright" value="copyright" v-model="selectedReason">
          <label for="copyright" class="margin-left-small">Infringes copyright</label>
        </div>

        <div>
          <input type="radio" name="type" id="adult" value="adult" v-model="selectedReason">
          <label for="adult" class="margin-left-small">Contains adult content</label>
        </div>

        <div>
          <input type="radio" name="type" id="other" value="other" v-model="selectedReason">
          <label for="other" class="margin-left-small">Other</label>
        </div>

        <span class="caption has-text-weight-semibold has-text-grey">For security purposes, CC collects and retains anonymized IP addresses of those who complete and submit this form.</span>
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
import Vue from 'vue';
import { SEND_CONTENT_REPORT } from '@/store/action-types';

const DCMA_FORM_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSdZLZpYJGegL8G2FsEAHNsR1nqVx1Wxfp-oj3o0h8rqe9j8dg/viewform';

const CopyrightNotice = Vue.component('copyright-notice', {
  props: ['dcmaFormUrl', 'imageURL'],
  template: `<div>
    <span class="is-block">Please fill out <a href={{ this.DCMA_FORM_URL }} target="_blank" rel="noopener">this DMCA form</a> to report copyright infringement.</span>
    <span>We recommend doing the same <a href={{ this.imageURL }} target="_blank" rel="noopener">at the source</a>.</span>
  </div>`,
});

const DoneMessage = Vue.component('done-message', {
  props: ['imageURL'],
  template: `<div>
    <span class="is-block">Thank you for reporting an issue with the results of CC Search!</span>
    <span>We recommend doing the same <a href={{ this.imageURL }} target="_blank" rel="noopener">at the source</a>.</span>
  </div>`,
});

export default {
  name: 'content-report-form',
  props: ['imageId', 'imageURL'],
  components: {
    CopyrightNotice,
    DoneMessage,
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

  },
  methods: {
    onIssueSelected() {
      if (this.selectedReason === 'copyright') {
        this.selectedCopyright = true;
      }
      if (this.selectedReason === 'other') {
        this.selectedOther = true;
      }
      else {
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
