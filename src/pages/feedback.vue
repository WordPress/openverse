<template>
  <div class="section">
    <div class="container is-fluid">
      <div class="padding-bottom-big">
        <h1 id="feedback" class="title is-2">
          {{ $t('feedback.title') }}
        </h1>
        <i18n
          path="feedback.description.content"
          tag="p"
          class="margin-bottom-large"
        >
          <template #openverse>
            <a
              href="https://wordpress.slack.com/messages/openverse/"
              target="_blank"
            >
              {{ $t('feedback.description.openverse') }}</a
            >
          </template>
          <template #making-wordpress>
            <a href="https://make.wordpress.org/chat/" target="_blank">
              {{ $t('feedback.description.making-wordpress') }}</a
            >
          </template>
        </i18n>
        <section class="tabs margin-top-big">
          <div role="tablist" :aria-label="$t('feedback.title')">
            <button
              id="improve"
              role="tab"
              :aria-selected="activeTab == 0"
              aria-controls="tab-improve"
              :class="tabClass(0, 'tab')"
              @click.prevent="setActiveTab(0)"
              @keyup.enter.prevent="setActiveTab(0)"
            >
              {{ $t('feedback.improve') }}
            </button>
            <button
              id="report"
              role="tab"
              :aria-selected="activeTab == 1"
              aria-controls="tab-report"
              :class="tabClass(1, 'tab')"
              @click.prevent="setActiveTab(1)"
              @keyup.enter.prevent="setActiveTab(1)"
            >
              {{ $t('feedback.bug') }}
            </button>
          </div>
          <div
            id="tab-improve"
            aria-labelledby="improve"
            role="tabpanel"
            :class="tabClass(0, 'tabs-panel')"
            tabindex="0"
          >
            <iframe
              :aria-label="$t('feedback.aria.improve')"
              :src="suggestionForm"
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
          <div
            id="tab-report"
            aria-labelledby="report"
            role="tabpanel"
            :class="tabClass(1, 'tabs-panel')"
            tabindex="0"
          >
            <iframe
              :aria-label="$t('feedback.aria.report-bug')"
              :src="bugForm"
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
const bugForm =
  'https://docs.google.com/forms/d/e/1FAIpQLSenCn-3HoZlCz4vlL2621wjezfu1sPZDaWGe_FtQ1R5-5qR4Q/viewform'
const suggestionForm =
  'https://docs.google.com/forms/d/e/1FAIpQLSfGC7JWbNjGs-_pUNe3B2nzBW-YrIrmRd92t-7u0y7s8jMjzQ/viewform'

export const FeedbackPage = {
  name: 'feedback-page',
  layout: 'with-nav-search',
  data() {
    return {
      activeTab: 0,
      bugForm: `${bugForm}?embedded=true`,
      suggestionForm: `${suggestionForm}?embedded=true`,
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
