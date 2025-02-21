# Extracellular Electrophysiological Recordings from Mouse Visual System

This repo contains data from the Allen Institute's [visual coding dataset](https://portal.brain-map.org/circuits-behavior/visual-coding-neuropixels) as well as the code to download this data and convert it to other formats.

## Download the Data

First, clone this repository and move into the cloned directory
```sh
git clone https://github.com/OleBialas/Ecephys-Recordings-from-Mouse-Visual-System.git
cd Ecephys-Recordings-from-Mouse-Visual-System
```

Then, install the [uv package manager](docs.astral.sh/uv/getting-started/installation/) and install and activate the Python environment

```sh
uv sync
source .venv/bin/activate # on Linux/MacOs
./venv/Scripts/activate # on Windows
```

Now you can download the actual data using `datalad` (which is part of the installed environment).
For example, to download everything in the `raw` folder, do

```sh
datalad get data/raw/*
```

Or, to simply downlad everything, do

```sh
datalad get *
```

## Running the Pipeline

The data are downloaded and converted using several Python scripts. They can be found in the `/scipts` directory and can be run together by running

```sh
bash run_pipeline.sh
```

Be aware that this will take several hours because the data has to be downloaded from the Allen Institute's repository.
