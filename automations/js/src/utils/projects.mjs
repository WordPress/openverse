import { getOctokit } from './octokit.mjs'

class Project {
  constructor(octokit, owner, number) {
    this.octokit = octokit
    this.owner = owner
    this.number = number
  }

  /**
   * Initialise the project and populate fields that require API call to GitHub.
   */
  async init() {
    this.projectId = await this.getProjectId()
    this.fields = await this.getFields()
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
        key.replace(/\W/g, '').trim(),
        key,
      ])
    )
  }

  /**
   * Get the ID of the project from the owner name and project number. Both of
   * these fields can be found in the project URL. For example,
   *
   * https://github.com/orgs/WordPress/projects/75/views/1
   *                         ^^^^^^^^^owner     ^^number
   *
   * @returns {Promise<string>} the ID of the project
   */
  async getProjectId() {
    const res = await this.octokit.graphql(
      `query getProjectId($login: String!, $number: Int!) {
        organization(login: $login) {
          projectV2(number: $number) {
            id
          }
        }
      }`,
      {
        login: this.owner,
        number: this.number,
      }
    )
    return res.organization.projectV2.id
  }

  /**
   * Get a mapping of field names to field IDs defined for this project. This
   * function currently only supports `ProjectV2SingleSelectField` because
   * that's all we currently have.
   *
   * @returns {Promise<{[p: string]: string}>} a mapping of field names to IDs
   */
  async getFields() {
    const res = await this.octokit.graphql(
      `query getFields($projectId: ID!) {
        node(id: $projectId) {
          ... on ProjectV2 {
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
        projectId: this.projectId,
      }
    )
    let fields = {}
    for (let field of res.node.fields.nodes) {
      if (field.options) {
        fields[field.name] = {
          id: field.id,
          options: Object.fromEntries(
            field.options.map((option) => [option.name, option.id])
          ),
        }
      }
    }
    return fields
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
 * @param name {string} the name of the project (without the 'Openverse' prefix)
 * @returns {Project} the `Project` instance to interact with the project board
 */
export async function getBoard(name) {
  const octokit = getOctokit()

  let project
  switch (name) {
    case 'Backlog':
      project = new Project(octokit, 'WordPress', 75)
      break
    case 'PRs':
      project = new Project(octokit, 'WordPress', 98)
      break
    case 'Todos':
      project = new Project(octokit, 'WordPress', 59)
      break
    case 'Discussions':
      project = new Project(octokit, 'WordPress', 79)
      break
    case 'Project Tracker':
      project = new Project(octokit, 'WordPress', 70)
      break
    default:
      throw new Error(`Unknown project board "${name}".`)
  }
  await project.init()
  return project
}
