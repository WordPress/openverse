import { readFileSync } from 'fs'

import { getBoard } from '../utils/projects.mjs'
import { PullRequest } from '../utils/pr.mjs'

/**
 * Move the PR to the right column based on the number of reviews.
 *
 * @param pr {PullRequest}
 * @param prBoard {Project}
 * @param prCard {Card}
 */
async function syncReviews(pr, prBoard, prCard) {
  console.log("::debug::Synchronizing reviews for PR:", pr.nodeId);
  const reviewDecision = pr.reviewDecision;
  console.log("::debug::Review decision:", reviewDecision);

  if (reviewDecision === 'APPROVED') {
    console.log("::debug::Moving PR to 'Approved'");
    await prBoard.moveCard(prCard.id, prBoard.columns.Approved);
  } else if (reviewDecision === 'CHANGES_REQUESTED') {
    console.log("::debug::Changes requested for PR. Moving to 'ChangesRequested'");
    await prBoard.moveCard(prCard.id, prBoard.columns.ChangesRequested);
  } else if (pr.reviewCounts.APPROVED === 1) {
    console.log("::debug::PR needs 1 more review. Moving to 'Needs1Review'");
    await prBoard.moveCard(prCard.id, prBoard.columns.Needs1Review);
  } else {
    console.log("::debug::PR needs 2 more reviews. Moving to 'Needs2Reviews'");
    await prBoard.moveCard(prCard.id, prBoard.columns.Needs2Reviews);
  }
}

/**
 * Move all linked issues to the specified column.
 *
 * @param pr {PullRequest}
 * @param backlogBoard {Project}
 * @param destColumn {string}
 */
async function syncIssues(pr, backlogBoard, destColumn) {
  console.log("::debug::Synchronizing linked issues for PR:", pr.nodeId);
  for (let linkedIssue of pr.linkedIssues) {
    console.log("::debug::Processing linked issue:", linkedIssue);
    const issueCard = await backlogBoard.addCard(linkedIssue);
    console.log("::debug::Moving linked issue to column:", destColumn);
    await backlogBoard.moveCard(issueCard.id, backlogBoard.columns[destColumn]);
  }
}

/**
 * This is the entrypoint of the script.
 *
 * @param octokit {import('@octokit/rest').Octokit} the Octokit instance to use
 */
export const main = async (octokit) => {
  console.log("::debug::Starting PR script");

  const { eventName, eventAction, prNodeId } = JSON.parse(
    readFileSync('/tmp/event.json', 'utf-8')
  );
  console.log("::debug::Event details - Name:", eventName, ", Action:", eventAction, ", PR Node ID:", prNodeId);

  const pr = new PullRequest(octokit, prNodeId);
  await pr.init();

  const prBoard = await getBoard(octokit, 'PRs');
  const backlogBoard = await getBoard(octokit, 'Backlog');

  const prCard = await prBoard.addCard(pr.nodeId);
  console.log("::debug::PR card created or fetched:", prCard.id);

  if (eventName === 'pull_request_review') {
    await syncReviews(pr, prBoard, prCard);
  } else {
    switch (eventAction) {
      case 'opened':
      case 'reopened': {
        console.log("::debug::PR opened or reopened");
        if (pr.isDraft) {
          console.log("::debug::PR is a draft. Moving to 'Draft'");
          await prBoard.moveCard(prCard.id, prBoard.columns.Draft);
        } else {
          await syncReviews(pr, prBoard, prCard);
        }
        await syncIssues(pr, backlogBoard, 'InProgress');
        break;
      }
      case 'edited': {
        console.log("::debug::PR edited");
        await syncIssues(pr, backlogBoard, 'InProgress');
        break;
      }
      case 'converted_to_draft': {
        console.log("::debug::PR converted to draft");
        await prBoard.moveCard(prCard.id, prBoard.columns.Draft);
        break;
      }
      case 'ready_for_review': {
        console.log("::debug::PR ready for review");
        await syncReviews(pr, prBoard, prCard);
        break;
      }
      case 'closed': {
        console.log("::debug::PR closed");
        if (!pr.isMerged) {
          console.log("::debug::PR not merged. Moving linked issues to 'Backlog'");
          await syncIssues(pr, backlogBoard, 'Backlog');
        }
        break;
      }
    }
  }
}
