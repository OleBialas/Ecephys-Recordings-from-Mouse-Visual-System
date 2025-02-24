# Extracellular Electrophysiological Recordings from Mouse Visual System

This repo contains data from the Allen Institute's [visual coding dataset](https://portal.brain-map.org/circuits-behavior/visual-coding-neuropixels) as well as the code to download this data and convert it to other formats.

## Installing Dependencies

This project uses `uv` to manage the Python software dependencies and `datalad` to download and manage data.
Follow the steps below to set up an environment that allows you to download the data and replicate the processing pipeline.

First, clone this repository and move into the cloned directory
```sh
git clone https://github.com/OleBialas/Ecephys-Recordings-from-Mouse-Visual-System.git
cd Ecephys-Recordings-from-Mouse-Visual-System
```

Then, install the [uv package manager](docs.astral.sh/uv/getting-started/installation/) and install and activate the Python environment

```sh
uv sync
source .venv/bin/activate # on Linux/MacOs
.\venv\Scripts\activate # on Windows
```

While datalad itself is included in the evironment, it depends on git-annex.
If you don't have git-annex installed, you can simply run the datalad installer:

```
datalad-installer git-annex -m datalad/git-annex:release
```

## Downloading Data

Now you can download the actual data using `datalad` (which is part of the installed environment) using the `datalad get` command.
Initially you may want to get the dataset's structure without downloading all of the content.
This can be done by using the `-n` (no data) flag which downloads symbolic links for al files without their content.

```sh
datalad get -n data
```

Once this is done you can download specific parts of the dataset, for example the `raw` folder:

```sh
datalad get data/raw
```

## Running the Pipeline

The data are downloaded and converted using several Python scripts. They can be found in the `/scipts` directory and can be run together by running

```sh
bash run_pipeline.sh
```

Be aware that this will take several hours because the data has to be downloaded from the Allen Institute's repository.
