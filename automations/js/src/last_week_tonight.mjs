/**
 * Generate a weekly report of closed issues and merged PRs for each of the
 * Openverse repos.
 */

import { readFileSync } from "fs"
import { resolve } from "path"

import yaml from "js-yaml"
import axios from "axios"
import { Octokit } from "@octokit/rest"

import { escapeHtml } from "./utils/html.mjs"

/* Environment variables */

/** the personal access token for the GitHub API */
const pat = process.env.ACCESS_TOKEN
/** the username for the Make site account making the post */
const username = process.env.MAKE_USERNAME
/** the application password, not login password, for the Make site */
const password = process.env.MAKE_PASSWORD

if (!pat) {
  console.log('GitHub personal access token "ACCESS_TOKEN" is required.')
}
if (!username) {
  console.log('Make site username "MAKE_USERNAME" is required.')
}
if (!password) {
  console.log('Make site application password "MAKE_PASSWORD" is required.')
}
if (!(pat && username && password)) process.exit(1)

/* Read GitHub information from the data files */

const githubDataFile = resolve("../data/github.yml") // resolved from `package.json`
// eslint-disable-next-line import/no-named-as-default-member
const githubInfo = yaml.load(readFileSync(githubDataFile))
const org = githubInfo.org
const repos = Object.values(githubInfo.repos)

/* Time period */

const msInWeeks = (weeks) => weeks * 7 * 24 * 60 * 60 * 1e3
// End date is always today
const [endDate] = new Date().toISOString().split("T")
// Start date is one week before today
const [startDate] = new Date(new Date().getTime() - msInWeeks(1))
  .toISOString()
  .split("T")

/* GitHub API */

const octokit = new Octokit({ auth: pat })
const mergedPrsQ = (repo) =>
  `repo:${org}/${repo} is:pr is:merged merged:>=${startDate}`
const closedIssuesQ = (repo) =>
  `repo:${org}/${repo} is:issue is:closed closed:>=${startDate}`

/* Other constants */

const stackNameMap = {
  api: "API",
  mgmt: "Management",
}

/* Format issues, PRs and repos as HTML */

/**
 * Generate the HTML for one closed issues or merged PRs section.
 *
 * @param {string} title - the title to use for the section
 * @param {{html_url: string, number: int, title: string}[]} items - the list of issues/PRs
 * @returns {string[]} - lines of HTML
 */
const getItemsHtml = (title, items) => {
  if (!items.length) return []

  // Get a unique list of stack labels
  const stacks = [
    ...new Set(
      items
        .flatMap((item) => item.labels) // Flatten all labels into a single array
        .map((label) => label.name) // Extract the name of each label
        .filter((name) => name.startsWith("🧱 stack"))
    ),
  ].sort()

  // Aggregate items by stack
  let itemsByStack = {}

  for (const stack of stacks) {
    const stackName = stack.split(":")[1].trim()
    itemsByStack[stackName] = items
      .filter((item) => item.labels.map((label) => label.name).includes(stack))
      .sort((a, b) => a.number - b.number)
  }

  return [
    `<h3>${title}</h3>`,
    // Produce a list of elements for each stack, then combine them all
    ...Object.entries(itemsByStack)
      .map(([stackName, items]) => [
        `<h4>${stackNameMap[stackName] || stackName.replace(/\b[a-z]/g, (match) => match.toUpperCase())}</h4>`,
        "<ul>",
        ...items.map((item) => {
          const href = item.html_url
          const number = `#${item.number}`
          const title = escapeHtml(item.title)
          return `<li><a href="${href}">${number}</a>: ${title}`
        }),
        "</ul>",
      ])
      .flat(),
  ]
}

/**
 * Generate the HTML for the closed issues or merged PRs of one repository.
 *
 * @param {string} repo - the name of the repository
 * @param {{html_url: string, number: int, title: string}[]} mergedPrs - the list of PRs
 * @param {{html_url: string, number: int, title: string}[]} closedIssues - the list of issues
 * @returns {string[]} - lines of HTML
 */
const getRepoHtml = ({ repo, mergedPrs, closedIssues }) => {
  return [
    `<h2><a href="https://github.com/${org}/${repo}">${repo}</a></h2>`,
    ...getItemsHtml("Merged PRs", mergedPrs),
    ...getItemsHtml("Closed issues", closedIssues),
  ]
}

/* Create post on Make site. */

/**
 * Post the activities to the Make site.
 * @param {{
 *   repo: string,
 *   mergedPrs: {html_url: string, number: int, title: string}[],
 *   closedIssues: {html_url: string, number: int, title: string}[]
 * }[]} activities - the list of repos and their activities
 * @returns {Promise} - the response for the POST request
 */
const postActivities = (activities) => {
  const report = activities.map(getRepoHtml).flat().join("\n")

  const MAKE_SITE_API = "https://make.wordpress.org/openverse/wp-json/wp/v2/"
  const token = Buffer.from(`${username}:${password}`).toString("base64")

  return axios.post(
    "posts",
    {
      title: `A week in Openverse: ${startDate} - ${endDate}`,
      slug: `last-week-openverse-${startDate}-${endDate}`,
      excerpt: `The developments in Openverse between ${startDate} and ${endDate}`,
      content: report,
      status: "publish",
      tags: [
        3, // openverse
        5, // week-in-openverse
      ],
    },
    {
      baseURL: MAKE_SITE_API,
      headers: {
        Authorization: `Basic ${token}`,
      },
    }
  )
}

// Entry point
const reportData = []
for (const repo of repos) {
  const closedIssues = (
    await octokit.rest.search.issuesAndPullRequests({ q: closedIssuesQ(repo) })
  ).data.items
  const mergedPrs = (
    await octokit.rest.search.issuesAndPullRequests({ q: mergedPrsQ(repo) })
  ).data.items
  if (closedIssues.length || mergedPrs.length)
    reportData.push({ repo, closedIssues, mergedPrs })
}

const res = await postActivities(reportData)
if (res.status !== 201) {
  console.error("Create post request failed. See the logs.")
  process.exitCode = 1
}
console.log(JSON.stringify(res.data, null, 2))
