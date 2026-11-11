import argparse
import os
from PIL import ExifTags, Image, TiffImagePlugin


SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")


def tag_name(tag_id, tags):
    return tags.get(tag_id, tag_id)


def format_value(value):
    if isinstance(value, bytes):
        try:
            decoded = value.decode("utf-8").replace("\x00", "").rstrip()
            if any(ord(character) < 32 and character not in "\t\n\r" for character in decoded):
                return f"<binary data: {len(value)} bytes>"
            return decoded
        except UnicodeDecodeError:
            return f"<binary data: {len(value)} bytes>"
    if isinstance(value, TiffImagePlugin.IFDRational):
        return str(float(value))
    if isinstance(value, tuple):
        return ", ".join(format_value(item) for item in value)
    if isinstance(value, dict):
        return ", ".join(
            f"{format_value(key)}={format_value(item)}"
            for key, item in value.items()
        )
    return str(value).replace("\x00", "").rstrip()


def print_ifd(title, ifd, tags):
    print(f"{title}:")
    for tag_id, value in ifd.items():
        print(f"  {tag_name(tag_id, tags)}: {format_value(value)}")


def gps_coordinate(gps, value_tag, reference_tag):
    values = gps.get(value_tag)
    reference = gps.get(reference_tag)
    if not values or not reference:
        return None

    degrees, minutes, seconds = (float(value) for value in values)
    coordinate = degrees + minutes / 60 + seconds / 3600
    if format_value(reference).upper() in ("S", "W"):
        coordinate = -coordinate
    return coordinate


def print_metadata(image):
    exif_data = image.getexif()
    if not exif_data:
        print("No EXIF metadata found")
    else:
        print_ifd("EXIF", exif_data, ExifTags.TAGS)

        gps_data = exif_data.get_ifd(ExifTags.IFD.GPSInfo)
        if gps_data:
            print_ifd("GPS", gps_data, ExifTags.GPSTAGS)
            latitude = gps_coordinate(
                gps_data, ExifTags.GPS.GPSLatitude, ExifTags.GPS.GPSLatitudeRef
            )
            longitude = gps_coordinate(
                gps_data, ExifTags.GPS.GPSLongitude, ExifTags.GPS.GPSLongitudeRef
            )
            if latitude is not None and longitude is not None:
                print(f"  Coordinates: {latitude:.6f}, {longitude:.6f}")

        for ifd_id, title, tags in (
            (ExifTags.IFD.Exif, "EXIF subdirectory", ExifTags.TAGS),
            (ExifTags.IFD.Interop, "Interop subdirectory", ExifTags.TAGS),
            (ExifTags.IFD.MakerNote, "MakerNote", ExifTags.TAGS),
        ):
            try:
                subdirectory = exif_data.get_ifd(ifd_id)
            except KeyError:
                continue
            if subdirectory:
                print_ifd(title, subdirectory, tags)

    for key, value in image.info.items():
        if key == "exif":
            continue
        print(f"{key}: {format_value(value)}")


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

                print_metadata(image)

        except OSError as error:
            print(f"Skipping {filename}: {error}")


if __name__ == "__main__":
    main()