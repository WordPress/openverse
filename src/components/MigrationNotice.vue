<template>
  <NoticeBar>
    {{ $t('migration-notice.intro') }}
    <i18n tag="p" path="migration-notice.more">
      <template #read-more>
        <a
          class="text-dark-blue hover:text-dark-blue underline"
          href="https://wordpress.org/news/2021/05/welcome-to-openverse/"
          target="_blank"
          >{{ $t('migration-notice.read') }}</a
        >
      </template>
    </i18n>
  </NoticeBar>
</template>

<script>
import NoticeBar from '~/components/NoticeBar/NoticeBar.vue'

export default {
  name: 'MigrationNotice',
  components: { NoticeBar },
}
</script>
