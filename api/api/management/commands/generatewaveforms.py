import subprocess

from django_tqdm import BaseCommand
from limit import limit

from api.models.audio import Audio, AudioAddOn


def paginate_reducing_query(get_query_set, page_size=10):
    """
    Iterate over the given query set yielding a specific number of entries each time.

    We can't use `Paginator` because it can't handle the situation
    where the query result changes each time a page is accessed.
    Because the `audios` QuerySet result is naturally getting smaller
    each time we successfully process waveforms, we can just take
    the first ten for each "page" until the page comes back empty.
    This should theoretically be faster/less DB latency inducing
    anyway as we're never going to have huge OFFSET values to
    access deep pages.
    """
    page = list(get_query_set()[0:page_size])
    while len(page):
        yield page
        page = list(get_query_set()[0:page_size])


class Command(BaseCommand):
    help = "Generates waveforms for all audio records to populate the cache."
    """
    Note: We rely on the file download and waveform generation times
    taking long enough to prevent us from either making too many requests
    to the upstream provider or inserting into our database too quickly and
    causing a slow down. In local tests and in tests run on the staging server
    it appeared to take on average around 6 to 8 seconds for each audio file.
    That should be enough latency to not cause any problems.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--no_rate_limit", help="Remove self impose rate limits for testing."
        )
        parser.add_argument(
            "--max_records", help="Limit the number of waveforms to create.", type=int
        )

    def get_audio_handler(self, options):
        if options["no_rate_limit"]:
            return lambda audio: audio.get_or_create_waveform()

        @limit(limit=1, every=2)  # Call once per two seconds maximum
        def limited(audio):
            audio.get_or_create_waveform()

        return limited

    def _process_wavelengths(self, audios, audio_handler, count_to_process):
        errored_identifiers = []
        processed = 0
        with self.tqdm(total=count_to_process) as progress:
            paginator = paginate_reducing_query(
                get_query_set=lambda: audios.exclude(identifier__in=errored_identifiers)
            )
            for page in paginator:
                for audio in page:
                    if processed > count_to_process:
                        return errored_identifiers
                    try:
                        processed += 1
                        audio_handler(audio)
                    except subprocess.CalledProcessError as err:
                        errored_identifiers.append(audio.identifier)
                        self.error(
                            f"Unable to process {audio.identifier}: "
                            f"{err.stderr.decode().strip()}"
                        )
                    except KeyboardInterrupt:
                        errored_identifiers.append(audio.identifier)
                        return errored_identifiers
                    except BaseException as err:
                        errored_identifiers.append(audio.identifier)
                        self.error(f"Unable to process {audio.identifier}: " f"{err}")
                    progress.update(1)

        return errored_identifiers

    def handle(self, *args, **options):
        existing_waveform_audio_identifiers_query = AudioAddOn.objects.filter(
            waveform_peaks__isnull=False
        ).values_list("audio_identifier", flat=True)
        audios = Audio.objects.exclude(
            identifier__in=existing_waveform_audio_identifiers_query
        ).order_by("id")

        max_records = options["max_records"]
        count = audios.count()

        count_to_process = count

        if max_records is not None:
            count_to_process = max_records if max_records < count else count

        self.info(
            self.style.NOTICE(f"Generating waveforms for {count_to_process:,} records")
        )

        audio_handler = self.get_audio_handler(options)

        errored_identifiers = self._process_wavelengths(
            audios, audio_handler, count_to_process
        )

        self.info(self.style.SUCCESS("Finished generating waveforms!"))

        if errored_identifiers:
            errored_identifiers_joined = "\n".join(
                str(identifier) for identifier in errored_identifiers
            )

            self.info(
                self.style.WARNING(
                    f"The following Audio identifiers were unable "
                    f"to be processed\n\n{errored_identifiers_joined}"
                )
            )
