import { describe, expect, test } from "vitest"

import { getIssueDestination } from "./issues.mjs"

const label = (name) => ({ name })

describe("getIssueDestination", () => {
  test("critical issues go directly to ToDo when opened", () => {
    expect(
      getIssueDestination(
        { labels: [label("🟥 priority: critical")] },
        "opened"
      )
    ).toBe("ToDo")
  })

  test("blocked issues go to Blocked when opened", () => {
    expect(
      getIssueDestination({ labels: [label("⛔ status: blocked")] }, "opened")
    ).toBe("Blocked")
  })

  test("critical priority takes precedence over blocked status", () => {
    expect(
      getIssueDestination(
        {
          labels: [label("🟥 priority: critical"), label("⛔ status: blocked")],
        },
        "opened"
      )
    ).toBe("ToDo")
  })

  test("ordinary issues go to Backlog when opened", () => {
    expect(getIssueDestination({ labels: [] }, "opened")).toBe("Backlog")
  })

  test("adding the blocked label moves an issue to Blocked", () => {
    expect(
      getIssueDestination(
        {
          labels: [label("⛔ status: blocked")],
        },
        "labeled",
        label("⛔ status: blocked")
      )
    ).toBe("Blocked")
  })

  test("adding critical priority moves an issue directly to ToDo", () => {
    expect(
      getIssueDestination(
        {
          labels: [label("🟥 priority: critical")],
        },
        "labeled",
        label("🟥 priority: critical")
      )
    ).toBe("ToDo")
  })

  test("removing blocked status returns a non-critical issue to Backlog", () => {
    expect(
      getIssueDestination(
        { labels: [] },
        "unlabeled",
        label("⛔ status: blocked")
      )
    ).toBe("Backlog")
  })

  test("removing critical priority returns an issue to Backlog", () => {
    expect(
      getIssueDestination(
        { labels: [] },
        "unlabeled",
        label("🟥 priority: critical")
      )
    ).toBe("Backlog")
  })

  test("closed completed issues go to Done", () => {
    expect(
      getIssueDestination({ labels: [], state_reason: "completed" }, "closed")
    ).toBe("Done")
  })

  test("closed rejected issues go to Discarded", () => {
    expect(
      getIssueDestination({ labels: [], state_reason: "not planned" }, "closed")
    ).toBe("Discarded")
  })

  test("unrelated label changes do not move ordinary issues", () => {
    expect(
      getIssueDestination(
        { labels: [] },
        "labeled",
        label("🧩 aspect: interface")
      )
    ).toBeNull()
  })

  test("unrelated label changes do not move critical issues", () => {
    expect(
      getIssueDestination(
        { labels: [label("🟥 priority: critical")] },
        "labeled",
        label("🧩 aspect: interface")
      )
    ).toBeNull()
  })
})
