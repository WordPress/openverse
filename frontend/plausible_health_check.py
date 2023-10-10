import sys

import requests


def main():
    try:
        host = sys.argv[1]
        url = f"http://{host}/api/health/"
        resp = requests.get(url=url)

        information = resp.json()
        for data in information:
            if information[data] != "ok":
                return sys.stdout.write("false")
        return sys.stdout.write("true")
    except ConnectionError:
        pass


if __name__ == "__main__":
    main()
