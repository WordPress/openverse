<template>
  <div class="feedback-page">
    <header-section showNavSearch="true"></header-section>
    <main role="main" class="margin-larger">
      <h1 id="feedback">{{ $t('feedback.title') }}</h1>
      <i18n path="feedback.description" tag="p">
        <template v-slot:channel>
          <a
            aria-label="slack cc-usability channel"
            href="https://creativecommons.slack.com/messages/CCS9CF2JE/details/"
            >#cc-usability</a
          >
        </template>
        <template v-slot:slack>
          <a
            href="https://wiki.creativecommons.org/wiki/Slack#How_to_join_Slack"
            >CC Slack</a
          >
        </template>
      </i18n>
      <div class="column">
        <section class="tabs margin-top-big">
          <ul role="tablist">
            <li
              role="tab"
              :aria-selected="activeTab == 0"
              :class="tabClass(0, 'tab')"
            >
              <a
                aria-label="help us improve form"
                href="#panel0"
                @click.prevent="setActiveTab(0)"
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
                aria-label="report a bug form"
                href="#panel1"
                @click.prevent="setActiveTab(1)"
              >
                {{ $t('feedback.bug') }}
              </a>
            </li>
          </ul>
        </section>
        <section class="tabs-content">
          <div :class="tabClass(0, 'tabs-panel')">
            <iframe
              aria-label="help us improve form"
              src="https://docs.google.com/forms/d/e/1FAIpQLSfb_6yq2Md0v6S-XzsyT7p1QVhqr7MWHqInKdyYh4ReaWn4FQ/viewform?embedded=true"
              width="100%"
              height="998"
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
              aria-label="report a bug form"
              src="https://docs.google.com/forms/d/e/1FAIpQLSeSN1AIG8LrdgIdKpBj4IlPDhu6T5ndZ7z_QcISBu-ITCU0Yw/viewform?embedded=true"
              width="100%"
              height="998"
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
    </main>
    <footer-section></footer-section>
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection'
import FooterSection from '@/components/FooterSection'

export default {
  name: 'feedback-page',
  components: {
    HeaderSection,
    FooterSection,
  },
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
</script>
