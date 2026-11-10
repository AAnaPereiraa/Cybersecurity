import argparse
import os
from PIL import ExifTags, Image


SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")


def parse_arguments():
    parser = argparse.ArgumentParser(description="images")
    parser.add_argument(
        "files", 
        nargs="+", 
        help="Image files to inspect"
    )

    args = parser.parse_args()

    for filename in args.files.copy():
        if not filename.lower().endswith(SUPPORTED_EXTENSIONS):
            args.files.remove(filename)
        elif not os.path.isfile(filename):
            args.files.remove(filename)


    return args


def main():
    args = parse_arguments()

    if not args.files:
        print("No files to check")
        return

    for filename in args.files:
        try:
            with Image.open(filename) as image:
                print(f"File: {filename}")
                print(f"Format: {image.format}")
                print(f"Size: {image.size}")
                print(f"Mode: {image.mode}")

                exif_data = image.getexif()
                    
                if not exif_data:
                    print("No EXIF metadata found")
                else:
                    for tag_id, value in exif_data.items():
                        tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                        print(f"{tag_name}: {value}")

        except OSError as error:
            print(f"Skipping {filename}: {error}")


if __name__ == "__main__":
    main()