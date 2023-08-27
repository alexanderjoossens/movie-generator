#!/bin/bash

find_in_conda_env(){
    conda env list | grep "${@}" >/dev/null 2>/dev/null
}

echo "Creating environment variable to signal that we are inside a docker container"
export IN_DOCKER="true" 

echo "Changing directory to 'MovieGenerator'"
cd MovieGenerator

echo "Listing all files"
ls

echo "Activating conda in current bash session"
#source ~/miniconda3/bin/activate
eval "$(conda shell.bash hook)"
conda init bash

if find_in_conda_env "MovieGen" ; then
   echo "Found pre-existing 'MovieGen' conda environment"
   echo "Activating environment"
   conda activate MovieGen
   echo "Updating environment"
   conda env update --file environment.yml --prune
   #yes | pip install -r requirements.txt
else
   echo "Couldn't find the 'MovieGen' conda environment, is this the first time setup?"
   echo "Creating new 'MovieGen' conda environment"
   conda env create --file environment.yml
   #conda create --name MovieGen python=3.10
   conda activate MovieGen
   #yes | pip install -r requirements.txt
fi

echo "Starting the recommender"
echo "Activating environment"
conda activate MovieGen
echo "Starting frontend"
cd /MovieGenerator/src/frontend
flask --app main run --host "0.0.0.0" --port 3410