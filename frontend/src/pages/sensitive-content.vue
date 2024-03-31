<template>
  <VContentPage>
    <h1>
      {{ $t("sensitive.title") }}
    </h1>

    <p>
      {{ $t("sensitive.description.content.a", { openverse: "Openverse" }) }}
      {{
        $t("sensitive.description.content.b", {
          openverse: "Openverse",
          openverseOrg: "Openverse.org",
        })
      }}
      <i18n path="sensitive.description.content.c" tag="span">
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
      </i18n>
      {{
        $t("sensitive.description.content.d", {
          openverse: "Openverse",
          openverseOrg: "Openverse.org",
        })
      }}
      {{ $t("sensitive.description.content.e", { openverse: "Openverse" }) }}
      {{ $t("sensitive.description.content.f", { openverse: "Openverse" }) }}
    </p>

    <p>
      {{ $t("sensitive.sensitivity.what.a", { openverse: "Openverse" }) }}
      {{ $t("sensitive.sensitivity.what.b") }}
      {{ $t("sensitive.sensitivity.what.c", { openverse: "Openverse" }) }}
      {{ $t("sensitive.sensitivity.what.d") }}
    </p>

    <p>
      {{ $t("sensitive.sensitivity.how.a") }}
      {{ $t("sensitive.sensitivity.how.b", { openverse: "Openverse" }) }}
      {{ $t("sensitive.sensitivity.how.c") }}
    </p>

    <h2 id="on-off">
      {{ $t("sensitive.onOff.title") }}
    </h2>

    <p>
      {{ $t("sensitive.onOff.sensitiveResults", { openverse: "Openverse" }) }}
    </p>

    <p>
      {{ $t("sensitive.onOff.blurSensitive.a") }}
      {{ $t("sensitive.onOff.blurSensitive.b") }}
    </p>

    <p>
      {{ $t("sensitive.onOff.where", { openverse: "Openverse" }) }}
    </p>

    <h2 id="designations">
      {{ $t("sensitive.designations.title") }}
    </h2>

    <p>
      {{
        $t("sensitive.designations.description.a", {
          openverse: "Openverse",
          openverseOrg: "Openverse.org",
        })
      }}
      {{ $t("sensitive.designations.description.b") }}
    </p>

    <h3 id="user-reported-sensitivity">
      {{ $t("sensitive.designations.userReported.title") }}
    </h3>

    <p>
      {{
        $t("sensitive.designations.userReported.description.a", {
          openverse: "Openverse",
          openverseOrg: "Openverse.org",
        })
      }}
      <i18n path="sensitive.designations.userReported.description.b" tag="span">
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
      </i18n>
      {{ $t("sensitive.designations.userReported.description.c") }}
      {{
        $t("sensitive.designations.userReported.description.d", {
          openverse: "Openverse",
        })
      }}
    </p>

    <h3 id="sensitive-textual-content">
      {{ $t("sensitive.designations.sensitiveText.title") }}
    </h3>

    <p>
      {{
        $t("sensitive.designations.sensitiveText.description.a", {
          openverse: "Openverse",
        })
      }}
      <i18n
        path="sensitive.designations.sensitiveText.description.b"
        tag="span"
      >
        <template #openverse>Openverse</template>
        <template #sensitiveTermsList>
          <VLink
            href="https://github.com/wordpress/openverse-sensitive-terms"
            >{{
              $t("sensitive.designations.sensitiveText.sensitiveTermsList")
            }}</VLink
          >
        </template>
      </i18n>
      {{
        $t("sensitive.designations.sensitiveText.description.c", {
          openverse: "Openverse",
        })
      }}
      {{ $t("sensitive.designations.sensitiveText.description.d") }}
      <i18n
        path="sensitive.designations.sensitiveText.description.e"
        tag="span"
      >
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
      </i18n>
    </p>

    <p>
      <i18n path="sensitive.designations.sensitiveText.metadata.a" tag="span">
        <template #openverse>Openverse</template>
        <template #openverseOrg>Openverse.org</template>
        <template #notAvailable>
          <VLink href="https://github.com/WordPress/openverse/issues/2594">{{
            $t("sensitive.designations.sensitiveText.notAvailable")
          }}</VLink>
        </template>
      </i18n>
      {{ $t("sensitive.designations.sensitiveText.metadata.b") }}
      {{
        $t("sensitive.designations.sensitiveText.metadata.c", {
          openverse: "Openverse",
        })
      }}
      {{
        $t("sensitive.designations.sensitiveText.metadata.d", {
          openverse: "Openverse",
        })
      }}
      {{
        $t("sensitive.designations.sensitiveText.metadata.e", {
          openverse: "Openverse",
        })
      }}
    </p>

    <h2>
      {{ $t("sensitive.faq.title") }}
    </h2>

    <p>
      <strong>{{ $t("sensitive.faq.one.question") }}</strong
      ><br />
      {{ $t("sensitive.faq.one.answer.a", { openverseOrg: "Openverse.org" }) }}
      {{ $t("sensitive.faq.one.answer.b", { openverse: "Openverse" }) }}
    </p>

    <p>
      <strong>{{ $t("sensitive.faq.two.question") }}</strong
      ><br />
      {{ $t("sensitive.faq.two.answerPt1", { openverse: "Openverse" }) }}
    </p>
    <p>
      {{ $t("sensitive.faq.two.answerPt2.a") }}
      {{ $t("sensitive.faq.two.answerPt2.b") }}
      {{ $t("sensitive.faq.two.answerPt2.c", { openverse: "Openverse" }) }}
    </p>

    <p>
      <strong>{{
        $t("sensitive.faq.three.question", { openverse: "Openverse" })
      }}</strong
      ><br />
      {{ $t("sensitive.faq.three.answer.a") }}
      {{ $t("sensitive.faq.three.answer.b") }}
      {{ $t("sensitive.faq.three.answer.c", { openverse: "Openverse" }) }}
    </p>
  </VContentPage>
</template>

<script lang="ts">
import { defineComponent, useMeta } from "@nuxtjs/composition-api"

import { useI18n } from "~/composables/use-i18n"

import VLink from "~/components/VLink.vue"
import VContentPage from "~/components/VContentPage.vue"

export default defineComponent({
  name: "SensitiveContent",
  components: { VLink, VContentPage },
  layout: "content-layout",
  setup() {
    const i18n = useI18n()

    useMeta({
      title: `${i18n.t("sensitive.title")} | Openverse`,
      meta: [{ hid: "robots", name: "robots", content: "all" }],
    })
  },
  head: {},
})
</script>
