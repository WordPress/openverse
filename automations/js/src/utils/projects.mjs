import { getOctokit } from './octokit.mjs'

const PROJECT_NUMBERS = {
  Backlog: 75,
  PRs: 98,
  Todos: 59,
  Discussions: 79,
  'Project Tracker': 70,
}

class Project {
  /**
   * Create a new `Project` instance using owner name and project number, both
   * of which can be found in the project URL. For example,
   *
   * https://github.com/orgs/WordPress/projects/75/views/1
   *                         ^^^^^^^^^owner     ^^number
   *
   * @param octokit {import('octokit').Octokit} the Octokit instance to use
   * @param owner {string} the login of the owner (org) of the project
   * @param number {number} the number of the project
   */
  constructor(octokit, owner, number) {
    this.octokit = octokit

    this.owner = owner
    this.number = number
  }

  /**
   * Initialise the project and populate fields that require API call to GitHub.
   */
  async init() {
    const projectDetails = await this.getProjectDetails()
    this.projectId = projectDetails.projectId
    this.fields = projectDetails.fields
  }

  /**
   * Get a mapping of all options for the "Status" field against their slugified
   * names to easily access status choices without typing emojis.
   *
   * @returns {{[p: string]: string}} mapping of "Status" slugs to choices
   */
  get columns() {
    return Object.fromEntries(
      Object.keys(this.fields['Status'].options).map((key) => [
        key.replace(/\W/g, '').replace(/^\d*/, '').trim(),
        key,
      ])
    )
  }

  /**
   * Get additional information about the project such as node ID and custom
   * fields.
   *
   * This function currently only supports `ProjectV2SingleSelectField` because
   * that's all we currently have.
   *
   * @returns {Promise<ProjectDetails>} the ID of the project
   */
  async getProjectDetails() {
    const res = await this.octokit.graphql(
      `query getProjectId($login: String!, $number: Int!) {
        organization(login: $login) {
          projectV2(number: $number) {
            id
            fields(first: 20) {
              nodes {
                ... on ProjectV2SingleSelectField {
                  id
                  name
                  options {
                    id
                    name
                  }
                }
              }
            }
          }
        }
      }`,
      {
        login: this.owner,
        number: this.number,
      }
    )
    const project = res.organization.projectV2
    return {
      projectId: project.id,
      fields: Object.fromEntries(
        project.fields.nodes
          .filter((field) => field.options)
          .map((field) => [
            field.name,
            {
              id: field.id,
              options: Object.fromEntries(
                field.options.map((option) => [option.name, option.id])
              ),
            },
          ])
      ),
    }
  }

  /**
   * Add the issue or PR to the project. This takes the `node_id` of the issue
   * or PR as opposed to the conventional `id` or `number` fields.
   *
   * This function is also idempotent, so it can be used to get the card ID for
   * an existing card with no side effects.
   *
   * @param issueId {string} the ID of the issue/PR to add
   * @returns {Promise<{id: string, status: string}>} the info of the added card
   */
  async addCard(issueId) {
    const res = await this.octokit.graphql(
      `mutation addCard($projectId: ID!, $contentId: ID!) {
        addProjectV2ItemById(input: {
          projectId: $projectId,
          contentId: $contentId
        }) {
          item {
            id
            fieldValueByName(name: "Status") {
              ...on ProjectV2ItemFieldSingleSelectValue {
                name
              }
            }
          }
        }
      }`,
      {
        projectId: this.projectId,
        contentId: issueId,
      }
    )
    const card = res.addProjectV2ItemById.item
    return {
      id: card.id,
      status: card.fieldValueByName?.name, // `null` if new card
    }
  }

  /**
   * Set the value of the custom choice field to the given option.
   *
   * @param cardId {string} the ID of the card whose field is to be updated
   * @param fieldName {string} the name of the field to update
   * @param optionName {string} the updated value of the field
   * @returns {Promise<string>} the ID of the card that was updated
   */
  async setCustomChoiceField(cardId, fieldName, optionName) {
    // Preliminary validation
    if (!this.fields[fieldName]) {
      throw new Error(`Unknown field name "${fieldName}".`)
    }
    if (!this.fields[fieldName].options[optionName]) {
      throw new Error(
        `Unknown option name "${optionName}" for field "${fieldName}".`
      )
    }

    const res = await this.octokit.graphql(
      `mutation setCustomField($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
        updateProjectV2ItemFieldValue(input: {
          projectId: $projectId,
          itemId: $itemId,
          fieldId: $fieldId,
          value: {singleSelectOptionId: $optionId}
        }) {
          projectV2Item {
            id
          }
        }
      }`,
      {
        projectId: this.projectId,
        itemId: cardId,
        fieldId: this.fields[fieldName].id,
        optionId: this.fields[fieldName].options[optionName],
      }
    )
    return res.updateProjectV2ItemFieldValue.projectV2Item.id
  }

  /**
   * Moving a card to a different column is akin to updating the custom field
   * "Status" that is present on all GitHub project boards.
   *
   * @param cardId {string} the ID of the card to move
   * @param destColumn {string} the name of the column where to move it
   * @returns {Promise<string>} the ID of the card that was moved
   */
  async moveCard(cardId, destColumn) {
    return await this.setCustomChoiceField(cardId, 'Status', destColumn)
  }
}

/**
 * Get the `Project` instance for the project board with the given name.
 *
 * @param octokit {import('octokit').Octokit} the Octokit instance to use
 * @param name {string} the name of the project (without the 'Openverse' prefix)
 * @returns {Project} the `Project` instance to interact with the project board
 */
export async function getBoard(octokit, name) {
  const projectNumber = PROJECT_NUMBERS[name]
  if (!projectNumber) {
    throw new Error(`Unknown project board "${name}".`)
  }

  const project = new Project(octokit, 'WordPress', projectNumber)
  await project.init()
  return project
}
