from argparse import ArgumentParser
from pathlib import Path
import pandas as pd

parser = ArgumentParser()
parser.add_argument("out_path", type=str)
args = parser.parse_args()

# Get the spikes in the areas defined below. Keys are the area names in the input
# data frame, values are the area names in the output data frame.
areas = {
    "VISal": "AL",  # anterolateral
    "VISam": "AM",  # anteromedial
    "VISl": "LM",  # lateromedial
    "VISp": "V1",  # primary visual cortex
    "VISpm": "PM",  # posteriormedial
    "VISrl": "RL",  # rostrolateral
}

root = Path(__file__).parent.parent.absolute()
sessions = list((root / "data" / "raw").glob("ses*"))

ses = sessions[0]

# Get white full-field flashes and natural scenes
stimuli = pd.read_parquet(ses / "stimuli.parquet")
stimuli = stimuli[stimuli.stimulus_name.isin(["flashes", "natural_scenes"])]
stimuli = stimuli[(stimuli.color == 1) | pd.isna(stimuli.color)]
stimuli = stimuli[["start_time", "stimulus_name"]].reset_index(drop=True)
stimuli = stimuli.rename(columns={"start_time": "time", "stimulus_name": "kind"})
stimuli = stimuli.set_index("time", drop=True)

units = pd.read_parquet(ses / "units.parquet")[
    ["ecephys_structure_acronym", "spike_times"]
]

units = (
    units.reset_index()
    .explode("spike_times")
    .set_index("spike_times")
    .rename_axis("time")
)
units = units.rename(columns={"unit_id": "unit", "ecephys_structure_acronym": "area"})

## save data
out_dir = Path(args.out_path)/ses.name
if not out_dir.exists():
    out_dir.mkdir(parents=True)
units.to_parquet(out_dir/"units.parquet")
stimuli.to_parquet(out_dir/"stimuli.parquet")
