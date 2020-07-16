<template>
  <div>
    <h1>Report a bug</h1>
    <p>
      If you would like to report a bug you are encountering when using the
      tool, please fill out the form below or
      <a href="https://github.com/creativecommons/cccatalog-frontend/issues">
        log the issue directly at Github </a
      >.
    </p>
    <vue-form class="bug-report" :state="formstate" @submit.prevent="onSubmit">
      <validate tag="label">
        <label for="name">Name</label>
        <input id="name" v-model="model.name" required name="name" />

        <field-messages name="name" show="$submitted && !$focused">
          <div class="error-message" slot="required">
            Name is a required field
          </div>
        </field-messages>
      </validate>

      <validate tag="label">
        <label for="email">Email</label>
        <input
          id="email"
          v-model="model.email"
          name="email"
          type="email"
          required
        />

        <field-messages name="email" show="$submitted && !$focused">
          <div class="error-message" slot="required">
            Email is a required field
          </div>
          <div class="error-message" slot="email">Email is not valid</div>
        </field-messages>
      </validate>

      <validate tag="label">
        <label for="bugReport">
          What is the bug and how did you encounter it? Please describe what
          steps you took, and what you expected to happen instead
        </label>
        <textarea
          id="bugReport"
          v-model="model.bugReport"
          name="bugReport"
          required
        />

        <field-messages name="bugReport" show="$submitted && !$focused">
          <div class="error-message" slot="required">
            This is a required field
          </div>
        </field-messages>
      </validate>

      <span v-if="bugReported">Thank you!</span>
      <button
        v-else
        class="button submit-form"
        type="submit"
        :disabled="isReportingBug"
      >
        Submit
      </button>

      <div class="error-message bug-report-failed" v-if="bugReportFailed">
        There was an error while reporting your bug. Please try again.
      </div>
    </vue-form>
  </div>
</template>

<script>
import VueForm from 'vue-form'
import { REPORT_BUG } from '@/store/action-types'
import getBrowserInfo from '@/utils/getBrowserInfo'

export default {
  name: 'bug-report',
  mixins: [VueForm],
  props: ['isReportingBug', 'bugReported', 'bugReportFailed'],
  data: () => ({
    formstate: {},
    model: {
      name: '',
      email: '',
      bugReport: '',
    },
  }),
  methods: {
    onSubmit() {
      if (!this.formstate.$invalid) {
        const bugReportData = {
          name: this.model.name,
          email: this.model.email,
          bug_description: this.model.bugReport,
          browser_info: getBrowserInfo(),
        }
        this.$store.dispatch(REPORT_BUG, bugReportData)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
input {
  display: block;
  box-sizing: border-box;
  width: 40rem;
  height: 2.4375rem;
  margin: 0 0 0.4rem;
  padding: 0.5rem;
  border: 1px solid #cacaca;
  border-radius: 0;
  background-color: #fefefe;
  box-shadow: inset 0 1px 2px rgba(10, 10, 10, 0.1);
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5;
  color: #0a0a0a;
  transition: border-color 0.25s ease-in-out, -webkit-box-shadow 0.5s;
}

textarea {
  height: 10rem;
  width: 40rem;
  margin: 0 0 0.4rem;
}

button {
  border-radius: 3px;
  background: #4a69ca;
}

.error-message {
  width: 40rem;
  font-style: italic;
  color: #ff0e0e;
  margin: 0 0 0.4rem;
}
</style>
