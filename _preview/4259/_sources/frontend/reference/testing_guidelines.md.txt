# Testing Guidelines

This document describes general guidelines you should follow when testing the
/frontend pull requests. It is not exhaustive but should be the starting point
that you adapt for each PR. You may also use your best judgement and skip things
that are unrelated to a specific PR. However, please be careful when doing this
as accessibility bugs _especially_ are easy to slip through the cracks when we
aren't doing our due diligence and testing changes thoroughly.

## Running the application

Please follow the instructions in the README for how to set up and run the
application locally. If you want to just generally test the application in its
current state (i.e., what exists on `main` as opposed to what has actually been
deployed to production) you can find the staging deployment here:

https://staging.openverse.org

Staging is redeployed every time we merge to the `main` branch, so if you're
looking to test the latest version of the app without going through the local
set up, that's the easiest way to go.

Once you have the application running, you can visit it in your browser at
http://localhost:8443.

You can also access it from other devices in your same network (like a mobile
phone) for additional testing. See the
[finding your local IP address](/frontend/reference/miscellaneous.md#finding-your-local-ip-address)
section of the README for how to identify the local IP address Nuxt is served
on. Once you have identified your local IP address, you can access the website
running on your computer by visiting `https://<local IP>:8443` replacing
`<local IP>` (including the brackets) with the value you found using the
instructions above in your mobile device's browser.

Testing from multiple different devices as often as possible is a great way to
contribute to Openverse's frontend development.

### API Authentication

By default, the application will run using the production API without
authentication. This means your local frontend server may be subject to the
unauthenticated rate limiting, depending on your testing behavior. There are two
ways to solve this:

1. You can change your local Nuxt server to point to a local API server that
   does not have throttling enabled
2. You can introduce the environment variables necessary for authenticating with
   an API

For the first, [run the Openverse API locally](/api/guides/quickstart.md). Then
create a `.env` file by copying the `.env.template` file and update it with the
following:

```shell
API_URL="http://localhost:8000/"
```

Be sure to remove the leading `#` to uncomment the variable from the copied
template.

The run the dev server as usual:

```shell
pnpm dev
```

For the second, you'll need to follow
[the instructions to set up an OAuth application](https://api.openverse.org/v1/#section/Register-and-Authenticate)
and then fill in the `API_CLIENT_ID` and `API_CLIENT_SECRET` in the `.env` file
copied from `.env.template`. Be sure to remove the leading `#` to uncomment
these variables from the copied template.

```shell
API_CLIENT_ID=""
API_CLIENT_SECRET=""
```

Then run the API as usual using `just api/up` & `just api/init`. Nuxt
automatically loads `.env` files into the environment. With these variables in
the environment, all requests made by your server will be made using an access
token retrieved by the `~/plugins/api-token.server.ts` plugin.

Once the `.env` file is set up, you may run the development build the typical
way:

```shell
just frontend/run dev
```

## Browsers

In addition to testing on multiple devices, we also strive to test on almost all
widely used browsers excluding Internet Explorer. Please be ready to regularly
test your work and the work of others in Firefox, Chrome, and Safari on a
desktop computer. On mobile devices, Mobile Safari on iOS, Firefox for Android
and Mobile Chrome on iOS are all important targets for testing as well. A
significant amount of web traffic is mobile these days.

## Accessibility

### Prerequisite reading

Please review the
[WordPress Accessibility Handbook](https://make.wordpress.org/accessibility/handbook/).

The [WAI-ARIA](https://www.w3.org/TR/wai-aria/) spec. This document describes,
in detail, all of the documented types of interactions that happen on most
websites and the accessibility properties of them. Many of them also include
examples.

Gutenberg also has an excellent
[Accessibility Testing Guide](https://github.com/WordPress/gutenberg/blob/5413ddbced8cbe0f0f10eb7739dbc34a7e56adee/docs/contributors/accessibility-testing.md)
with specific instructions for setting up screen readers for testing with.

### General recommendations

Practice using keyboard navigation when you run the app locally generally. This
will reveal to you some of the initial hurdles that the app currently presents
to users who rely on assistive technology. Note that keyboard accessibility is
part of the bare-minimum in accessibility for a website along with accessible
color contrasts.

If you are a regular contributor, at least once a week, attempt to use the site
using a screen reader like VoiceOver on macOS, NVDA on Windows, or Orca on
Linux. If you do not regularly rely on a screen reader for navigating the web,
it can also stretch your comfort level a lot by closing your eyes or turning off
your monitor while navigating using the screen reader. Keep in mind that many
people who rely on screen readers to navigate the web do not have any of the
visual context that a sighted user is using to interpret a website. This
especially applies to directionality and the _broad_ context of a page. Screen
readers can't "see" what's at the "end" of the page unless the user navigates
all the way there. Sighted users have a huge privilege in being able to take in
the broader context of a website almost immediately through visual information.

## Specific things to test for

### Focus styles

Buttons, form fields, and other interactive elements should all have visible and
high contrast focus styles applied. Please note that hover styles are _not_ the
same as focus styles and are often distinct. Note also that hover styles and
focus styles may not always be applied at the same time. It is best to test the
following scenarios:

1. Hover over the element, unfocused
2. Focus the element using the keyboard, no mouse hover
3. Focus the element using the keyboard and also hover over it with the mouse

That will exhaust 95% of the interactions that visible focus styles need to
cover.

### Interactiveness

Buttons should be able to be activated using mouse click, <kbd>Enter</kbd> and
<kbd>Space</kbd> keys. Links should be able to be activated using a mouse click
and <kbd>Enter</kbd> but not <kbd>Space</kbd>.

Arrow keys are common methods for navigating distinct UI elements, especially
composite groups like field sets, radio groups, menus, and other
[composite elements](https://www.w3.org/TR/wai-aria-1.1/#composite). Please test
these interactions and compare them against the WAI-ARIA examples for the same
UI components.

### Screen reader intelligibility

When testing a new piece of UI, please test it thoroughly with a screen reader
paying close attention to what the screen reader is saying, in particular how it
is describing parts of the page.

Buttons, for example, should have appropriate labels. If the visible text of the
button relies on some wider visual context to be intelligible, ensure that it
has an appropriate `aria-label` that a screen reader can use to give more
information about the button.

### Server vs client side render

The Openverse frontend is a Nuxt SSR application. This means the initial Vue
page rendering when you make a request is processed by a server and then
delivered to you to be "hydrated" with the current state of the page. The
implication of this is that there are two ways for _every single page_ to be
rendered, and we should test with that in mind. Please make sure that you are
testing client side navigation as well as SSR. To test SSR for a page, simply
reload the page: it will be rendered in SSR and then delivered to your browser.
To test client side rendering for a page, navigate to that page from another
page without reloading the page in between. For example, to test the search
route client side, you can execute a search from the homepage and it will
redirect you client-side to the search page.

### Conclusion

Please note that these are non-expert and non-exhaustive recommendations. Spend
time reading the [WAI-ARIA spec](https://www.w3.org/TR/wai-aria/) and other web
accessibility materials. Even just knowing about specific roles and interactions
that exist and are meant to be developed in consistent ways is a good first step
to learning what to look out for when testing.

## Automated tests

Openverse uses
[Vue Testing Library](https://testing-library.com/docs/vue-testing-library/intro/)
for unit testing with [Jest](https://jestjs.io/docs/), and
[Playwright](https://playwright.dev) for end-to-end and visual-regression
testing.

There are also legacy unit tests written in
[Vue Test Utils](https://vue-test-utils.vuejs.org/) but those are slated to be
re-written using testing library.

### Playwright tests

Please see the
[Playwright test guidelines](/frontend/reference/playwright_tests.md) for
instructions on running and maintaining the Playwright test suite, and the
[Storybook test guidelines](/frontend/reference/storybook_tests.md) for
instructions on the Storybook Playwright test suite.
