"""
Download metadata on all recording sessions.
Metadata for the whole dataset are stored in .csv files and metadata for individual sessions are stored in .json files in the subfolder for the respective session.
"""

from pathlib import Path
from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
from tqdm import tqdm

root = Path(__file__).parent.parent.absolute()

# Connect to Allen Service
cache_dir = root / "data" / "cache"
cache = EcephysProjectCache.from_warehouse(manifest=cache_dir / "manifest.json")

# Download the tables for sessions, channels and units in the whole dataset
sessions = cache.get_session_table()
channels = cache.get_channels()
units = cache.get_units()

# Create output directory
out_dir = root / "data" / "raw"
out_dir.mkdir(exist_ok=True, parents=True)

# Save dataset-level tables
sessions.to_csv(out_dir/"all_sessions.csv")
channels.to_csv(out_dir/"all_channels.csv")
units.to_csv(out_dir/"all_units.csv")

for session_id, row in tqdm(sessions.iterrows()):
    row["id"] = session_id
    session_dir = out_dir / f"ses-{session_id}"
    session_dir.mkdir(exist_ok=True, parents=True)
    out_file = session_dir / "session.json"
    row.to_json(out_file, indent=3)
