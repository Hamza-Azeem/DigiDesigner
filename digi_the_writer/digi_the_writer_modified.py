import argparse
import spacy
import pandas as pd
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from textblob import TextBlob
import textstat  # For readability scores
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

# Paths to datasets
main_dataset_path = "D:\\study\\backend\\digi_the_writer\\fashion_maxi_ads_with_offer.csv" # Adjust to your dataset path
fallback_dataset_path = "D:\\study\\backend\\digi_the_writer\\fashion_maxi_ads.csv"   # Fallback dataset path

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
                try:
                    product_name = ent.text.split()[-1]
                except Exception as e:
                    print(f"Error splitting entity text: {ent.text}. Error: {e}")
            elif ent.label_ == "MONEY":
                offer_amount = ent.text.strip("$")
            elif "%" in ent.text:
                offer_percentage = ent.text.strip("%")

    # Fallback if entities are missing
    if not product_name:
        for token in doc:
            if token.text.lower() == "called":
                product_name = token.nbor(1).text  # Get the token after "called"
                break

    # Defaults if not found
    product_name = product_name or "Maxi"
    offer_amount = offer_amount or "50"
    offer_percentage = offer_percentage or "50"

    return product_name, offer_amount, offer_percentage

def generate_custom_ad(ads, vectorizer, kmeans, prompt):
    """
    Generates a customized ad copy based on the extracted product name and offer percentage,
    and predicts the cluster for the generated ad.
    """
    product_name, offer_amount, offer_percentage = extract_details_with_nlp(prompt)

    # Load the appropriate dataset
    if offer_percentage == "50":
        ads = pd.read_csv(fallback_dataset_path)
        ads, X, vectorizer = extract_text_features(ads, vectorizer)
        ads_with_clusters, kmeans, vectorizer = cluster_ads_by_features(ads, X)

    # Choose a random ad copy from the dataset
    random_ad_copy = random.choice(ads['copy'].values)

    # Replace placeholders with extracted details
    updated_copy = random_ad_copy.replace("Maxi", product_name)
    updated_copy = updated_copy.replace("50%", f"{offer_percentage}%")

    return updated_copy

def extract_text_features(ads, vectorizer=None):
    """
    Extracts various text-based features from the ad copy for clustering.
    """
    ads['length'] = ads['copy'].apply(lambda x: len(x.split()))
    ads['sentiment'] = ads['copy'].apply(sentiment_analysis)
    ads['emotion'] = ads['copy'].apply(emotion_detection)
    ads['readability'] = ads['copy'].apply(readability_scores)

    if vectorizer is None:
        vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(ads['copy'])
    return ads, X, vectorizer

def sentiment_analysis(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def emotion_detection(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)

    if sentiment['compound'] >= 0.05:
        return "Happy"
    elif sentiment['compound'] <= -0.05:
        return "Angry"
    else:
        return "Neutral"

def readability_scores(text):
    return textstat.flesch_kincaid_grade(text)

def cluster_ads_by_features(ads, X, n_clusters=5):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(X)
    ads['cluster'] = kmeans.labels_
    return ads, kmeans, vectorizer

def main():
    # Command-line arguments
    parser = argparse.ArgumentParser(description="Generate custom ad copy.")
    parser.add_argument('--prompt', type=str, required=True, help="User prompt for ad generation")
    args = parser.parse_args()

    # Process the user prompt
    user_prompt = args.prompt.strip()
    if not user_prompt:
        print("Error: No prompt provided.")
        return

    # Generate a customized ad copy
    try:
        custom_ad = generate_custom_ad(ads, vectorizer, kmeans, user_prompt)
        print(custom_ad)  # Output the generated ad copy for Spring Boot
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Preprocess ads and initialize clustering
    ads, X, vectorizer = extract_text_features(ads)
    ads_with_clusters, kmeans, vectorizer = cluster_ads_by_features(ads, X)
    main()
