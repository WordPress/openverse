=== AI ===
Contributors:      wordpressdotorg, dkotter, jeffpaul
Tags:              ai, artificial intelligence, experiments, abilities, mcp
Tested up to:      7.0
Stable tag:        1.2.0
License:           GPL-2.0-or-later
License URI:       https://spdx.org/licenses/GPL-2.0-or-later.html

AI features, experiments and capabilities for WordPress.

== Description ==

The AI plugin brings AI-powered features directly into your WordPress admin and editing experience.

Requires the WordPress Block Editor.  The Classic Editor plugin and other non-Block Editor editing experiences are not supported.

**What's Inside:**

This plugin is built on the [AI Building Blocks for WordPress](https://make.wordpress.org/ai/2025/07/17/ai-building-blocks) initiative, combining the AI Client library and Abilities API into a unified experience. It serves as both a practical tool for content creators and a reference implementation for developers.

**Current Features:**

* **Abilities Explorer** – Browse and interact with registered AI abilities from a dedicated admin screen.
* **AI Request Logging** – Logs AI requests for observability and debugging.
* **Alt Text Generation** - Generate descriptive alt text for images to improve accessibility.
* **Comment Moderation** - Automatically moderate comments based on toxicity detection and sentiment analysis.
* **Connector Approvals** - Require explicit administrator approval before plugins or themes can use AI connectors configured on this site.
* **Content Classification** – Suggests relevant tags and categories to organize content.
* **Content Resizing** - Shorten, expand, or rephrase selected block content.
* **Content Summarization** - Summarizes long-form content into digestible overviews.
* **Dashboard Widgets** - AI Status and AI Capabilities widgets, plus framework for registering new ones.
* **Editorial Notes** - Reviews post content block-by-block and adds Notes with suggestions for Accessibility, Readability, Grammar, and SEO.
* **Editorial Updates** - Automatically apply editorial notes to content.
* **Excerpt Generation** - Automatically create concise summaries for your posts.
* **Experiment Framework** - Opt-in system that lets you enable only the AI features you want to use.
* **Guidelines** - Allows abilities to respect site-wide editorial standards.
* **Image Generation and Editing** - Create and edit images from post content in the editor, also via the Media Library.
* **Key Encryption** - Encrypts AI provider API keys at rest using bundled libsodium encryption. Keys are transparently decrypted on read and re-encrypted on write. Disabling the experiment or deactivating the plugin restores plaintext keys.
* **Meta Description Generation** - Generates meta description suggestions and integrates those with various SEO plugins.
* **Multi-Provider Support** - Works with AI Connector plugins for providers such as OpenAI, Google, and Anthropic.
* **Suggest Reply** - Adds a "Suggest Reply" action to the Comments screen and Activity widget, enabling moderators to quickly generate comment reply suggestions.
* **Title Generation** - Generate title suggestions for your posts with a single click. Perfect for brainstorming headlines or finding the right tone for your content.
* **Type Ahead** – Contextual type-ahead assistance for suggestions while typing.

**Provider Setup:**

The AI plugin does not include provider credentials or provider implementations by itself. To use AI-powered features, install and activate at least one AI Connector plugin, then configure its credentials in `Settings -> Connectors`. Features may appear unavailable until a connector is installed, authenticated, and capable of the required operation.

Provider connector plugins include [Anthropic](https://wordpress.org/plugins/ai-provider-for-anthropic), [Google](https://wordpress.org/plugins/ai-provider-for-google), [OpenAI](https://wordpress.org/plugins/ai-provider-for-openai), and [others](https://wordpress.org/plugins/tags/connector/).

**Coming Soon:**

We're actively developing new features to enhance your WordPress workflow:

* **AI Playground** – Experiment with different AI models and providers.
* **Content Assistant** – AI-powered writing and editing in Gutenberg.
* **Site Agent** – Natural language WordPress administration.
* **Workflow Automation** – AI-driven task automation.

This is an experimental plugin; functionality may change as we gather feedback from the community.

**Roadmap:**

You can view the active plugin roadmap in a filtered view in the WordPress AI [GitHub Project Board](https://github.com/orgs/WordPress/projects/240/views/1).

== Installation ==

1. Upload the plugin files to the `/wp-content/plugins/ai` directory, or install the plugin through the WordPress plugins screen directly.
2. Activate the plugin through the 'Plugins' screen in WordPress.
3. Install and activate at least one AI Connector plugin, then go to `Settings -> Connectors` and configure its credentials.
4. Go to `Settings -> AI` and globally enable functionality and then enable the individual features or experiments you want to test.
5. Start experimenting with AI features! For the Title Generation experiment, edit a post and click into the title field. You should see a `Generate/Regenerate` button above the field. Click that button and after the request is complete, title suggestions will be displayed in a modal. Choose the title you like and click the `Select` button to insert it into the title field.

== For Developers ==

The AI plugin is designed to be studied, extended, and built upon. Whether you're a plugin developer, agency, or hosting provider, here's what you can do:

**Extend the Plugin:**

* **Build Custom Experiments** - Use the `Abstract_Feature` base class to create your own AI-powered features.
* **Pre-configure Providers** - Hosts and agencies can set up AI Connector plugins so users don't need their own API keys.
* **Abilities Explorer** - Test and explore registered AI abilities (available when experiments are enabled).
* **Register Custom Abilities** - Hook into the Abilities API to add new AI capabilities.
* **Override Default Behavior** - Use filters to customize prompts, responses, and UI elements.
* **Comprehensive Hooks** - Filters and actions throughout the codebase for customization.

**Developer Tools Coming Soon:**

* **AI Playground** - Experiment with different AI models and prompts.
* **MCP (Model Context Protocol)** – Integrate and test Model Context Protocol capabilities in WordPress workflows.
* **Extended Providers** – Support for experimenting with additional or alternate AI providers.

**Get Started:**

1. Read the [Contributing Guide](https://github.com/WordPress/ai/blob/trunk/CONTRIBUTING.md) for development setup
2. Join the conversation in [#core-ai on WordPress Slack](https://wordpress.slack.com/archives/C08TJ8BPULS)
3. Browse the [GitHub repository](https://github.com/WordPress/ai) to see how experiments are built
4. Participate in [discussions](https://github.com/WordPress/ai/discussions) on how best the plugin should iterate.

We welcome contributions! Whether you want to build new experiments, improve existing features, or help with documentation, check out our [GitHub repository](https://github.com/WordPress/ai) to get involved.

== Frequently Asked Questions ==

= What is this plugin for? =

This plugin brings AI-powered writing and editing tools directly into WordPress. It's also a reference implementation for developers who want to build their own AI features.

= Is this safe to use on a production site? =

This is an experimental plugin, so we recommend testing in a staging environment first. Features may change as we gather community feedback. All AI features are opt-in and require manual triggering - nothing happens automatically without your approval.

= Which AI providers are supported? =

The plugin can work with provider connector plugins from [Anthropic](https://wordpress.org/plugins/ai-provider-for-anthropic) (Claude), [Google](https://wordpress.org/plugins/ai-provider-for-google) (Gemini), [OpenAI](https://wordpress.org/plugins/ai-provider-for-openai), and [others](https://wordpress.org/plugins/tags/connector/). Install and activate the relevant connector plugin, then configure it in `Settings -> Connectors`.

= Do I need an API key to use the features? =

Yes, currently you need to provide your own API key for the configured AI Connector plugin, such as OpenAI, Google AI, or Anthropic.

= How much does it cost? =

The plugin itself is free, but you'll need to pay for API usage from your chosen AI provider. Costs vary by provider and usage. Most providers offer free trial credits to get started. There are some local, open source, and free providers (like [Ollama](https://wordpress.org/plugins/ai-provider-for-ollama/)) that can be used as well.

= Can I use this without coding knowledge? =

Absolutely! The plugin is designed for content creators and site administrators. Once your AI Connectors are configured, you can use the AI functionality directly from the post editor.

= Does this plugin support the Classic Editor? =

No.

The AI plugin currently supports only the Block Editor (aka Gutenberg).  The plugin is designed around modern editor APIs, block-based content workflows, and the evolving editing capabilities being developed within WordPress core (including Gutenberg).

The Block Editor has been the default WordPress editing experience since WordPress 5.0 in 2018 and remains the primary focus of active editor development.  Concentrating development efforts on the Block Editor enables the project to ship new features, experiments, and integrations more quickly while avoiding the complexity of maintaining parallel implementations across multiple editing experiences.

Although the Classic Editor plugin continues to have a large installed base, the Core AI team has chosen to prioritize innovation and experimentation within the Block Editor ecosystem.  At this time there are no plans to add official Classic Editor support.

= Where can I get help or report issues? =

You can ask questions in the [#core-ai channel on WordPress Slack](https://wordpress.slack.com/archives/C08TJ8BPULS) or report issues on the [GitHub repository](https://github.com/WordPress/ai/issues).

== Screenshots ==

1. Feature: Image Generation and Editing. Post editor sidebar showing Generate featured image button and the generated featured image preview with Alt Text, Title, and Description.
2. Feature: Image Generation and Editing. Post editor showing Generate Image flows.
3. Feature: Image Generation and Editing. Media Library showing Generate Image flows.
4. Editor Experiment: Alt Text Generation. Image block settings showing Generate Alt Text button and the generated alt text.
5. Editor Experiment: Alt Text Generation. Bulk alt text generation from within the Media Library.
6. Editor Experiment: Comment Moderation. Comments admin screen showing AI-powered comment moderation features, including color-coded badges for toxicity scoring and comment sentiment.
7. Editor Experiment: Comment Moderation. Recent Comments section of the Activity widget showing Sentiment and Toxicity scores.
8. Editor Experiment: Content Classification. AI-powered suggestions for post tags and categories based on content analysis.
9. Editor Experiment: Content Resizing. Shorten, expand, or rephrase selected block content.
10. Editor Experiment: Content Summarization. Post editor sidebar showing Generate AI Summary button and the generated content summary within a Content Summary block.
11. Editor Experiment: Editorial Notes. Post editor sidebar showing Generate Editorial Notes flows.
12. Editor Experiment: Editorial Updates. Applies pending Editorial Notes to your content automatically.
13. Editor Experiment: Excerpt Generation. Post editor sidebar showing Generate Excerpt button and generated excerpt.
14. Editor Experiment: Meta Description Generation. Generates meta description suggestions and integrates those with various SEO plugins.
15. Editor Experiment: Title Generation. Post editor showing Generate button above the post title field and title recommendations in a modal.
16. Editor Experiment: Type-ahead Text. Ghost text suggestions while writing paragraphs in the block editor.
17. Dashboard Widgets. AI Capabilities widget showing Abilities Explorer summary and connected AI providers and model capabilities.
18. Dashboard Widgets. AI Status widget showing three step configuration process.
19. Dashboard Widgets. AI Status widget showing connected AI providers and enabled Features and Experiments.
20. Admin Experiment: Abilities Explorer. Abilities Explorer admin screen listing available AI abilities with filters, providers, and test actions.
21. Admin Experiment: Abilities Explorer. Abilities Explorer's view details screen showing an AI ability’s description, provider, input schema, output schema, and raw data.
22. Admin Experiment: Abilities Explorer. Abilities Explorer's test ability screen showing JSON input data, validation, and input schema reference for an AI ability.
23. Admin Experiment: AI Request Logging. Logs AI requests for observability and debugging. View detailed logs under Tools.
24. Admin Experiment: Connector Approvals. Require explicit administrator approval before plugins or themes can use AI connectors configured on this site.
25. Admin Experiment: Key Generation. Encrypts AI provider API keys at rest using bundled libsodium encryption. Keys are transparently decrypted on read and re-encrypted on write. Disabling the experiment or deactivating the plugin restores plaintext keys.
26. AI Settings. AI settings screen showing toggles to enable specific experiments.

== Changelog ==

= 1.2.0 - 2026-07-14 =

**Added**

- New Experiment: Suggest Reply; gives comment moderators a quick way to generate a reply to a comment through the admin ([#724](https://github.com/WordPress/ai/pull/724)).
- New "Advanced settings" option in Developer Tools to show/hide additional configuration options for features and experiments ([#842](https://github.com/WordPress/ai/pull/842)).
- Bulk "Generate AI Summary" action to the posts and pages list table, enabling summary generation for multiple posts at once ([#650](https://github.com/WordPress/ai/pull/650)).
- New `core/read-content` Ability with secure single-post and query modes (including include and opt-in fields) to enable read-only content access ([#739](https://github.com/WordPress/ai/pull/739)).
- New `core/read-users` Ability that retrieves a single user by ID, email, login, or nicename, or a filtered and paginated users collection, with sensitive fields opt-in and permission-gated ([#774](https://github.com/WordPress/ai/pull/774)).
- An inline admin notice when Connector Approvals are enabled and no AI connectors are yet approved, prompting admins to approve the AI plugin for use ([#830](https://github.com/WordPress/ai/pull/830)).
- Introduce new `wp_ai_client_default_request_timeout` filter to make the default request timeout configurable. Use this for the image generation request timeout ([#862](https://github.com/WordPress/ai/pull/862)).

**Changed**

- Content Summary block detection now checks within nested blocks ([#810](https://github.com/WordPress/ai/pull/810)).
- Move all existing configuration options into a new "Advanced settings" section which is hidden by default ([#842](https://github.com/WordPress/ai/pull/842)).

**Fixed**

- Focus restoration after AI setting saves ([#812](https://github.com/WordPress/ai/pull/812)).
- Added descriptive alt text to AI Home feature card images for improved screen reader accessibility ([#819](https://github.com/WordPress/ai/pull/819)).
- Prevent Type-Ahead assets from loading on the front end ([#820](https://github.com/WordPress/ai/pull/820)).
- Dismissing a type-ahead suggestion with escape should not trigger a new suggestion request ([#840](https://github.com/WordPress/ai/pull/840)).
- Type-ahead ghost text placement and stale suggestions overlapping empty-block placeholders ([#847](https://github.com/WordPress/ai/pull/847)).
- `MutationObserver` crash when editor iframe body isn't ready when using Title Generation ([#849](https://github.com/WordPress/ai/pull/849)).
- Respect an explicit `show_in_abilities` value on curated settings, and leave the flag to WordPress core once core declares it ([#852](https://github.com/WordPress/ai/pull/852)).
- Register initial settings before `core/read-settings` snapshots them ([#856](https://github.com/WordPress/ai/pull/856)).

= 1.1.0 - 2026-06-30 =

**Added**

- New Experiment: Type Ahead; automatically suggests ghost text at the end of paragraphs, can be manually triggered within a paragraph ([#151](https://github.com/WordPress/ai/pull/151), [#776](https://github.com/WordPress/ai/pull/776)).
- New Experiment: Key Encryption; encrypts AI Connector API keys before storing them in the database ([#560](https://github.com/WordPress/ai/pull/560)).
- Ensure all Features that rely on utilizing content are disabled until minimum content thresholds are met ([#581](https://github.com/WordPress/ai/pull/581)).
- New `core/read-settings` Ability ([#691](https://github.com/WordPress/ai/pull/691), [#806](https://github.com/WordPress/ai/pull/806)).
- New `wpai_has_image_generation_support` filter that allows 3rd parties to claim support for Image Generation, for example if authenticating without an API key ([#748](https://github.com/WordPress/ai/pull/748)).
- New setting to choose if guest comments should be moderated or not, defaulting to `yes` ([#751](https://github.com/WordPress/ai/pull/751)).
- Explicit save button to developer settings panel, requiring a user to click save before the Provider and Model settings are saved ([#761](https://github.com/WordPress/ai/pull/761)).
- Documentation callouts that the plugin has targeted support for the Block Editor only ([#766](https://github.com/WordPress/ai/pull/766)).

**Changed**

- Note prompting the user to save after running Editorial Notes ([#682](https://github.com/WordPress/ai/pull/682)).
- Use `__next40pxDefaultSize` for buttons consistently ([#702](https://github.com/WordPress/ai/pull/702)).
- Skip Comment Analysis and Moderation when comment has already been flagged as spam/trash ([#743](https://github.com/WordPress/ai/pull/743)).
- Replace developer mode settings CSS with Stack component ([#785](https://github.com/WordPress/ai/pull/785)).
- Use character-based count instead of word-based to determine when features are available to use ([#802](https://github.com/WordPress/ai/pull/802)).
- Use `Notice` component to display warnings within experiment modals ([#803](https://github.com/WordPress/ai/pull/803)).
- Added success snackbar when saving or resetting developer settings ([#807](https://github.com/WordPress/ai/pull/807)).

**Fixed**

- Add `wordCountType` to check for user's locale and update to count character or words when detecting minimum content length ([#581](https://github.com/WordPress/ai/pull/581)).
- Restrict Content Resizing to REST-exposed post types when a post ID is provided ([#658](https://github.com/WordPress/ai/pull/658)).
- Only show Editorial Updates button when pending Notes are linked to current blocks ([#682](https://github.com/WordPress/ai/pull/682)).
- Hide developer settings on stable Features when AI is disabled ([#737](https://github.com/WordPress/ai/pull/737)).
- Improve readability of Ability Explorer schema output by preventing unicode escaping for non‑ASCII characters ([#740](https://github.com/WordPress/ai/pull/740)).
- The "Last 30 Days" summary period in the AI Requests Logs page now uses a fixed 30-day window so the summary cards and logs table cover the same span ([#753](https://github.com/WordPress/ai/pull/753)).
- Developer Tools popover overlapping the WP admin bar ([#756](https://github.com/WordPress/ai/pull/756)).
- Persistence of suggested terms when running the Content Classification experiment ([#769](https://github.com/WordPress/ai/pull/769)).
- Restored term suggestion pills to their original positions if the backend term assignment API fails, resolving stale state race conditions ([#772](https://github.com/WordPress/ai/pull/772)).
- Preserve omitted `runAbility()` input so ability schema defaults can apply when abilities are invoked without input ([#775](https://github.com/WordPress/ai/pull/775)).
- Ensure scalar input schemas are allowed in the Abilities Explorer validation ([#787](https://github.com/WordPress/ai/pull/787)).
- Standardize the Title Generation button text ([#790](https://github.com/WordPress/ai/pull/790)).
- Scope the Editorial Note generation loading spinner only to the block currently being reviewed ([#794](https://github.com/WordPress/ai/pull/794)).
- Snackbar notifications no longer overlap the settings content; they are pinned to the bottom-left of the content area ([#801](https://github.com/WordPress/ai/issues/801)).

= 1.0.2 - 2026-06-15 =

**Added**

- Manual refresh button to the AI Request Logs table header ([#687](https://github.com/WordPress/ai/pull/687)).
- New `ai_generated` param on our Image Import Ability to set if the imported image was AI generated or not ([GHSA-42mg-ffvx-4xff](https://github.com/WordPress/ai/security/advisories/GHSA-42mg-ffvx-4xff)).


**Changed**

- Ensure Editorial Notes and Editorial Updates controls stay grouped together in the post editor sidebar ([#605](https://github.com/WordPress/ai/pull/605)).
- Use explicit UTF-8 encoding for generated Meta Description character counts ([#655](https://github.com/WordPress/ai/pull/655)).
- Return a consistent decorative flag from Alt Text Generation results ([#659](https://github.com/WordPress/ai/pull/659)).
- Show an error message immediately in the Image Generation UI when there's no AI Connector in place that supports image generation ([#679](https://github.com/WordPress/ai/pull/679)).
- Use a neutral icon for disabled Features and Experiments in the AI Status widget ([#720](https://github.com/WordPress/ai/pull/720)).

**Fixed**

- Abilities Explorer schema validation ([#612](https://github.com/WordPress/ai/pull/612)).
- Alt Text Generation button becomes unresponsive after using Next/Previous in the media modal ([#631](https://github.com/WordPress/ai/pull/631)).
- Add descriptive accessible labels to approval matrix toggle controls ([#637](https://github.com/WordPress/ai/pull/637)).
- Added accessible labels to the Provider and Category filter dropdowns on the Abilities Explorer page ([#642](https://github.com/WordPress/ai/pull/642)).
- Lost focus after generating a Title ([#644](https://github.com/WordPress/ai/pull/644)).
- Lost focus when generating Alt Text in Image block inspector controls ([#645](https://github.com/WordPress/ai/pull/645)).
- Lost focus when toggling the Connector Approval state ([#646](https://github.com/WordPress/ai/pull/646)).
- Lost focus after generating Images ([#647](https://github.com/WordPress/ai/pull/647)).
- Added an accessible label to the ability test payload textarea in the Abilities Explorer ([#649](https://github.com/WordPress/ai/pull/649)).
- Excerpt generation post context payload ([#651](https://github.com/WordPress/ai/pull/651)).
- Clear out the Meta Description suggestion when the modal closes ([#653](https://github.com/WordPress/ai/pull/653)).
- Lost focus after running Content Resizing actions ([#663](https://github.com/WordPress/ai/pull/663)).
- Column reordering and hiding in the AI Request Logs table now persists instead of resetting to the default ([#669](https://github.com/WordPress/ai/pull/669)).
- Summary statistics showing zero for short time periods on non-UTC MySQL servers ([#671](https://github.com/WordPress/ai/pull/671)).
- UI inconsistency on AI Request Logs page ([#676](https://github.com/WordPress/ai/pull/676)).
- Ensure thinking tokens are counted in AI Request Logs ([#680](https://github.com/WordPress/ai/pull/680)).
- Ensure the Ability schemas and outputs are valid JSON Schema for strict REST and MCP consumers ([#688](https://github.com/WordPress/ai/pull/688)).
- Title Generation button disappears after toggling off "Show template" ([#694](https://github.com/WordPress/ai/pull/694)).
- Prevent accidental interactions and stale feedback in the Meta Description Generation modal and improve focus handling ([#696](https://github.com/WordPress/ai/pull/696)).
- Ensure focus isn't lost after generating an Excerpt inline ([#698](https://github.com/WordPress/ai/pull/698)).
- AI Request Logs: "Copy Log ID" gives no feedback when copied ([#700](https://github.com/WordPress/ai/pull/700)).
- AI Request Logs: main header overlapping table header ([#705](https://github.com/WordPress/ai/pull/705)).
- Allow users to clear an applied Meta Description while preventing whitespace-only descriptions ([#706](https://github.com/WordPress/ai/pull/706)).
- Rename unforwarded `MaskCanvas` component function to `InnerMaskCanvas` to avoid duplicate declarations ([#713](https://github.com/WordPress/ai/pull/713)).

**Security**

- Remove the `meta` param from our Image Import Ability ([GHSA-42mg-ffvx-4xff](https://github.com/WordPress/ai/security/advisories/GHSA-42mg-ffvx-4xff)).
- Check the current user's capabilities and the comment type before setting an Editorial Note ([GHSA-j7hg-vqpw-f98f](https://github.com/WordPress/ai/security/advisories/GHSA-j7hg-vqpw-f98f)).

= 1.0.1 - 2026-05-27 =

**Added**

- New helper functions that are used to determine if we have valid AI Connector credentials ([#603](https://github.com/WordPress/ai/pull/603)).
- New helper methods, `is_globally_enabled` and `is_individually_enabled` to help tell if a feature is enabled individually or if features are globally enabled ([#604](https://github.com/WordPress/ai/pull/604)).

**Changed**

- Removed the description from the Abilities listing within the Abilities Explorer ([#592](https://github.com/WordPress/ai/pull/592)).
- Filter Guideline queries by the guideline type content ([#593](https://github.com/WordPress/ai/pull/593)).
- Use the new `has_connector_authentication` instead of `is_connector_configured` to avoid unnecessary API requests ([#603](https://github.com/WordPress/ai/pull/603)).

**Removed**

- Deprecated `__nextHasNoMarginBottom` prop ([#609](https://github.com/WordPress/ai/pull/609)).

**Fixed**

- Utilize a new `is_connector_configured` function to properly determine if a connector is configured, whether via an API key, constant or ENV var ([#537](https://github.com/WordPress/ai/pull/537)).
- "Generate Editorial Note" button appearing in the block settings menu during post revisions ([#591](https://github.com/WordPress/ai/pull/591)).
- If the Connector Approvals experiment is turned on, ensure we don't over-aggressively block functionality in the AI plugin that isn't actually making requests, like Request Logging ([#595](https://github.com/WordPress/ai/pull/595)).
- Better matching of the originating code when the Connector Approvals experiment is on ([#595](https://github.com/WordPress/ai/pull/595)).
- Focus loss issues when interacting with Purge actions in the Request Logs experiments page ([#599](https://github.com/WordPress/ai/pull/599)).
- Disable the "Purge All" button when no logs are available to purge ([#599](https://github.com/WordPress/ai/pull/599)).
- AI Status feature checklist properly shows if an individual feature is enabled even if globally features are disabled ([#604](https://github.com/WordPress/ai/pull/604)).
- Ensure focus isn't lost when buttons enter disabled state during Alt Text Generation, Content Classification, Content Summarization, Excerpt Generation, Featured Image Generation, and Title Generation ([#608](https://github.com/WordPress/ai/pull/608), [#611](https://github.com/WordPress/ai/pull/611)).
- Settings page strings, which are enqueued as script modules, are now localized at runtime ([#613](https://github.com/WordPress/ai/pull/613)).
- Connector Approvals "Dismiss" button failing for pending requests whose key contains a slash ([#615](https://github.com/WordPress/ai/pull/615)).
- Hide empty provider capabilities section in the dashboard widget ([#616](https://github.com/WordPress/ai/pull/616)).
- Playground and test configs now target the latest WordPress release instead of the beta release ([#626](https://github.com/WordPress/ai/pull/626)).
- Connector Approvals notice no longer overlaps the page header on the AI Request Logs screen ([#628](https://github.com/WordPress/ai/pull/628)).

= 1.0.0 - 2026-05-19 =

**Added**

- New Experiment: Request Logging that provides observability for all AI operations ([#437](https://github.com/WordPress/ai/pull/437)).
- New Experiment: Connector Approvals that allows administrators the ability to determine which plugins can access which AI connectors ([#467](https://github.com/WordPress/ai/pull/467)).
- Integrate Alt Text generation into the experimental media editor ([#446](https://github.com/WordPress/ai/pull/446)).
- Sorting and filtering in Comments screen by Toxicity and/or Sentiment ([#518](https://github.com/WordPress/ai/pull/518)).
- Toxicity and Sentiment labelling in admin dashboard for comments ([#518](https://github.com/WordPress/ai/pull/518)).

**Changed**

- Disable the Summarization button until content reaches a certain length ([#492](https://github.com/WordPress/ai/pull/492)).
- Refined image generation loading state ([#512](https://github.com/WordPress/ai/pull/512)).
- Featured image button now hides when image is already set ([#512](https://github.com/WordPress/ai/pull/512)).
- When no AI provider is configured and a feature is triggered, show actionable guidance directing users to configure an AI Connector ([#523](https://github.com/WordPress/ai/pull/523)).
- Update Meta Description loading state and remove duplicate heading in modal ([#527](https://github.com/WordPress/ai/pull/527)).
- Rename "Review Notes" experiment to "Editorial Notes" and "Refine from Notes" experiment to "Editorial Updates" ([#528](https://github.com/WordPress/ai/pull/528)).
- Keep comments without moderation metadata visible when sorting by Comment Moderation columns ([#538](https://github.com/WordPress/ai/pull/538)).
- Updated plugin banner and icons ([#546](https://github.com/WordPress/ai/pull/546)).
- Show a notice when a user has chosen a provider that no longer exists ([#552](https://github.com/WordPress/ai/pull/552)).
- When no provider is configured, show an error notice instead of an admin notice for alt text generation ([#561](https://github.com/WordPress/ai/pull/561)).
- Standardize error message text ([#562](https://github.com/WordPress/ai/pull/562)).
- Abilities Explorer page heading ([#585](https://github.com/WordPress/ai/pull/585)).

**Fixed**

- Ensure we properly use the new client-side Abilities API ([#482](https://github.com/WordPress/ai/pull/482)).
- Keep keyboard focus on the Provider select when resetting per-feature developer settings to default ([#532](https://github.com/WordPress/ai/pull/532)).
- Deduplicate provider API requests on the settings page when developer mode is toggled on ([#542](https://github.com/WordPress/ai/pull/542)).
- Update the Playground Preview workflow to use `pluginData` instead of `pluginZipFile` ([#548](https://github.com/WordPress/ai/pull/548)).
- Empty space shown for Model field when saved provider no longer exists in developer settings ([#552](https://github.com/WordPress/ai/pull/552)).
- Prevent analyzing newly inserted comments when no provider is configured ([#554](https://github.com/WordPress/ai/pull/554)).
- Ensure the meta description modal doesn't open if no provider is configured ([#558](https://github.com/WordPress/ai/pull/558)).
- False error for alt text generation on decorative images in media library ([#559](https://github.com/WordPress/ai/pull/559)).
- Show a failed badge when comment analysis fails ([#568](https://github.com/WordPress/ai/pull/568)).
- Correct RTL rendering of directional icons, runtime-set styles, and inline styles in the admin UI ([#573](https://github.com/WordPress/ai/pull/573)).
- Add notice to standalone image generation when there is no provider connected ([#575](https://github.com/WordPress/ai/pull/575)).
- Ensure we show a more specific error message when no valid AI connector is in place and we try to generate a featured image ([#576](https://github.com/WordPress/ai/pull/576)).
- Improve keyboard focus visibility for suggested term actions in content classification ([#580](https://github.com/WordPress/ai/pull/580)).
- User-facing text in several experiments is now fully translatable, and JS-side translations are loaded at runtime ([#582](https://github.com/WordPress/ai/pull/582)).
- Make title generation and content classification UI react to current editor state ([#584](https://github.com/WordPress/ai/pull/584)).
- Ensure global AI enabled options are migrated properly ([#586](https://github.com/WordPress/ai/pull/586)).

= 0.9.0 - 2026-05-07 =

**Added**

* New Experiment: Comment Moderation to automatically moderate comments based on toxicity detection and sentiment analysis ([#155](https://github.com/WordPress/ai/pull/155), [#516](https://github.com/WordPress/ai/pull/516)).
* New Experiment: Content Resizing to shorten, expand, or rephrase selected block content ([#331](https://github.com/WordPress/ai/pull/331)).
* Developer Mode settings page toggle to set the desired provider and model per feature ([#486](https://github.com/WordPress/ai/pull/486)).
* WP-CLI command, `wp ai alt-text generate`, for bulk alt text generation ([#436](https://github.com/WordPress/ai/pull/436)).
* Basic styles for the Content Summary block ([#510](https://github.com/WordPress/ai/pull/510)).

**Changed**

* Compress the AI settings page by moving the global AI toggle into the header with an infotip ([#455](https://github.com/WordPress/ai/pull/455)).
* Update AI settings page to use `@wordpress/ui` components and related UI adjustments ([#472](https://github.com/WordPress/ai/pull/472), [#488](https://github.com/WordPress/ai/pull/488), [#490](https://github.com/WordPress/ai/pull/490), [#491](https://github.com/WordPress/ai/pull/491), [#505](https://github.com/WordPress/ai/pull/505), [#519](https://github.com/WordPress/ai/pull/519)).
* AI-generated images are now saved with descriptive, slugified filenames derived from the post title or prompt instead of `ai-generated-image-<timestamp>` ([#471](https://github.com/WordPress/ai/pull/471)).
* For image generation, set guidelines as part of the prompt instead of system instructions ([#497](https://github.com/WordPress/ai/pull/497)).
* Update the Content Summary experiment to render the summary in a Group variation block instead of a Paragraph variation block ([#510](https://github.com/WordPress/ai/pull/510)).

**Fixed**

* Standards compliance switch from the custom `$builder->is_text_generation_supported()` method with the abstract `ensure_text_generation_supported()` method ([#465](https://github.com/WordPress/ai/pull/465)).
* Ability schema JSON viewer now stays LTR under RTL admin languages ([#485](https://github.com/WordPress/ai/pull/485)).
* Ensure the Generate Image button doesn't render in contexts that aren't valid ([#489](https://github.com/WordPress/ai/pull/489)).
* Localize several user-facing fallback error strings in image-generation and summarization flows ([#500](https://github.com/WordPress/ai/pull/500)).

**Security**

* Bump `serialize-javascript` from 6.0.2 to 7.0.5 ([#503](https://github.com/WordPress/ai/pull/503)).
* Bump `postcss` from 8.5.10 to 8.5.14 ([#503](https://github.com/WordPress/ai/pull/503)).
* Bump `minimatch` from 3.0.8 to 3.1.4 ([#503](https://github.com/WordPress/ai/pull/503)).

Older changelog entries can be found in the [CHANGELOG.md](https://github.com/WordPress/ai/blob/trunk/CHANGELOG.md) file.

== Upgrade Notice ==

= 0.6.0 =
This version includes Breaking Changes.

= 0.5.0 =
This version bumps the WordPress minimum supported version from 6.9 to 7.0.
