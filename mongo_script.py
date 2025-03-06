import json

import pymongo
from pymongo import GEOSPHERE
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

from app.core.config import settings

# Initialize Rich Console
console = Console()

# MongoDB Connection String
MONGO_URI = settings.MONGODB_URI
DATABASE_NAME = settings.MONGODB_DB
COLLECTION_NAME = "lga_boundaries"

# Load Nigeria States GeoJSON File
GEOJSON_FILE_PATH = "nigeria_lga_boundaries.geojson"

console.print(
    Panel.fit(
        "[bold cyan]Starting Nigeria LGAs GeoJSON Upload to MongoDB 🌍[/bold cyan]",
        title="[bold green]MongoDB Uploader[/bold green]",
    )
)

try:
    with open(GEOJSON_FILE_PATH, "r", encoding="utf-8") as file:
        geojson_data = json.load(file)

    console.print("✅ Successfully loaded GeoJSON data.", style="bold green")
except Exception as e:
    console.print(f"❌ Error loading GeoJSON file: {e}", style="bold red")
    exit(1)

# Extracting features
features = geojson_data.get("features", [])
if not features:
    console.print("⚠️ No features found in the GeoJSON file.", style="bold yellow")
    exit(1)

# Connect to MongoDB
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    console.print("🔗 Connected to MongoDB successfully!", style="bold green")
except Exception as e:
    console.print(f"❌ MongoDB Connection Failed: {e}", style="bold red")
    exit(1)

# Ensure Collection Has a Geospatial Index
collection.create_index([("geometry", GEOSPHERE)])
console.print("📌 Geospatial index created on 'geometry' field.", style="bold cyan")

# Prepare Data for MongoDB Upload
documents = []
for feature in features:
    state_data = {
        "lga_name": feature["properties"].get("admin2Name", "Unknown"),
        "lga_code": feature["properties"].get("admin2Pcod", "Unknown"),
        "state_name": feature["properties"].get("admin1Name", "Unknown"),
        "state_code": feature["properties"].get("admin1Pcod", "Unknown"),
        "country_name": feature["properties"].get("admin0Name", "Nigeria"),
        "geometry": feature["geometry"],
    }
    documents.append(state_data)

# Insert Data into MongoDB
with Progress() as progress:
    task = progress.add_task(
        "[green]Uploading data to MongoDB...", total=len(documents)
    )
    for doc in documents:
        collection.insert_one(doc)
        progress.update(task, advance=1)

console.print(
    f"✅ Successfully uploaded {len(documents)} state boundaries to MongoDB!",
    style="bold green",
)
