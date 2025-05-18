from dotenv import load_dotenv
import os
from pathlib import Path
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ENTITY_FILES_DIR = Path("input/entity_files")

if not ENTITY_FILES_DIR.exists() or not ENTITY_FILES_DIR.is_dir():
    raise RuntimeError(f"Directory not found: {ENTITY_FILES_DIR}")

uploaded_file_ids = []
for file_path in ENTITY_FILES_DIR.iterdir():
    if not file_path.is_file():
        continue
    with file_path.open("rb") as f:
        resp = client.files.create(
            file=f,
            purpose="user_data"
        )
    file_id = resp.id
    print(f"Uploaded {file_path.name} → file ID: {file_id}")
    uploaded_file_ids.append(file_id)

if not uploaded_file_ids:
    raise RuntimeError(f"No files uploaded from {ENTITY_FILES_DIR}")

vector_store = client.vector_stores.create(
    name="Entity Files"
)
vs_id = vector_store.id
print(f"Created vector store → ID: {vs_id}")

for fid in uploaded_file_ids:
    link_resp = client.vector_stores.files.create(
        vector_store_id=vs_id,
        file_id=fid
    )
    print(f"Linked file {fid} to vector store → {link_resp}")

print("All files have been uploaded and linked successfully.")
