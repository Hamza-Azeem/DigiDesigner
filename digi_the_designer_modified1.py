
import sys

if len(sys.argv) != 3:
    print("Usage: python script_name.py <image_path> <user_prompt>")
    sys.exit(1)

image_path = sys.argv[1]
user_prompt = sys.argv[2]
# -*- coding: utf-8 -*-
"""Digi the designer (final1).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1xhgByK4h6Uk0pAFhj8XNJaotHu2xRVct
"""

# final
import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import nltk
from nltk.corpus import stopwords
from sklearn.metrics import pairwise_distances_argmin_min

# Ensure you have the required NLTK resources (run this once)
nltk.download('stopwords')

color_names = {
    'brown': (153, 101, 21),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'gray': (169, 169, 169),
    'orange': (255, 165, 0),  # Added orange
    'purple': (128, 0, 128),  # Added purple
    'pink': (255, 192, 203),  # Added pink
    'cyan': (0, 255, 255),  # Added cyan
    'magenta': (255, 0, 255),  # Added magenta
    'lime': (0, 255, 0),  # Added lime (same as green, but more vivid)
    'turquoise': (64, 224, 208),  # Added turquoise
    'teal': (0, 128, 128),  # Added teal
    'indigo': (75, 0, 130),  # Added indigo
    'violet': (238, 130, 238),  # Added violet
    'beige': (245, 245, 220),  # Added beige
    'maroon': (128, 0, 0),  # Added maroon
    'olive': (128, 128, 0),  # Added olive
}


def round_corners(image, radius, background_color):
    # Get the dimensions of the image
    height, width = image.shape[:2]

    # Create a mask with the same size as the image (all black)
    mask = np.zeros((height, width), dtype=np.uint8)

    # Create rounded corners by filling an ellipse into each corner of the mask
    cv2.ellipse(mask, (radius, radius), (radius, radius), 180, 0, 90, 255, -1)  # Top-left corner
    cv2.ellipse(mask, (width - radius, radius), (radius, radius), 270, 0, 90, 255, -1)  # Top-right corner
    cv2.ellipse(mask, (radius, height - radius), (radius, radius), 90, 0, 90, 255, -1)  # Bottom-left corner
    cv2.ellipse(mask, (width - radius, height - radius), (radius, radius), 0, 0, 90, 255, -1)  # Bottom-right corner
    # Fill the remaining area of the rectangle
    cv2.rectangle(mask, (radius, 0), (width - radius, height), 255, thickness=-1)  # Top rectangle
    cv2.rectangle(mask, (0, radius), (width, height - radius), 255, thickness=-1)  # Left rectangle

    # Apply the mask to the image using bitwise_and
    rounded_image = cv2.bitwise_and(image, image, mask=mask)

    # Create an image of the same size for transparent areas, with the detected background color
    rounded_image_with_background = np.ones_like(image) * background_color
    rounded_image_with_background[mask == 255] = rounded_image[mask == 255]

    return rounded_image_with_background

def extract_color_from_prompt(prompt):
    """
    Extract the color name from the user's prompt.
    This is a simple implementation using basic color names.
    More advanced NLP techniques could be used for better extraction.
    """
    # Convert the prompt to lowercase and tokenize
    words = prompt.lower().split()

    # Filter out stopwords (like 'the', 'is', 'a', etc.)
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]

    # Check if any color name exists in the words
    for word in words:
        if word in color_names:
            return color_names[word]
    return None  # If no color is found

def calculate_average_color(image):
    """
    Calculate the average color of an image.
    """
    # Convert image to the RGB space (if it is in BGR)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Calculate the average color
    avg_color = np.mean(image_rgb, axis=(0, 1)).astype(int)
    return avg_color

def find_closest_design(color, output_folder):
    """
    Compare the user's desired color with the colors of the generated designs and display the closest match.
    """
    # Get all image files from the output folder
    output_files = [f for f in os.listdir(output_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

    # Loop through the generated designs and compare average colors
    closest_image = None
    closest_distance = float('inf')

    for output_file in output_files:
        # Load the generated image
        image_path = os.path.join(output_folder, output_file)
        image = cv2.imread(image_path)
        if image is None:
            continue

        # Calculate the average color of the image
        avg_color = calculate_average_color(image)

        # Calculate the color distance (Euclidean distance between RGB values)
        distance = np.linalg.norm(np.array(color) - np.array(avg_color))

        # Update the closest image if this one is a better match
        if distance < closest_distance:
            closest_distance = distance
            closest_image = image

    return closest_image

# Path to the templates folder
templates_folder = r"D:\study\backend\templates"

# Get all image file names in the templates folder
template_paths = [os.path.join(templates_folder, f) for f in os.listdir(templates_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

# Load all template images
templates = []
for template_path in template_paths:
    template = cv2.imread(template_path)
    if template is None:
        print(f"Error: Unable to load the image at {template_path}. Please check the file path and format.")
        continue
    templates.append(template)  # Add template to templates list

# Load the product image
product_image_path = image_path
product_image = cv2.imread(product_image_path)
if product_image is None:
    raise FileNotFoundError('Image could not be loaded')

# Iterate over each template and apply the product image
for idx, template in enumerate(templates):
    # Detect the background color by analyzing a region of the template
    # For simplicity, we take the top-left corner's color as the background color for each template
    background_color = np.mean(template[:50, :50], axis=(0, 1)).astype(int)  # Average color of top-left 50x50 region

    # Convert template to grayscale and find edges
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray_template, 100, 200)

    # Find contours in the template
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize portrait size and area
    portrait_size = None
    portrait_area = None
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 100 and h > 200:  # Check for suitable size
            portrait_size = (w, h)
            portrait_area = (x, y, x + w, y + h)  # Define the rectangular area

    # Resize the product image to match the portrait size
    resized_image = cv2.resize(product_image, portrait_size)

    # Apply rounded corners to the resized image
    radius = 50  # Adjust the radius of the rounded corners
    rounded_product_image = round_corners(resized_image, radius, background_color)

    # Get the area where the image will be inserted into the template
    x1, y1, x2, y2 = portrait_area

    # Create a region of interest (ROI) from the template where the image will be inserted
    template_roi = template[y1:y2, x1:x2]

    # Apply the rounded corners image into the region of interest
    rounded_product_image_resized = cv2.resize(rounded_product_image, (x2 - x1, y2 - y1))
    template[y1:y2, x1:x2] = rounded_product_image_resized

    # Save the result for this template
    output_path = f"D:\\study\\backend\\output\\final_result_{idx + 1}.png"  # Specify the output path for each template
    cv2.imwrite(output_path, template)  # Save the final result

# Main part of the code for generating designs
output_folder = r"D:\study\backend\output"
user_prompt = user_prompt

# Step 1: Extract the color from the prompt
desired_color = extract_color_from_prompt(user_prompt)

if desired_color is None:
    print("Sorry, we couldn't identify a color in the prompt.")
else:
    print(f"Desired color: {desired_color}")

    # Step 2: Find the closest design based on the average color
    closest_design = find_closest_design(desired_color, output_folder)

    if closest_design is not None:
        # Step 3: Save the closest design in the prompt_output folder
        prompt_output_folder = r"D:\study\backend\prompt_output"

        # Ensure the prompt_output folder exists
        os.makedirs(prompt_output_folder, exist_ok=True)

        output_path = os.path.join(prompt_output_folder, 'closest_design.png')
        cv2.imwrite(output_path, closest_design)
        print(f"Closest design saved at {output_path}")
    else:
        print("No suitable design found.")