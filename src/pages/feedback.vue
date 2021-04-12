<template>
  <div class="section">
    <div class="container is-fluid">
      <div class="padding-bottom-big">
        <h1 id="feedback" class="title is-2">
          {{ $t('feedback.title') }}
        </h1>
        <i18n path="feedback.description" tag="p" class="margin-bottom-large">
          <template #channel>
            <a
              :aria-label="$t('feedback.aria.cc-usability')"
              href="https://creativecommons.slack.com/messages/CCS9CF2JE/details/"
              >#cc-usability</a
            >
          </template>
          <template #slack>
            <a
              aria-label="cc slack"
              href="https://wiki.creativecommons.org/wiki/Slack#How_to_join_Slack"
              >CC Slack</a
            >
          </template>
        </i18n>
        <section class="tabs margin-top-big">
          <ul role="tablist">
            <li
              role="tab"
              :aria-selected="activeTab == 0"
              :class="tabClass(0, 'tab')"
            >
              <a
                :aria-label="$t('feedback.aria.improve')"
                href="#panel0"
                @click.prevent="setActiveTab(0)"
                @keyup.enter.prevent="setActiveTab(0)"
              >
                {{ $t('feedback.improve') }}
              </a>
            </li>
            <li
              role="tab"
              :aria-selected="activeTab == 1"
              :class="tabClass(1, 'tab')"
            >
              <a
                :aria-label="$t('feedback.aria.report-bug')"
                href="#panel1"
                @click.prevent="setActiveTab(1)"
                @keyup.enter.prevent="setActiveTab(1)"
              >
                {{ $t('feedback.bug') }}
              </a>
            </li>
          </ul>
        </section>
        <section class="tabs-content">
          <div :class="tabClass(0, 'tabs-panel')">
            <iframe
              :aria-label="$t('feedback.aria.improve')"
              src="https://docs.google.com/forms/d/e/1FAIpQLSfb_6yq2Md0v6S-XzsyT7p1QVhqr7MWHqInKdyYh4ReaWn4FQ/viewform?embedded=true"
              width="100%"
              height="1200"
              frameborder="0"
              marginheight="0"
              marginwidth="0"
              title="feedback form"
            >
              {{ $t('feedback.loading') }}
            </iframe>
          </div>
          <div :class="tabClass(1, 'tabs-panel')">
            <iframe
              :aria-label="$t('feedback.aria.report-bug')"
              src="https://docs.google.com/forms/d/e/1FAIpQLSeSN1AIG8LrdgIdKpBj4IlPDhu6T5ndZ7z_QcISBu-ITCU0Yw/viewform?embedded=true"
              width="100%"
              height="1600"
              frameborder="0"
              marginheight="0"
              marginwidth="0"
              title="feedback form"
            >
              {{ $t('feedback.loading') }}
            </iframe>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
export const FeedbackPage = {
  name: 'feedback-page',
  layout: 'with-nav-search',
  data() {
    return {
      activeTab: 0,
    }
  },
  methods: {
    tabClass(tabIdx, tabClass) {
      return {
        [tabClass]: true,
        'is-active': tabIdx === this.activeTab,
      }
    },
    setActiveTab(tabIdx) {
      this.activeTab = tabIdx
    },
  },
  computed: {
    isReportingBug() {
      return this.$store.state.isReportingBug
    },
    bugReported() {
      return this.$store.state.bugReported
    },
    bugReportFailed() {
      return this.$store.state.bugReportFailed
    },
  },
}

export default FeedbackPage
</script>
