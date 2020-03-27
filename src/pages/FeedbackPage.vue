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
      <div class="column">
        <section class="tabs margin-top-big">
          <ul>
            <li :class="tabClass(0, 'a')">
              <a href="#panel0" :aria-selected="activeTab == 0" @click.prevent="setActiveTab(0)">
                Help us Improve
              </a>
            </li>
            <li :class="tabClass(1, 'a')">
              <a href="#panel1" :aria-selected="activeTab == 1" @click.prevent="setActiveTab(1)">
                Report a Bug
              </a>
            </li>
          </ul>
        </section>
        <section class="tabs-content">
          <div :class="tabClass(0, 'tabs-panel')">
            <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSfb_6yq2Md0v6S-XzsyT7p1QVhqr7MWHqInKdyYh4ReaWn4FQ/viewform?embedded=true"
                    width="100%"
                    height="998"
                    frameborder="0"
                    marginheight="0"
                    marginwidth="0"
                    title="feedback form">
              Loading...
            </iframe>
          </div>
          <div :class="tabClass(1, 'tabs-panel')">
            <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSeSN1AIG8LrdgIdKpBj4IlPDhu6T5ndZ7z_QcISBu-ITCU0Yw/viewform?embedded=true"
                    width="100%"
                    height="998"
                    frameborder="0"
                    marginheight="0"
                    marginwidth="0"
                    title="feedback form">
              Loading...
            </iframe>
          </div>
        </section>
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
  data() {
    return {
      activeTab: 0,
    };
  },
  methods: {
    tabClass(tabIdx, tabClass) {
      return {
        [tabClass]: true,
        'is-active': tabIdx === this.activeTab,
      };
    },
    setActiveTab(tabIdx) {
      this.activeTab = tabIdx;
    },
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

