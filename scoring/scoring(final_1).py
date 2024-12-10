import argparse
import facebook
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import json
import sys
import re

# Function to extract 'purchases' from 'actions'
def get_purchases(actions):
    for action in actions:
        if action.get('action_type') == 'purchase':
            return float(action.get('value', 0))
    return 0

# Function to calculate 'cost_per_purchase'
def get_cost_per_purchase(actions, spend):
    spend = float(spend)
    purchases = get_purchases(actions)
    if purchases > 0:
        return spend / purchases
    return 0

def clean_name(name):
    return re.sub(r'\s+', ' ', name.strip())

# Fetch campaign insights
def get_campaign_insights_by_name(access_token, campaign_name, fields=None, date_preset='last_7d'):
    graph = facebook.GraphAPI(access_token)
    campaigns = graph.get_object('/act_1567679400445774/campaigns', fields='id,name')

    # Log retrieved campaigns to stderr
    for campaign in campaigns['data']:
        sys.stderr.write(f"Campaign Name: {campaign['name']} (ID: {campaign['id']})\n")

    campaign_id = None
    for campaign in campaigns['data']:
        if clean_name(campaign['name']) == clean_name(campaign_name):
            campaign_id = campaign['id']
            break

    if not campaign_id:
        raise ValueError(f"Campaign with name '{campaign_name}' not found.")

    if fields is None:
        fields = 'campaign_name,impressions,clicks,spend,cpc,cpm,ctr,actions,cost_per_action_type,inline_link_click_ctr'

    insights = graph.get_object(f'/{campaign_id}/insights', fields=fields, date_preset=date_preset)

    insights_data = insights.get('data', [])
    if insights_data:
        insights_df = pd.DataFrame(insights_data)
        insights_df['purchases'] = insights_df['actions'].apply(get_purchases)
        insights_df['cost_per_purchase'] = insights_df.apply(
            lambda row: get_cost_per_purchase(row['actions'], row['spend']), axis=1
        )
        insights_df.rename(columns={
            'actions': 'purchase',
            'inline_link_click_ctr': 'link_clicks'
        }, inplace=True)

        return insights_df[['spend', 'cpm', 'link_clicks', 'ctr', 'cpc', 'purchases', 'cost_per_purchase']]
    else:
        raise ValueError("No insights data found for this campaign.")

# Machine learning scoring function
def Shikabala(data, new_campaigns):
    label_encoders = {}
    for column in ['metrics_label', 'roi_label']:
        le = LabelEncoder()
        data[column] = le.fit_transform(data[column])
        label_encoders[column] = le

    X = data[['spend', 'cpm', 'ctr', 'cpc', 'purchases', 'cost_per_purchase']]
    y = data[['combined_score', 'cluster', 'how_far_score', 'predicted_roi',
              'normalized_how_far', 'metrics_label', 'roi_label']]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf_models = {}
    for target in y.columns:
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train[target])
        rf_models[target] = rf_model

    predictions = {}
    for target in y.columns:
        predictions[target] = rf_models[target].predict(new_campaigns)

    predictions_df = pd.DataFrame(predictions)
    predictions_df['metrics_label'] = label_encoders['metrics_label'].inverse_transform(predictions_df['metrics_label'].astype(int))
    predictions_df['roi_label'] = label_encoders['roi_label'].inverse_transform(predictions_df['roi_label'].astype(int))

    return predictions_df

# Score campaigns using ML
def score_campaign_with_ml(access_token, campaign_name, model_data_path):
    model_data = pd.read_excel(model_data_path)
    insights_df = get_campaign_insights_by_name(access_token, campaign_name)
    campaign_data = insights_df[['spend', 'cpm', 'ctr', 'cpc', 'purchases', 'cost_per_purchase']]
    scores_df = Shikabala(model_data, campaign_data)
    return scores_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Score campaigns using ML model.")
    parser.add_argument("--access_token", required=True, help="Facebook API access token")
    parser.add_argument("--campaign_name", required=True, help="Campaign name")
    parser.add_argument("--model_data_path", required=True, help="Path to model data file (Excel)")
    args = parser.parse_args()

    try:
        scores_df = score_campaign_with_ml(args.access_token, args.campaign_name, args.model_data_path)
        print(scores_df.to_json(orient='records'))  # JSON output
    except Exception as e:
        print(json.dumps({"error": str(e)}))  # JSON error response
        sys.exit(1)
