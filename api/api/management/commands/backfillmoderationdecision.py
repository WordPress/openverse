import argparse

from django.contrib.auth import get_user_model

from django_tqdm import BaseCommand

from api.constants.moderation import DecisionAction
from api.models import AudioDecision, AudioReport, ImageDecision, ImageReport
from api.models.media import DMCA, MATURE_FILTERED, NO_ACTION, PENDING


class Command(BaseCommand):
    help = "Back-fill the moderation decision table for a given media type."
    batch_size = 3

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            "--dry-run",
            help="Count reports to process, and don't do anything else.",
            type=bool,
            default=True,
            action=argparse.BooleanOptionalAction,
        )
        parser.add_argument(
            "--media-type",
            help="The media type to back-fill moderation decisions.",
            type=str,
            default="image",
            choices=["image", "audio"],
        )
        parser.add_argument(
            "--moderator",
            help="The username of the moderator to attribute the decisions to.",
            type=str,
            default="opener",
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]
        username = options["moderator"]
        media_type = options["media_type"]

        MediaReport = ImageReport
        MediaDecision = ImageDecision
        if media_type == "audio":
            MediaReport = AudioReport
            MediaDecision = AudioDecision

        non_pending_reports = MediaReport.objects.filter(decision=None).exclude(
            status=PENDING
        )
        count_to_process = non_pending_reports.count()

        if dry:
            self.info(
                f"{count_to_process} {media_type} reports to back-fill. "
                f"This is a dry run, exiting without making changes."
            )
            return

        if not count_to_process:
            self.info("No reports to process.")
            return

        t = self.tqdm(total=count_to_process // self.batch_size)
        User = get_user_model()
        try:
            moderator = User.objects.get(username=username)
        except User.DoesNotExist:
            t.error(f"User '{username}' not found.")
            return

        while reports_chunk := non_pending_reports[: self.batch_size]:
            decisions = MediaDecision.objects.bulk_create(
                MediaDecision(
                    action=self.get_action(report),
                    moderator=moderator,
                    notes="__backfilled_from_report_status",
                )
                for report in reports_chunk
            )
            for report, decision in zip(reports_chunk, decisions):
                report.decision = decision
            MediaReport.objects.bulk_update(reports_chunk, ["decision"])
            t.update(1)

        t.info(
            self.style.SUCCESS(
                f"Created {count_to_process} {media_type} moderation decisions from existing reports."
            )
        )

    @staticmethod
    def get_action(report):
        if report.status == MATURE_FILTERED:
            return DecisionAction.MARKED_SENSITIVE

        if report.status == NO_ACTION:
            return DecisionAction.REJECTED_REPORTS

        # Cases with status = DEINDEXED
        if report.reason == DMCA:
            return DecisionAction.DEINDEXED_COPYRIGHT

        return DecisionAction.DEINDEXED_SENSITIVE  # For reasons MATURE and OTHER
