import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os
import json
from azure.storage.blob import BlobServiceClient

# =====================
# DISPLAY OPTIONS
# =====================
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# =====================
# AZURITE BLOB CONNECTION
# =====================
connect_str = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING",
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://azurite:10000/devstoreaccount1;"
)
container_name = os.getenv("CONTAINER_NAME", "datasets")
blob_name = os.getenv("BLOB_NAME", "All_Diets.csv")

# Create BlobServiceClient and BlobClient
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

print("Downloading CSV from Azure Blob Storage (Azurite)...")
csv_bytes = blob_client.download_blob().readall()

# =====================
# LOAD DATASET
# =====================
df = pd.read_csv(io.BytesIO(csv_bytes))

print("Dataset Preview:")
print(df.head())
print("\nDataset Info:")
print(df.info())

# =====================
# DATA CLEANING
# =====================
numeric_cols = ['Protein(g)', 'Carbs(g)', 'Fat(g)']
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

# =====================
# ANALYSIS
# =====================
avg_macros = df.groupby('Diet_type')[numeric_cols].mean()
top_protein = df.sort_values('Protein(g)', ascending=False).groupby('Diet_type').head(5)
highest_protein_diet = avg_macros['Protein(g)'].idxmax()
common_cuisine = df.groupby('Diet_type')['Cuisine_type'].agg(lambda x: x.value_counts().idxmax())

# =====================
# RATIO METRICS
# =====================
df['Protein_to_Carbs_ratio'] = df['Protein(g)'] / df['Carbs(g)']
df['Carbs_to_Fat_ratio'] = df['Carbs(g)'] / df['Fat(g)']

# =====================
# SAVE OUTPUT FILES
# =====================
avg_macros.to_csv("avg_macros_by_diet.csv")
top_protein.to_csv("top_5_protein_recipes.csv", index=False)

# =====================
# SIMULATED NOSQL STORAGE
# =====================
os.makedirs("simulated_nosql", exist_ok=True)
avg_macros.reset_index(inplace=True)
result_json = avg_macros.to_dict(orient="records")
with open("simulated_nosql/results.json", "w") as f:
    json.dump(result_json, f, indent=2)

# =====================
# VISUALIZATIONS
# =====================
plt.figure(figsize=(10, 6))
sns.barplot(x=avg_macros['Diet_type'], y=avg_macros['Protein(g)'])
plt.title("Average Protein by Diet Type")
plt.ylabel("Protein (g)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("avg_protein_by_diet.png")
plt.close()

plt.figure(figsize=(8, 6))
sns.heatmap(avg_macros.set_index('Diet_type')[numeric_cols], annot=True, fmt=".0f", cmap="coolwarm")
plt.title("Macronutrient Heatmap by Diet Type")
plt.tight_layout()
plt.savefig("macronutrient_heatmap_by_diet.png")
plt.close()

plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=top_protein,
    x='Protein(g)',
    y='Carbs(g)',
    hue='Cuisine_type'
)
plt.title("Top 5 Protein-Rich Recipes by Cuisine")
plt.tight_layout()
plt.savefig("top5_protein_recipes_scatter.png")
plt.close()

print("\nAnalysis complete. Files generated successfully.")
