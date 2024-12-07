# -*- coding: utf-8 -*-
"""digi the writer2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rTZ9BYZlI07S4ktFlTj85O7euplrI-tp
"""

import spacy
import pandas as pd
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from textblob import TextBlob
import textstat  # For readability scores
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # For emotion detection

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

# Paths to datasets
main_dataset_path = r"D:\digi the writer\fashion_maxi_ads_with_offer.csv"  # Adjust to your dataset path
fallback_dataset_path = r"D:\digi the writer\fashion_maxi_ads.csv"  # Fallback dataset path

# Load the initial dataset with ad copies
ads = pd.read_csv(main_dataset_path)

def extract_details_with_nlp(prompt):
    """
    Extracts product name and offer percentage from the given prompt using NLP.
    """
    doc = nlp(prompt)
    product_name = None
    offer_amount = None
    offer_percentage = None

    # Extract named entities
    for ent in doc.ents:
        if ent.text:  # Ensure the entity text is not None or empty
            if "product" in ent.text.lower():
                # Safely split the entity text
                try:
                    product_name = ent.text.split()[-1]  # Extract name after "called" or "product"
                except Exception as e:
                    print(f"Error splitting entity text: {ent.text}. Error: {e}")
            elif ent.label_ == "MONEY":  # For monetary offers like "$30"
                offer_amount = ent.text.strip("$")
            elif "%" in ent.text:  # For percentage offers
                offer_percentage = ent.text.strip("%")

    # Look for fallback if entities are missing
    if not product_name:
        for token in doc:
            if token.text.lower() == "called":
                product_name = token.nbor(1).text  # Get the token after "called"
                break

    # Defaults if not found
    product_name = product_name or "Maxi"  # Default product name set to "Maxi"
    offer_amount = offer_amount or "50"  # Default offer amount
    offer_percentage = offer_percentage or "50"  # Default percentage offer

    return product_name, offer_amount, offer_percentage

def sentiment_analysis(text):
    """
    Returns sentiment polarity of the text.
    """
    analysis = TextBlob(text)
    return analysis.sentiment.polarity  # Returns a value between -1 (negative) and 1 (positive)

def emotion_detection(text):
    """
    Detects the emotion in the text and returns it.
    """
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)

    # Classifying sentiment scores into emotions
    if sentiment['compound'] >= 0.05:
        return "Happy"
    elif sentiment['compound'] <= -0.05:
        return "Angry"
    else:
        return "Neutral"

def readability_scores(text):
    """
    Returns Flesch-Kincaid readability scores of the text.
    """
    fk_score = textstat.flesch_kincaid_grade(text)
    return fk_score

def extract_text_features(ads, vectorizer=None):
    """
    Extracts various text-based features from the ad copy for clustering.
    """
    # Feature 1: Ad Copy Length
    ads['length'] = ads['copy'].apply(lambda x: len(x.split()))

    # Feature 2: Sentiment of the ad copy
    ads['sentiment'] = ads['copy'].apply(sentiment_analysis)

    # Feature 3: Emotion of the ad copy
    ads['emotion'] = ads['copy'].apply(emotion_detection)

    # Feature 4: Readability Score (Flesch-Kincaid)
    ads['readability'] = ads['copy'].apply(readability_scores)

    # Feature 5: Tfidf-based vectorization of the ad copy
    if vectorizer is None:
        vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(ads['copy'])
    return ads, X, vectorizer

def cluster_ads_by_features(ads, X, n_clusters=5):
    """
    Clusters ads based on text features using KMeans.
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(X)

    ads['cluster'] = kmeans.labels_

    # Cluster centers (average features for each cluster)
    cluster_centers = kmeans.cluster_centers_

    # Assigning meaningful labels based on cluster centers
    cluster_labels = []
    for center in cluster_centers:
        sentiment_mean = center[ads.columns.get_loc('sentiment')]
        length_mean = center[ads.columns.get_loc('length')]
        readability_mean = center[ads.columns.get_loc('readability')]

        if sentiment_mean > 0.1:
            sentiment_label = "Positive Tone"
        elif sentiment_mean < -0.1:
            sentiment_label = "Negative Tone"
        else:
            sentiment_label = "Neutral Tone"

        if length_mean > 15:
            length_label = "Long Ads"
        else:
            length_label = "Short Ads"

        if readability_mean > 8:
            readability_label = "Easy to Read"
        else:
            readability_label = "Hard to Read"

        cluster_labels.append(f"{sentiment_label}, {length_label}, {readability_label}")

    ads['cluster_description'] = ads['cluster'].apply(lambda x: cluster_labels[x])
    return ads, kmeans, vectorizer

def generate_custom_ad(ads, vectorizer, kmeans, prompt):
    """
    Generates a customized ad copy based on the extracted product name and offer percentage,
    and predicts the cluster for the generated ad.
    """
    # Extract product name and offer details from the user prompt
    product_name, offer_amount, offer_percentage = extract_details_with_nlp(prompt)

    # Load the appropriate dataset based on the presence of an offer percentage
    if offer_percentage == "50":  # Check if there's no percentage
        print("No percentage found in the prompt, using fallback dataset.")
        ads = pd.read_csv(fallback_dataset_path)  # Use fallback dataset
        ads, X, vectorizer = extract_text_features(ads, vectorizer)  # Use the same vectorizer
        ads_with_clusters, kmeans, vectorizer = cluster_ads_by_features(ads, X)

    # Choose a random ad copy from the dataset
    random_ad_copy = random.choice(ads['copy'].values)

    # Replace occurrences of "Maxi" with the extracted product name
    updated_copy = random_ad_copy.replace("Maxi", product_name)

    # Replace any occurrences of "50%" with the extracted offer percentage
    updated_copy = updated_copy.replace("50%", f"{offer_percentage}%")

    # Extract features from the final copy
    updated_copy_features = vectorizer.transform([updated_copy])

    # Predict the cluster for the final ad copy
    cluster_label = kmeans.predict(updated_copy_features)[0]

    return updated_copy, cluster_label


# Extract text features and apply clustering on the main dataset
ads, X, vectorizer = extract_text_features(ads)
ads_with_clusters, kmeans, vectorizer = cluster_ads_by_features(ads, X)

# Interactive input
while True:
    print("\nEnter your prompt (or type 'exit' to quit):")
    user_prompt = input("> ").strip()
    if user_prompt.lower() == "exit":
        print("Goodbye!")
        break
    try:
        # Generate a customized ad copy
        custom_ad, cluster_label = generate_custom_ad(ads, vectorizer, kmeans, user_prompt)
        print("\nHere’s your customized ad copy:")
        print(custom_ad)

        # Display ad cluster description
        cluster_description = ads_with_clusters[ads_with_clusters['cluster'] == cluster_label]['cluster_description'].values[0]
        print(f"\nThis ad belongs to cluster: {cluster_label} ({cluster_description})")

    except Exception as e:
        print(f"Error: {e}")
