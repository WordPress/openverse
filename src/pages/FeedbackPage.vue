<template>
  <div class="grid-container full">
    <header-section showNavSearch="true"></header-section>
    <div class="feedback-page">
      <h1 id="feedback">Feedback</h1>
      <p>
        Thank you for using CC Search! We welcome your ideas for improving the tool below.
        To provide regular user feedback, join the
        <a href="https://creativecommons.slack.com/messages/CCS9CF2JE/details/">#cc-usability</a> channel on
        <a href="https://wiki.creativecommons.org/wiki/Slack#How_to_join_Slack">CC Slack</a>.
      </p>
      <p>
        To give Feedback, <a href="https://docs.google.com/forms/d/e/1FAIpQLSfb_6yq2Md0v6S-XzsyT7p1QVhqr7MWHqInKdyYh4ReaWn4FQ/viewform?embedded=true" target="_blank">click here</a>.
      </p>

      <div>
        <h2><a id="report"></a>Report a bug</h2>
        <p>
          If you would like to report a bug you are encountering when using the tool, please email
          <a href="mailto:support-search@creativecommons.org">
            support-search@creativecommons.org
          </a>
          or
          <a href="https://github.com/creativecommons/cccatalog-frontend/issues">
            log the issue directly at Github
          </a>.
        </p>
      </div>
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';

export default {
  name: 'feedback-page',
  components: {
    HeaderSection,
    FooterSection,
  },
  computed: {
    isReportingBug() {
      return this.$store.state.isReportingBug;
    },
    bugReported() {
      return this.$store.state.bugReported;
    },
    bugReportFailed() {
      return this.$store.state.bugReportFailed;
    },
  },
};
</script>

<style lang="scss" scoped>
  h1, h2 {
    margin-bottom: .44117647em;
    font-size: 2.125em;
    font-weight: normal;
    letter-spacing: initial;
    line-height: 1.25;
    text-transform: initial;
  }

  .feedback-page {
    margin: 45px !important;
  }
</style>
