<template>
  <div class="card padding-normal is-clearfix">
    <h4 class="b-header">Report this content</h4>

    <form v-if="!selectedOther">
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
      </fieldset>

      <button type="button"
              class="button tiny is-info is-block margin-top-normal is-pulled-right"
              @click="onIssueSelected()">
        Next
      </button>
    </form>
    <form v-else>
      <legend class="margin-bottom-small">Please describe the issue for us</legend>

      <textarea class="reason" v-model="otherReasonDescription" placeholder="Issue description required" />

      <div>
        <button class="button is-text tiny padding-top-normal is-shadowless"
                @click="onBackClick()">
          <img alt="back" class="back margin-right-small" src="@/assets/back_arrow.svg" />
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

export default {
  name: 'content-report-form',
  props: ['imageId'],
  data() {
    return {
      selectedReason: null,
      selectedOther: false,
      otherReasonDescription: '',
    };
  },
  methods: {
    onIssueSelected() {
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
