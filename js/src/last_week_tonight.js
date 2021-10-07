/**
 * Generate a weekly report of closed issues and merged PRs for each of the
 * Openverse repos.
 */

const fs = require('fs');
const path = require('path');

const yaml = require('js-yaml');
const fetch = require('node-fetch');
const {Octokit} = require('@octokit/rest');

/* Environment variables */

/** the personal access token for the GitHub API */
const pat = process.env.ACCESS_TOKEN;
/** the username for the Make site account making the post */
const username = process.env.MAKE_USERNAME;
/** the application password for the Make site */
const password = process.env.MAKE_PASSWORD;

if (!pat) console.log('GitHub personal access token "ACCESS_TOKEN" is required.')
if (!username) console.log('Make site username "MAKE_USERNAME" is required.')
if (!password) console.log('Make site application password "MAKE_PASSWORD" is required.')
if (!(pat && username && password)) process.exit(1)

/* Read GitHub information from the data files */

const githubDataFile = path.resolve(__dirname, '../../data/github.yml');
const githubInfo = yaml.load(fs.readFileSync(githubDataFile));
const org = githubInfo.org;
const repos = Object.values(githubInfo.repos);

/* Time period */

const msInWeeks = (weeks) => weeks * 7 * 24 * 60 * 60 * 1e3;
// End date is always today
const [endDate] = new Date()
    .toISOString()
    .split('T');
// Start date is one week before today
const [startDate] = new Date(new Date().getTime() - msInWeeks(1))
    .toISOString()
    .split('T');

/* GitHub API */

const octokit = new Octokit({auth: pat});
const mergedPrsQ = repo =>
    `repo:${org}/${repo} is:pr is:merged merged:>=${startDate}`;
const closedIssuesQ = repo =>
    `repo:${org}/${repo} is:issue is:closed closed:>=${startDate}`;

/* Format issues, PRs and repos as HTML */

/**
 * Generate the HTML for one closed issues or merged PRs section.
 * @param {string} title - the the title to use for the section
 * @param {{html_url: string, number: int, title: string}[]} items - the list of issues/PRs
 * @returns {string[]} - lines of HTML
 */
const getItemsHtml = (title, items) => {
    if (!items.length) return [];

    return [
        `<h3>${title}</h3>`,
        '<ul>',
        ...items.map(item =>
            `<li><a href="${item.html_url}">#${item.number}</a>: ${item.title}`,
        ),
        '</ul>',
    ];
};
/**
 * Generate the HTML for the closed issues or merged PRs of one repository.
 * @param {string} repo - the name of the repository
 * @param {{html_url: string, number: int, title: string}[]} mergedPrs - the list of PRs
 * @param {{html_url: string, number: int, title: string}[]} closedIssues - the list of issues
 * @returns {string[]} - lines of HTML
 */
const getRepoHtml = ({repo, mergedPrs, closedIssues}) => {
    return [
        `<h2><a href="https://github.com/${org}/${repo}">${repo}</a></h2>`,
        ...getItemsHtml('Merged PRs', mergedPrs),
        ...getItemsHtml('Closed issues', closedIssues),
    ]
};

// Create post on Make site
const MAKE_SITE_API = 'https://make.wordpress.org/openverse/wp-json/wp/v2';
const token = Buffer.from(`${username}:${password}`).toString('base64');
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
    const report = activities.map(getRepoHtml).flat().join('\n');
    return fetch(`${MAKE_SITE_API}/posts`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Basic ${token}`,
        },
        body: JSON.stringify({
            title: `A week in Openverse: ${startDate} - ${endDate}`,
            slug: `last-week-openverse-${startDate}-${endDate}`,
            excerpt: `The developments in Openverse between ${startDate} and ${endDate}`,
            content: report,
            status: 'draft',
            tags: [
                3, // openverse
                5, // week-in-openverse
            ],
        }),
    });
};

// Entry point
Promise.all(
    repos.map((repo) => Promise.all([
            octokit.rest.search.issuesAndPullRequests({q: closedIssuesQ(repo)})
                .then(res => res.data.items),
            octokit.rest.search.issuesAndPullRequests({q: mergedPrsQ(repo)})
                .then(res => res.data.items),
        ])
            .then(([closedIssues, mergedPrs]) => {
                if (closedIssues.length || mergedPrs.length) {
                    return {
                        repo: repo,
                        closedIssues,
                        mergedPrs,
                    };
                }
                return null;
            }),
    ),
)
    .then((activities) => activities.filter(activity => Boolean(activity)))
    .then(postActivities)
    .then(res => {
        if (res.status !== 201) {
            console.error('Create post request failed. See the logs.')
            process.exitCode = 1
        }
        return res.json()
    })
    .then(data => JSON.stringify(data, null, 2))
    .then(console.log)
