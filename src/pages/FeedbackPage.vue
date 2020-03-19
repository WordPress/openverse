<template>
  <div class="feedback-page">
    <header-section showNavSearch="true"></header-section>
    <div class="margin-larger">
      <h1 id="feedback">Feedback</h1>
      <p>
        Thank you for using CC Search! We welcome your ideas for improving the tool below.
        To provide regular user feedback, join the
        <a href="https://creativecommons.slack.com/messages/CCS9CF2JE/details/">#cc-usability</a> channel on
        <a href="https://wiki.creativecommons.org/wiki/Slack#How_to_join_Slack">CC Slack</a>.
      </p>
      <p>
        To report a bug, <a href="#report">click here</a>.
      </p>

      <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSfb_6yq2Md0v6S-XzsyT7p1QVhqr7MWHqInKdyYh4ReaWn4FQ/viewform?embedded=true"
              width="100%"
              height="998"
              frameborder="0"
              marginheight="0"
              marginwidth="0"
              title="feedback form">
              Loading...
      </iframe>

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
