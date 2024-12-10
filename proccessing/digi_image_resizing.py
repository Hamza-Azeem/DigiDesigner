from PIL import Image
import os
import argparse

def resize_and_crop_image(image, target_size=(1080, 1080)):
    img_width, img_height = image.size
    target_width, target_height = target_size
    img_aspect = img_width / img_height
    target_aspect = target_width / target_height

    # Resize image while maintaining aspect ratio
    if img_aspect > target_aspect:
        new_width = target_width
        new_height = int(new_width / img_aspect)
    else:
        new_height = target_height
        new_width = int(new_height * img_aspect)

    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    # Crop to target size
    left = (new_width - target_width) / 2
    top = (new_height - target_height) / 2
    right = (new_width + target_width) / 2
    bottom = (new_height + target_height) / 2

    cropped_image = resized_image.crop((left, top, right, bottom))

    return cropped_image

def process_single_image(input_path, output_path, target_size=(1080, 1080)):
    try:
        with Image.open(input_path) as img:
            img_resized = resize_and_crop_image(img, target_size)
            img_resized.save(output_path)
            print(f'Image processed and saved to: {output_path}')
    except Exception as e:
        print(f'Error processing image: {e}')
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resize and crop an image to 1:1 aspect ratio.")
    parser.add_argument("--input_path", required=True, help="Path to the input image file.")
    parser.add_argument("--output_path", required=True, help="Path to save the processed image.")

    args = parser.parse_args()

    try:
        process_single_image(args.input_path, args.output_path)
    except Exception as e:
        print({"error": str(e)})
        exit(1)
