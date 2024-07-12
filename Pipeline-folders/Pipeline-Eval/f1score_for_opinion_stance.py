import pandas as pd
from sklearn.metrics import classification_report, f1_score
from collections import Counter

# Load the CSV data
csv_file = "entities_opinions_evaluation.csv"
data = pd.read_csv(csv_file)

# Helper function to split and normalize list strings
def split_and_normalize(s):
    return sorted(s.split(', ')) if pd.notna(s) else []

# Extract the true and predicted values for opinion evaluation
y_true_evaluation = data["manual_opinion_evaluation"]
y_pred_evaluation = data["ml_opinion_evaluation"]

# Compute classification report for opinion evaluation

report_evaluation = classification_report(y_true_evaluation, y_pred_evaluation, labels=["authentic", "forgery", "suspicious"], zero_division=1, digits=4)
print("Opinion Evaluation Report")
print(report_evaluation)

# Compute F1 scores for opinion evaluation
f1_authentic = f1_score(y_true_evaluation, y_pred_evaluation, labels=["authentic"], average='macro')
f1_forgery = f1_score(y_true_evaluation, y_pred_evaluation, labels=["forgery"], average='macro')
f1_suspicious = f1_score(y_true_evaluation, y_pred_evaluation, labels=["suspicious"], average='macro')

print(f"F1 Score for authentic: {f1_authentic:.4f}")
print(f"F1 Score for forgery: {f1_forgery:.4f}")
print(f"F1 Score for suspicious: {f1_suspicious:.4f}")

# Extract and normalize opinion evidence provided (features)
data["manual_opinion_evidence_provided"] = data["manual_opinion_evidence_provided"].apply(split_and_normalize)
data["ml_opinion_evidence_provided"] = data["ml_opinion_evidence_provided"].apply(split_and_normalize)

# Flatten lists of features for evaluation, based only on manual dataset
manual_features = sorted(set([feature for sublist in data["manual_opinion_evidence_provided"] for feature in sublist]))
print("Features being evaluated (manual dataset):", manual_features)

# Initialize true and predicted lists for each feature
true_features = {feature: [] for feature in manual_features}
pred_features = {feature: [] for feature in manual_features}

# Populate true and predicted lists for each feature
for i, row in data.iterrows():
    manual_features_list = row["manual_opinion_evidence_provided"]
    ml_features_list = row["ml_opinion_evidence_provided"]
    for feature in manual_features:
        true_features[feature].append(1 if feature in manual_features_list else 0)
        pred_features[feature].append(1 if feature in ml_features_list else 0)

# Calculate F1 scores for each feature
feature_f1_scores = {}
for feature in manual_features:
    f1 = f1_score(true_features[feature], pred_features[feature], zero_division=1)
    feature_f1_scores[feature] = f1
    print(f"F1 Score for feature '{feature}': {f1}")

# Calculate mean F1 score for all features
mean_f1_features = sum(feature_f1_scores.values()) / len(feature_f1_scores)
print(f"Mean F1 Score for all features: {mean_f1_features}")

# Identify features only in ML dataset
ml_only_features = set([feature for sublist in data["ml_opinion_evidence_provided"] for feature in sublist]) - set(manual_features)
print("Features only in ML dataset:", ml_only_features)

# Extract and normalize opinion specific perspective
data["manual_opinion_specific_perspective"] = data["manual_opinion_specific_perspective"].apply(split_and_normalize)
data["ml_opinion_specific_perspective"] = data["ml_opinion_specific_perspective"].apply(split_and_normalize)

# Flatten lists of perspectives for evaluation, based only on manual dataset
manual_perspectives = sorted(set([perspective for sublist in data["manual_opinion_specific_perspective"] for perspective in sublist]))
print("Perspectives being evaluated (manual dataset):", manual_perspectives)

# Initialize true and predicted lists for each perspective
true_perspectives = {perspective: [] for perspective in manual_perspectives}
pred_perspectives = {perspective: [] for perspective in manual_perspectives}

# Populate true and predicted lists for each perspective
for i, row in data.iterrows():
    manual_perspectives_list = row["manual_opinion_specific_perspective"]
    ml_perspectives_list = row["ml_opinion_specific_perspective"]
    for perspective in manual_perspectives:
        true_perspectives[perspective].append(1 if perspective in manual_perspectives_list else 0)
        pred_perspectives[perspective].append(1 if perspective in ml_perspectives_list else 0)

# Calculate F1 scores for each perspective
perspective_f1_scores = {}
for perspective in manual_perspectives:
    f1 = f1_score(true_perspectives[perspective], pred_perspectives[perspective], zero_division=1)
    perspective_f1_scores[perspective] = f1
    print(f"F1 Score for perspective '{perspective}': {f1}")

# Calculate mean F1 score for all perspectives
mean_f1_perspectives = sum(perspective_f1_scores.values()) / len(perspective_f1_scores)
print(f"Mean F1 Score for all perspectives: {mean_f1_perspectives}")

# Identify perspectives only in ML dataset
ml_only_perspectives = set([perspective for sublist in data["ml_opinion_specific_perspective"] for perspective in sublist]) - set(manual_perspectives)
print("Perspectives only in ML dataset:", ml_only_perspectives)

# Calculate document-level F1 scores for opinion evaluation
doc_f1_scores = {}
num_claims_per_doc = {}
for doc_id in data["doc_id"].unique():
    doc_data = data[data["doc_id"] == doc_id]
    y_true_doc = doc_data["manual_opinion_evaluation"]
    y_pred_doc = doc_data["ml_opinion_evaluation"]
    f1_doc = f1_score(y_true_doc, y_pred_doc, average='macro', zero_division=1)
    doc_f1_scores[doc_id] = f1_doc
    num_claims_per_doc[doc_id] = len(doc_data)

# Sort documents by F1 score
sorted_docs = sorted(doc_f1_scores.items(), key=lambda x: x[1], reverse=True)

# Print sorted document-level F1 scores
print("Documents sorted by F1 score for opinion evaluation:")
for doc_id, f1_score in sorted_docs:
    print(f"Document {doc_id}: F1 Score = {f1_score}")

# Count the number of documents for each unique F1 score
f1_score_counts = Counter(doc_f1_scores.values())
print("\nNumber of documents for each unique F1 score:")
for score, count in f1_score_counts.items():
    print(f"F1 Score: {score:.2f}, Number of Documents: {count}")
