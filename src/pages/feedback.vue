<template>
  <div class="section" dir="ltr">
    <div class="container">
      <div class="pb-6">
        <h1 id="feedback" class="text-5xl mb-10">
          {{ $t('feedback.title') }}
        </h1>
        <i18n path="feedback.description.content" tag="p" class="mb-6">
          <template #openverse>
            <VLink href="https://wordpress.slack.com/messages/openverse/">
              {{ $t('feedback.description.openverse') }}</VLink
            >
          </template>
          <template #making-wordpress>
            <VLink href="https://make.wordpress.org/chat/">
              {{ $t('feedback.description.making-wordpress') }}</VLink
            >
          </template>
        </i18n>
        <section class="tabs mt-6">
          <div role="tablist" :aria-label="$t('feedback.title')">
            <button
              v-for="(name, index) in tabs"
              :id="name"
              :key="index"
              :class="tabClass(index, 'tab')"
              role="tab"
              :aria-selected="activeTab === index"
              :aria-controls="`tab-${name}`"
              @click.prevent="setActiveTab(index)"
              @keyup.enter.prevent="setActiveTab(index)"
            >
              {{ $t(`feedback.${name}`) }}
            </button>
          </div>
          <div
            v-for="(name, index) in tabs"
            :id="`tab-${name}`"
            :key="index"
            :class="tabClass(index, 'tabs-panel')"
            :aria-labelledby="name"
            role="tabpanel"
            tabindex="0"
          >
            <iframe
              class="form-iframe"
              :aria-label="$t(`feedback.aria.${name}`)"
              :src="forms[name]"
              :title="`${name} form`"
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
import VLink from '~/components/VLink.vue'

const bugForm =
  'https://docs.google.com/forms/d/e/1FAIpQLSenCn-3HoZlCz4vlL2621wjezfu1sPZDaWGe_FtQ1R5-5qR4Q/viewform'
const suggestionForm =
  'https://docs.google.com/forms/d/e/1FAIpQLSfGC7JWbNjGs-_pUNe3B2nzBW-YrIrmRd92t-7u0y7s8jMjzQ/viewform'

export const FeedbackPage = {
  name: 'feedback-page',
  components: { VLink },
  data() {
    return {
      activeTab: 0,
      tabs: ['improve', 'report'],
      forms: {
        report: `${bugForm}?embedded=true`,
        improve: `${suggestionForm}?embedded=true`,
      },
    }
  },
  head() {
    return {
      title: `${this.$t('feedback.title')} | ${this.$t('hero.brand')}`,
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
}

export default FeedbackPage
</script>
<style lang="scss" scoped>
.form-iframe {
  width: 100%;
  height: 1200px;
  border: none;
}
</style>
