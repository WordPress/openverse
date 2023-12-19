<template>
  <VContentPage>
    <h1>
      {{ $t("sensitive.title") }}
    </h1>

    <i18n-t keypath="sensitive.description.content" tag="p">
      <template #openverse>Openverse</template>
      <template #wpCoc
        ><VLink
          href="https://make.wordpress.org/handbook/community-code-of-conduct/"
          >{{ $t("sensitive.description.wpCoc") }}</VLink
        ></template
      >
      <template #deiStatement
        ><VLink
          href="https://make.wordpress.org/handbook/diversity-equity-and-inclusion-in-wordpress/"
          >{{ $t("sensitive.description.deiStatement") }}</VLink
        ></template
      >
    </i18n-t>

    <p>{{ $t("sensitive.sensitivity.what", { openverse: "Openverse" }) }}</p>
    <p>{{ $t("sensitive.sensitivity.how", { openverse: "Openverse" }) }}</p>

    <h2 id="on-off">
      {{ $t("sensitive.onOff.title") }}
    </h2>

    <p>
      {{ $t("sensitive.onOff.sensitiveResults", { openverse: "Openverse" }) }}
    </p>

    <p>
      {{ $t("sensitive.onOff.blurSensitive", { openverse: "Openverse" }) }}
    </p>

    <p>
      {{ $t("sensitive.onOff.where", { openverse: "Openverse" }) }}
    </p>

    <h2 id="designations">
      {{ $t("sensitive.designations.title") }}
    </h2>

    <p>
      {{ $t("sensitive.designations.description", { openverse: "Openverse" }) }}
    </p>

    <h3 id="user-reported-sensitivity">
      {{ $t("sensitive.designations.userReported.title") }}
    </h3>

    <i18n-t keypath="sensitive.designations.userReported.description" tag="p">
      <template #openverse>Openverse</template>
      <template #gutenbergMediaInserter>
        <VLink
          href="https://learn.wordpress.org/tutorial/add-media-and-openverse-images-to-your-content-directly-from-the-inserter/"
          >{{
            $t("sensitive.designations.userReported.gutenbergMediaInserter", {
              openverse: "Openverse",
            })
          }}</VLink
        >
      </template>
    </i18n-t>

    <h3 id="sensitive-textual-content">
      {{ $t("sensitive.designations.sensitiveText.title") }}
    </h3>

    <i18n-t keypath="sensitive.designations.sensitiveText.description" tag="p">
      <template #openverse>Openverse</template>
      <template #sensitiveTermsList>
        <VLink href="https://github.com/wordpress/openverse-sensitive-terms">{{
          $t("sensitive.designations.sensitiveText.sensitiveTermsList")
        }}</VLink>
      </template>
      <template #imperfect>
        <VLink
          href="https://docs.openverse.org/projects/proposals/trust_and_safety/detecting_sensitive_textual_content/20230309-implementation_plan_sensitive_terms_list.html#this-will-not-be-perfect"
          >{{
            $t("sensitive.designations.sensitiveText.imperfect", {
              sectionName: "This will not be perfect",
            })
          }}</VLink
        >
      </template>
    </i18n-t>

    <i18n-t keypath="sensitive.designations.sensitiveText.metadata" tag="p">
      <template #openverse>Openverse</template>
      <template #notAvailable>
        <VLink href="https://github.com/WordPress/openverse/issues/2594">{{
          $t("sensitive.designations.sensitiveText.notAvailable")
        }}</VLink>
      </template>
    </i18n-t>

    <h2>
      {{ $t("sensitive.faq.title") }}
    </h2>

    <p>
      <strong>{{ $t("sensitive.faq.one.question") }}</strong
      ><br />
      {{ $t("sensitive.faq.one.answer", { openverse: "Openverse" }) }}
    </p>

    <p>
      <strong>{{ $t("sensitive.faq.two.question") }}</strong
      ><br />
      {{ $t("sensitive.faq.two.answerPt1", { openverse: "Openverse" }) }}
    </p>
    <p>{{ $t("sensitive.faq.two.answerPt2", { openverse: "Openverse" }) }}</p>

    <p>
      <strong>{{
        $t("sensitive.faq.three.question", { openverse: "Openverse" })
      }}</strong
      ><br />
      {{ $t("sensitive.faq.three.answer", { openverse: "Openverse" }) }}
    </p>
  </VContentPage>
</template>

<script lang="ts">
import { defineNuxtComponent, definePageMeta, useHead, useI18n } from "#imports"

import VLink from "~/components/VLink.vue"
import VContentPage from "~/components/VContentPage.vue"

export default defineNuxtComponent({
  name: "SensitiveContent",
  components: { VLink, VContentPage },
  setup() {
    definePageMeta({
      layout: "content-layout",
    })
    const i18n = useI18n()

    useHead({
      title: `${i18n.t("sensitive.title")} | Openverse`,
      meta: [{ name: "robots", content: "all" }],
    })
  },
})
</script>
