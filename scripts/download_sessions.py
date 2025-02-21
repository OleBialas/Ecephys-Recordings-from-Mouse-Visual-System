"""
Download the stimulus table, behavioral data and single units with spike times and mean waveforms for a single recording session in store them in three separate parquet files.
"""

from pathlib import Path
import os
import ast
from tqdm import tqdm
from argparse import ArgumentParser
import numpy as np
import pandas as pd
from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache

root = Path(__file__).parent.parent.absolute()

parser = ArgumentParser()
parser.add_argument("--clear", action="store_true", default=False, help="Clear the cache after saving the output")
parser.add_argument("--overwrite", action="store_true", default=False, help="Overwrite existing files with the same name")
args = parser.parse_args()

# Connect to Allen Service
cache_dir = root / "data" / "cache"
cache = EcephysProjectCache.from_warehouse(manifest=cache_dir / "manifest.json")

# Check if session ID exists
sessions = pd.read_csv(root/"data"/"raw"/"all_sessions.csv", index_col="id")
for session_id in tqdm(sessions.index):
    # Check if the output files already exists
    out_folder = root / "data" / "raw" / f"ses-{session_id}"
    files_exist = all([
        (out_folder/f).exists() for f in ["units.parquet", "stimuli.parquet", "running.parquet"]
    ])
    if (out_folder/"units.parquet").exists() and not args.overwrite:
        print(
            f"Skipping session {session_id} because files already exist! Use `--overwrite` to re-download.")
    else:
        print(f"Loading session {session_id}")
        out_folder.mkdir(exist_ok=True, parents=True)

        # load session data
        ecephys_session = cache.get_session_data(session_id)

        # Get behavior data (eye tracking does not exist for all animals)
        df_running = ecephys_session.running_speed
        df_pupil = ecephys_session.get_pupil_data()
        if df_pupil is not None:
            df_gaze = ecephys_session.get_screen_gaze_data()
            pd.testing.assert_index_equal(df_pupil.index, df_gaze.index)
            df_eyetracking = pd.concat([df_pupil, df_gaze], axis=1)
        else:
            df_eyetracking = None

        # Encode "null" values as NaN to make data parquet compatible
        df_stimuli = ecephys_session.get_stimulus_table()
        df_stimuli.replace("null", np.nan, inplace=True)
        # convert (lists of) strings to scalars
        def safe_literal_eval(val):
            try:
                if val == "null" or pd.isna(val):
                    return None
                val = ast.literal_eval(val)
                if isinstance(val, list):
                    val = val[0]
                return val
            except (ValueError, SyntaxError):
                # Return the original value if it can't be evaluated
                return val

        for field in ["spatial_frequency", "phase"]:
            df_stimuli[field] = df_stimuli[field].apply(safe_literal_eval)

        # Get units data and add spike times
        df_units = ecephys_session.units
        df_units["spike_times"] = pd.Series(ecephys_session.spike_times, name="unit_id")

        # Add largest mean waveform and corresponding channel id
        mean_waveforms = ecephys_session.mean_waveforms
        max_waveforms = {}
        max_waveforms_channels = {}
        for uid, mean_waveform in mean_waveforms.items():
            peak_to_peak = mean_waveform.data.max(axis=1) - mean_waveform.data.min(axis=1)
            max_idx = np.argmax(peak_to_peak)
            max_waveforms[uid] = mean_waveform.data[max_idx]
            max_waveforms_channels[uid] = mean_waveform.channel_id.values[max_idx]
        df_units["mean_waveform"] = pd.Series(max_waveforms, name="unit_id")
        df_units["mean_waveform_channel"] = pd.Series(max_waveforms_channels, name="unit_id")

        # Add rounded time points for mean waveforms
        times = np.array([wave.time.values for wave in mean_waveforms.values()])
        # Fix NaN rows
        times[np.where(np.isnan(times))[0]] = times[0]
        times_rounded = np.round(times, 6)
        assert np.all(
            np.diff(times_rounded, axis=0).mean(axis=0) == 0
        ), "Rounded times have not created identical time points."
        assert np.all(
            np.diff(times_rounded, axis=1) > 0
        ), "Rounded times are not monotonically increasing."
        df_units["mean_waveforms_times"] = [row for row in times_rounded]

        # Save result
        df_units.to_parquet(out_folder/"units.parquet")
        df_running.to_parquet(out_folder/"running.parquet")
        df_stimuli.to_parquet(out_folder/"stimuli.parquet")
        if df_eyetracking is not None:
            df_eyetracking.to_parquet(out_folder/"eyetracking.parquet")

        # Delete downloaded file from cache
        if args.clear:
            cache_fname = cache_dir/f"session_{session_id}"/f"session_{session_id}.nwb"
            os.remove(cache_fname)


