<template>
  <VContentPage>
    <h1 id="feedback">
      {{ $t('feedback.title') }}
    </h1>
    <i18n path="feedback.intro" tag="p">
      <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
      <template #openverse>Openverse</template>
      <template #slack>
        <VLink href="https://wordpress.slack.com/messages/openverse/"
          >#openverse</VLink
        >
      </template>
      <template #making-wordpress>
        <VLink href="https://make.wordpress.org/chat/">Making WordPress</VLink>
      </template>
      <!-- eslint-enable @intlify/vue-i18n/no-raw-text -->
    </i18n>
    <section>
      <div role="tablist" :aria-label="$t('feedback.title')">
        <button
          v-for="(name, index) in tabs"
          :id="name"
          :key="index"
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
  </VContentPage>
</template>

<script>
import VLink from '~/components/VLink.vue'
import VContentPage from '~/components/VContentPage.vue'

const bugForm =
  'https://docs.google.com/forms/d/e/1FAIpQLSenCn-3HoZlCz4vlL2621wjezfu1sPZDaWGe_FtQ1R5-5qR4Q/viewform'
const suggestionForm =
  'https://docs.google.com/forms/d/e/1FAIpQLSfGC7JWbNjGs-_pUNe3B2nzBW-YrIrmRd92t-7u0y7s8jMjzQ/viewform'

export const FeedbackPage = {
  name: 'feedback-page',
  components: { VLink, VContentPage },
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
      title: `${this.$t('feedback.title')} | Openverse`,
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

<style scoped>
.form-iframe {
  width: 100%;
  height: 1200px;
  border: none;
}
</style>
