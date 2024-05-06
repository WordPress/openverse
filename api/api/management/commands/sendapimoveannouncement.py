import argparse

from django.conf import settings
from django.core.mail import send_mail

import django_redis
from django_tqdm import BaseCommand

from api.models.oauth import OAuth2Verification


message = """
On 3 June 2024, the Openverse API’s domain will be changed to api.openverse.org and api.openverse.engineering will start
redirecting to api.openverse.org. Existing API credentials and all other aspects of integrations with the
Openverse API will continue to work without changes, provided requests follow redirects.

For the best experience, and to avoid redirects, please update code referencing api.openverse.engineering to use api.openverse.org.

To read more about this change, including opportunities to ask questions or give feedback, please read the Make Openverse blog post announcing it:

https://make.wordpress.org/openverse/2024/05/06/the-openverse-api-is-moving-to-api-openverse-org/

You are receiving this email because you’ve registered and verified with the Openverse API.

Openverse only sends emails for critical operational notifications.
"""


class Command(BaseCommand):
    help = "Resends verification emails for unverified Oauth applications."
    """
    This command sends a corrected oauth verification email to users who have
    not yet verified their Openverse oauth applications. A previous version sent
    an email with an incorrectly formatted link.

    It stores a cache of successfully sent emails in Redis, so running it multiple
    times (in case of failure) should not be an issue.
    """

    processed_key = "apimoveannouncement:processed"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry_run",
            help="Count the emails to send, and don't do anything else.",
            type=bool,
            default=True,
            action=argparse.BooleanOptionalAction,
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]

        redis = django_redis.get_redis_connection("default")

        sent_emails = [
            email.decode("utf-8") for email in redis.smembers(self.processed_key)
        ]

        # Join from verification because it has a reference to both the application and the email
        unsent_email_addresses = (
            OAuth2Verification.objects.filter(
                # Only send to verified email addresses to avoid bounce rate increase
                associated_application__verified=True
            )
            .exclude(
                email__in=sent_emails,
            )
            .distinct("email")
            .values_list("email", flat=True)
        )

        count_to_process = unsent_email_addresses.count()
        errored_emails = []

        if dry:
            self.info(
                f"{count_to_process} announcement emails to send. This is a dry run, exiting without making changes."
            )
            return

        if not count_to_process:
            self.info("No emails to send.")
            return

        with self.tqdm(total=count_to_process) as progress:
            while chunk := unsent_email_addresses.exclude(
                email__in=sent_emails + errored_emails
            )[:100]:
                for email in chunk:
                    try:
                        send_mail(
                            subject="Openverse API is moving to api.openverse.org",
                            message=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[email],
                            fail_silently=False,
                        )
                        sent_emails.append(email)
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

        self.info(self.style.SUCCESS("Sent API move notifications."))
