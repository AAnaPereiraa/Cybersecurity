import argparse
import os
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests


def parse_arguments():
    parser = argparse.ArgumentParser(description="Download images from a website")

    parser.add_argument(
        "-r",
        dest="recursive",
        action="store_true",
        help="Recursive crawl linked pages"
    )

    parser.add_argument(
        "-l",
        dest="level",
        type=int,
        default=5,
        help="Maximum recursion depth, default = 5"
    )

    parser.add_argument(
        "-p",
        dest="path",
        default="./data",
        help="Directory where images are saved, default = ./data"
    )

    parser.add_argument(
        "url",
        help="Website URL"
    )

    args = parser.parse_args()
    if args.level < 0:
        parser.error("recursion level cannot be negative")

    parsed_url = urlparse(args.url)
    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        parser.error("URL must use http or https")

    return args


SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")


class ImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.links = []

    def handle_starttag(self, tag, attrs):

        for name, value in attrs:
            if tag == "img" and name == "src" and value:
                image_url = value.lower().split("?")[0]
                if image_url.endswith(SUPPORTED_EXTENSIONS):
                    self.images.append(value)
            
            elif tag == "link" and name == "href" and value:
                image_url = value.lower().split("?")[0]
                if image_url.endswith(SUPPORTED_EXTENSIONS):
                    self.images.append(value)

            elif tag == "a" and name == "href" and value:
                self.links.append(value)


def crawl(url, depth, max_depth, path, visited, allowed_domain):

    if url in visited:
        return

    visited.add(url)

    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as error:
        print(f"Skipping {url}: {error}")
        return

    if response.status_code != 200:
        print(f"Skipping {url}: HTTP {response.status_code}")
        return

    image = ImageParser()
    image.feed(response.text)

    for image_url in image.images:
        full_url = urljoin(url, image_url)
        parsed_image_url = urlparse(full_url)

        if parsed_image_url.scheme not in ("http", "https"):
            continue

        if parsed_image_url.hostname != allowed_domain:
            continue

        save_image(full_url, path)

    if depth >= max_depth:
        return

    for link in image.links:
        next_url = urljoin(url, link)
        parsed_url = urlparse(next_url)

        if parsed_url.scheme not in ("http", "https"):
            continue

        if parsed_url.hostname != allowed_domain:
            continue
        crawl(next_url, depth + 1, max_depth, path, visited, allowed_domain)


def save_image(image_url, path):
    os.makedirs(path, exist_ok=True)

    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Skipping image {image_url}: {error}")
        return

    filename = image_url.split("/")[-1].split("?")[0]
    destination = os.path.join(path, filename)

    counter = 1
    while os.path.exists(destination):
        name, extension = os.path.splitext(filename)
        destination = os.path.join(path, f"{name}_{counter}{extension}")
        counter += 1

    with open(destination, "wb") as file:
        file.write(response.content)


def main():
    args = parse_arguments()

    if args.recursive:
        visited = set()
        allowed_domain = urlparse(args.url).hostname
        crawl(args.url, 0, args.level, args.path, visited, allowed_domain)
        return

    try:
        response = requests.get(args.url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Skipping {args.url}: {error}")
        return

    image = ImageParser()
    image.feed(response.text)

    for image_url in image.images:
        full_url = urljoin(args.url, image_url)
        save_image(full_url, args.path)


if __name__ == "__main__":
    main()