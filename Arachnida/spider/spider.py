import argparse
import requests
from html.parser import HTMLParser
from urllib.parse import urljoin

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

def main():
    args = parse_arguments()
    response = requests.get(args.url, timeout=10)
    response.raise_for_status()
    image = ImageParser()
    image.feed(response.text)

    for image_url in image.images:
        full_url = urljoin(args.url, image_url)
        print(full_url)


if __name__ == "__main__":
    main()