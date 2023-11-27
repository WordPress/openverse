import { getBoard } from '../utils/projects.mjs'

/**
 * Set the "Priority" custom field based on the issue's labels. Also move
 * the card for critical issues directly to the "📅 To Do" column.
 *
 * @param issue {import('@octokit/rest')}
 * @param board {import('../utils/projects.mjs').Project}
 * @param card {import('../utils/projects.mjs').Card}
 */
async function syncPriority(issue, board, card) {
  console.log("::debug::Starting syncPriority for issue:", issue.number);
  const priority = issue.labels.find((label) => label.name.includes('priority'))?.name;

  if (priority) {
    console.log("::debug::Setting priority:", priority, "for card:", card.id);
    await board.setCustomChoiceField(card.id, 'Priority', priority);
    console.log("::debug::Priority set for card:", card.id);
  }
  if (priority === '🟥 priority: critical') {
    console.log("::debug::Moving card to 'To Do' for critical priority issue");
    await board.moveCard(card.id, board.columns.ToDo);
    console.log("::debug::Card moved to 'To Do' column");
  }
}

/**
 * This is the entrypoint of the script.
 *
 * @param octokit {import('@octokit/rest').Octokit} the Octokit instance to use
 * @param context {import('@actions/github').context} info about the current event
 */
export const main = async (octokit, context) => {
  const { EVENT_ACTION: eventAction } = process.env;
  console.log("::debug::Event action received:", eventAction);

  const issue = context.payload.issue;
  const label = context.payload.label;
  console.log("::debug::Issue details:", issue);

  if (issue.labels.some((label) => label.name === '🧭 project: thread')) {
    console.log("::debug::Issue is a project thread. Exiting.");
    process.exit(0);
  }

  const backlogBoard = await getBoard(octokit, 'Backlog');
  console.log("::debug::Backlog board fetched");

  const card = await backlogBoard.addCard(issue.node_id);
  console.log("::debug::Card created or fetched for the issue:", card.id);

  switch (eventAction) {
    case 'opened':
    case 'reopened': {
      console.log("::debug::Issue opened or reopened");
      if (issue.labels.some((label) => label.name === '⛔ status: blocked')) {
        console.log("::debug::Issue is blocked. Moving card to 'Blocked' column");
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Blocked);
      } else {
        console.log("::debug::Moving card to 'Backlog'");
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Backlog);
      }
      await syncPriority(issue, backlogBoard, card);
      break;
    }
    case 'closed': {
      console.log("::debug::Issue closed");
      if (issue.state_reason === 'completed') {
        console.log("::debug::Issue completed. Moving card to 'Done'");
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Done);
      } else {
        console.log("::debug::Issue not completed. Moving card to 'Discarded'");
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Discarded);
      }
      break;
    }
    case 'assigned': {
      console.log("::debug::Issue assigned");
      if (card.status === backlogBoard.columns.Backlog) {
        console.log("::debug::Moving card to 'To Do'");
        await backlogBoard.moveCard(card.id, backlogBoard.columns.ToDo);
      }
      break;
    }
    case 'labeled': {
      console.log("::debug::Issue labeled:", label.name);
      if (label.name === '⛔ status: blocked') {
        console.log("::debug::Issue is blocked. Moving card to 'Blocked' column");
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Blocked);
      }
      await syncPriority(issue, backlogBoard, card);
      break;
    }
    case 'unlabeled': {
      console.log("::debug::Label removed:", label.name);
      if (label.name === '⛔ status: blocked') {
        console.log("::debug::'Blocked' label removed. Moving card to 'Backlog'");
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Backlog);
      }
      await syncPriority(issue, backlogBoard, card);
      break;
    }
  }
}
