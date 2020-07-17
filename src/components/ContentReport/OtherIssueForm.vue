<template>
  <form class="other-form">
    <h4 class="b-header">Report this content</h4>
    <legend class="margin-bottom-small">
      Please describe the issue for us
    </legend>
    <textarea
      class="reason padding-small has-text-weight-semibold"
      v-model="otherReasonDescription"
      placeholder="Issue description required (with at least 20 characters)"
    />
    <div>
      <button
        class="button other-back-button is-text tiny margin-top-normal has-text-grey"
        @click="onBackClick()"
      >
        <span><i class="icon chevron-left margin-right-small"></i> Back</span>
      </button>

      <button
        type="button"
        :disabled="!descriptionHasMoreThan20Chars"
        class="button submit-other-button tiny is-info margin-top-normal is-pulled-right"
        @click="sendContentReport()"
      >
        Submit
      </button>
    </div>
  </form>
</template>

<script>
export default {
  name: 'other-issue-form',
  data() {
    return {
      otherReasonDescription: '',
    }
  },
  computed: {
    descriptionHasMoreThan20Chars() {
      return this.otherReasonDescription.length >= 20
    },
  },
  methods: {
    onBackClick() {
      this.$emit('onBackClick')
    },
    sendContentReport() {
      this.$emit('sendContentReport', this.otherReasonDescription)
    },
  },
}
</script>

<style lang="scss" scoped>
.reason {
  width: 100%;
  height: 6rem;
  font-size: 13px;
  font-family: Source Sans Pro;
}
</style>
