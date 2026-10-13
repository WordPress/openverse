# 2022-02-18 Project Propsal: Frontend UI State Cookie

**Author**: @sarayourfriend

- [x] @obulat
- [x] @zackkrida

**[Milestone](https://github.com/WordPress/openverse-frontend/milestone/11)**

## Rationale

We removed all the cookies from the application. That's a good thing generally.
But we _can_ use cookies without a banner and still be GDPR compliant as long as
the cookies are necessary for providing a smoother user experience.

Doing this would fix problems like the UI pop in/out in this
[video](https://user-images.githubusercontent.com/24264157/154730060-dd602b4c-52cf-441b-b0f6-b2d7206244d9.mp4).

## GDPR rules

To quote from https://gdpr.eu/cookies:

> Strictly necessary cookies — These cookies are essential for you to browse the
> website and use its features, such as accessing secure areas of the site.
> Cookies that allow web shops to hold your items in your cart while you are
> shopping online are an example of strictly necessary cookies. These cookies
> will generally be first-party session cookies. While it is not required to
> obtain consent for these cookies, what they do and why they are necessary
> should be explained to the user.

I believe the cookie I am proposing we add in this RFC falls under this and we
would not need a consent banner for it.

We should however add an explanatory page for our cookie usage; potentially this
could just be a general "Privacy" page that links out to the WP.org privacy
policy and explains Openverse specific things.

## Cookie shape

Let's introduce one "ui state" cookie that encodes the following:

```ts
interface UIStateCookie {
  /**
   * Whether the filter sidebar was open during the last page load
   * @defaultValue false
   */
  filterSidebarOpen: boolean;
  /**
   * Record of translation banners that have been dismissed.
   * For increased privacy through obsurity, only actually dismissed
   * locales are present, that way there isn't a running record
   * of all the locales the client has visited.
   */
  translationBannerDismissed: { [slug: WPLocaleSlug]?: true };
  /**
   * The breakpoint of the most recent page load.
   * We do not store the exact screen width because we don't need it
   * and it could inadvertently be used for fingerprinting.
   *
   * The default value will be `md` for non-mobile UAs or when a UA is
   * unavailable. For mobile UAs it will default to `mob`.
   */
  breakpoint: 'xl' | 'lg' | 'md' | 'sm' | 'mob';
}
```

## Implementation plan

- [ ] `useUiStateCookie()` -> Returns an existing cookie or creates a new one
      and saves it. It should be a `reactive` object with custom `set` handlers
      to update the stored cookie value. Creating a new one should sniff the UA
      for the correct default value for `breakpoint`.
  - Additionally: `useSyncUiStateCookieBreakpoint()` -> Called by
    `useUiStateCookie` to sync the breakpoint upon resizing.
- [ ] Update `useMediaQuery` to use the ui state cookie to deduce a default for
      `shouldPassInSSR` based on the breakpoint value.
- [ ] Update the translation banner dismissal to set the cookie property and
      read from it to determine whether to show.
- [ ] Update filter sidebar opening to set the cookie property and read from it
      to determine whether to show.
- [ ] Add new Privacy page that explains our use of cookies and links to
      WP.org's Privacy policy. Replace the page menu privacy link to use the
      internal one.
