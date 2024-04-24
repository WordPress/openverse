# flake8: noqa
"""
Content Provider:       Thingiverse

ETL Process:            Use the API to identify all CC0 3D Models.

Output:                 TSV file containing the 3D models, their respective images and meta-data.

Notes:                  <https://www.thingiverse.com/developers/getting-started>
                        All API requests require authentication.
                        Rate limiting is 300 per 5 minute window.
"""

import argparse

from airflow.models import Variable
from modules.etlMods import *


MAX_THINGS = 30
LICENSE = "pd0"
TOKEN = Variable.get("API_KEY_THINGIVERSE", default_var=None)
DELAY = 5.0  # seconds
FILE = f"thingiverse_{int(time.time())}.tsv"


def requestBatchThings(_page):

    url = "https://api.thingiverse.com/newest?access_token={1}&per_page={2}&page={0}".format(
        _page, TOKEN, MAX_THINGS
    )

    result = requestContent(url)
    if result:
        return map(lambda x: x["id"], result)

    return None


def getMetaData(_thing, _date):

    url = f"https://api.thingiverse.com/things/{_thing}?access_token={TOKEN}"
    licenseText = "Creative Commons - Public Domain Dedication"
    license = None
    version = None
    creator = None
    creatorURL = None
    title = None
    foreignURL = None
    extracted = []

    logging.info(f"Processing thing: {_thing}")

    result = requestContent(url)
    if result:

        # verify the date
        modDate = result.get("modified", "")
        if modDate:
            modDate = modDate.split("T")[0].strip()
            if datetime.strptime(modDate, "%Y-%m-%d") < datetime.strptime(
                _date, "%Y-%m-%d"
            ):
                return "-1"

        startTime = time.time()

        # validate CC0 license
        if not (
            ("license" in result) and (licenseText.lower() in result["license"].lower())
        ):
            logging.warning(
                "License not detected => https://www.thingiverse.com/thing:{}".format(
                    _thing
                )
            )
            delayProcessing(startTime, DELAY)
            return None
        else:
            license = "CC0"
            version = "1.0"

        # get meta data

        # description of the work
        description = sanitizeString(result.get("description", ""))

        # title for the 3D model
        title = sanitizeString(result.get("name", ""))

        # the landing page
        if "public_url" in result:
            foreignURL = result["public_url"].strip()
        else:
            foreignURL = f"https://www.thingiverse.com/thing:{_thing}"

        # creator of the 3D model
        if "creator" in result:
            if ("first_name" in result["creator"]) and (
                "last_name" in result["creator"]
            ):
                creator = "{} {}".format(
                    sanitizeString(result["creator"]["first_name"]),
                    sanitizeString(result["creator"]["last_name"]),
                )

            if (creator.strip() == "") and ("name" in result["creator"]):
                creator = sanitizeString(result["creator"]["name"])

            if "public_url" in result["creator"]:
                creatorURL = result["creator"]["public_url"].strip()

        # get the tags
        delayProcessing(startTime, DELAY)
        logging.info(f"Requesting tags for thing: {_thing}")
        startTime = time.time()
        tags = requestContent(url.replace(_thing, f"{_thing}/tags"))
        tagsList = None

        if tags:
            tagsList = list(
                map(
                    lambda tag: {
                        "name": str(tag["name"].strip()),
                        "provider": "thingiverse",
                    },
                    tags,
                )
            )

        # get 3D models and their respective images
        delayProcessing(startTime, DELAY)
        logging.info(f"Requesting images for thing: {_thing}")

        imageList = requestContent(url.replace(_thing, f"{_thing}/files"))
        if imageList is None:
            logging.warning("Image Not Detected!")
            delayProcessing(startTime, DELAY)
            return None

        for img in imageList:
            metaData = {}
            thumbnail = None
            imageURL = None
            foreignID = None

            metaData["description"] = description

            if ("default_image" in img) and img["default_image"]:
                if "url" not in img["default_image"]:
                    logging.warning("3D Model Not Detected!")
                    continue

                metaData["3d_model"] = img["default_image"]["url"]
                foreignID = str(img["default_image"]["id"])
                images = img["default_image"]["sizes"]

                for imgSize in images:

                    if str(imgSize["type"]).strip().lower() == "display":

                        if str(imgSize["size"]).lower() == "medium":
                            thumbnail = imgSize["url"].strip()

                        if str(imgSize["size"]).lower() == "large":
                            imageURL = imgSize["url"].strip()

                        elif imageURL is None:
                            imageURL = thumbnail

                    else:
                        continue

                if imageURL is None:
                    logging.warning("Image Not Detected!")
                    continue

                extracted.append(
                    [
                        imageURL if not foreignID else foreignID,
                        foreignURL,
                        imageURL,
                        thumbnail,
                        "\\N",
                        "\\N",
                        "\\N",
                        license,
                        str(version),
                        creator,
                        creatorURL,
                        title,
                        "\\N" if not metaData else json.dumps(metaData),
                        "\\N" if not tagsList else json.dumps(tagsList),
                        "f",
                        "thingiverse",
                        "thingiverse",
                    ]
                )

        writeToFile(extracted, FILE)

        return len(extracted)


def execJob(_date):
    page = 1
    result = 0
    isValid = True
    tmpCtr = 0

    while isValid:  # temporary control flow

        batch = requestBatchThings(page)

        if batch:
            batch = list(batch)
            tmp = list(
                filter(
                    None, list(map(lambda thing: getMetaData(str(thing), _date), batch))
                )
            )

            if "-1" in tmp:
                isValid = False
                tmp = tmp.remove("-1")

            if tmp:
                tmpCtr = sum(tmp)

            result += tmpCtr
            tmpCtr = 0

        page += 1

    logging.info(f"Total CC0 3D Models: {result}")


def main():
    logging.info("Begin: Thingiverse API requests")
    param = None
    mode = "date: "

    parser = argparse.ArgumentParser(description="Thingiverse API Job", add_help=True)
    parser.add_argument(
        "--mode",
        choices=["default", "newest"],
        help="Identify all CC0 3D models from the previous day [default] or the current date [newest].",
    )

    args = parser.parse_args()
    if args.mode:

        if str(args.mode) == "newest":
            param = datetime.strftime(datetime.now(), "%Y-%m-%d")
        else:
            param = datetime.strftime(datetime.now() - timedelta(1), "%Y-%m-%d")

        mode += param if param is not None else ""
        logging.info(f"Processing {mode}")

        if param:
            execJob(param)

    logging.info("Terminated!")


if __name__ == "__main__":
    main()
