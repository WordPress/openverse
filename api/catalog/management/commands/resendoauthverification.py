import argparse
from dataclasses import dataclass

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from rest_framework.reverse import reverse

from django_redis import get_redis_connection
from django_tqdm import BaseCommand

from catalog.api.models.oauth import (
    OAuth2Registration,
    OAuth2Verification,
    ThrottledApplication,
)


def get_input(text):
    """
    Wrapped ``input`` to allow patching in unittests
    """
    return input(text)


verification_msg_template = """
The Openverse API OAuth2 email verification process has recently been fixed.
We have detected that you attempted to register an application using this email.

To verify your Openverse API credentials, click on the following link:

{link}

If you believe you received this message in error, please disregard it.
"""


@dataclass
class Result:
    saved_application_name: str
    deleted_applications: int
    deleted_registrations: int
    deleted_verifications: int


class Command(BaseCommand):
    help = "Resends verification emails for unverified Oauth applications."
    """
    This command is meant to be used a single time in production to remediate
    failed email sending.

    It stores a cache of successfully sent emails in Redis, so running it multiple
    times (in case of failure) should not be an issue.
    """

    processed_key = "resendoauthverification:processed"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry_run",
            help="Count the records that will be removed but don't apply any changes.",
            type=bool,
            default=True,
            action=argparse.BooleanOptionalAction,
        )

    @transaction.atomic
    def _handle_email(self, email, dry):
        """
        1. Get all application IDs for the email
        2. Use the one with the lowest ID as the "original" attempt
        3. Delete the rest
        4. Delete OAuth2Registrations for the email not associated
            with the "original" application
        5. Delete OAuth2Verifications for the email not associated
            with the "original" application

        This ignores the fact that someone could have tried to register
        multiple unverified but distinct applications under the same email.
        This is unlikely given that none of the requests would have worked
        and that the "feature" isn't explicitly documented anyway.
        """
        application_ids = list(
            OAuth2Registration.objects.filter(email=email)
            .select_related("associated_application")
            .order_by("id")
            .values_list("pk", flat=True)
        )

        application_to_verify = ThrottledApplication.objects.get(pk=application_ids[0])

        deleted_applications = 0
        deleted_registrations = 0
        deleted_verifications = 0
        if len(application_ids) > 1:
            applications_to_delete_ids = application_ids[1:]
            deleted_applications = len(applications_to_delete_ids)
            if not dry:
                ThrottledApplication.objects.filter(
                    pk__in=applications_to_delete_ids
                ).delete()

            registrations_to_delete = OAuth2Registration.objects.filter(
                email=email
            ).exclude(name=application_to_verify.name)
            deleted_registrations = registrations_to_delete.count()
            if not dry:
                registrations_to_delete.delete()

            verifications_to_delete = OAuth2Verification.objects.filter(
                email=email
            ).exclude(associated_application=application_to_verify)
            deleted_verifications = verifications_to_delete.count()
            if not dry:
                verifications_to_delete.delete()

        if not dry:
            verification = OAuth2Verification.objects.get(
                associated_application=application_to_verify
            )
            token = verification.code
            # We don't have access to `request.build_absolute_uri` so we
            # have to build it ourselves for the production endpoint
            link = (
                f"https://api.openverse.engineering/{reverse('verify-email', [token])}"
            )
            verification_msg = verification_msg_template.format(link=link)
            send_mail(
                subject="Verify your API credentials",
                message=verification_msg,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[verification.email],
                fail_silently=False,
            )

        return Result(
            saved_application_name=application_to_verify.name,
            deleted_applications=deleted_applications,
            deleted_registrations=deleted_registrations,
            deleted_verifications=deleted_verifications,
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]
        if not dry:
            self.info(
                self.style.WARNING(
                    "This is NOT a dry run. Are you sure you wish to proceed? "
                    "Respond 'yes' in all uppercase to proceed.\n"
                )
            )
            if get_input(": ") != "YES":
                self.error("Exiting.")
                exit(1)

        redis = get_redis_connection("default")

        already_processed_emails = [
            email.decode("utf-8") for email in redis.smembers(self.processed_key)
        ]

        emails_with_verified_applications = OAuth2Verification.objects.filter(
            Q(associated_application__verified=True)
            | Q(email__in=already_processed_emails)
        ).values_list("email", flat=True)

        emails_with_zero_verified_applications = list(
            OAuth2Verification.objects.exclude(
                email__in=emails_with_verified_applications
            )
            .values_list("email", flat=True)
            .distinct()
        )

        count_to_process = len(emails_with_zero_verified_applications)
        results = []
        errored_emails = []

        with self.tqdm(total=count_to_process) as progress:
            for email in emails_with_zero_verified_applications:
                try:
                    results.append(self._handle_email(email, dry))
                    if not dry:
                        redis.sadd(self.processed_key, email)
                except BaseException as err:
                    errored_emails.append(email)
                    self.error(f"Unable to process {email}: " f"{err}")

                progress.update(1)

        if errored_emails:
            joined = "\n".join(errored_emails)
            self.info(
                self.style.WARNING(
                    f"The following emails were unable to be processed.\n\n"
                    f"{joined}"
                    "\n\nPlease check the output above for the error related"
                    "to each email."
                )
            )

        formatted_results = "\n\n".join(
            (
                f"Application name: {result.saved_application_name}\n"
                f"Cleaned related application count: {result.deleted_applications}\n"
                f"Cleaned related verification count: {result.deleted_verifications}\n"
                f"Cleaned related registration count: {result.deleted_registrations}\n"
            )
            for result in results
        )

        self.info(
            self.style.SUCCESS(
                f"The following applications had email verifications sent.\n\n"
                f"{formatted_results}"
            )
        )

        if dry:
            self.info(
                self.style.WARNING(
                    "The above was a dry run and no records were actually affected."
                )
            )
