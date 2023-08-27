# Movie Generator

Click [here](http://movie-generator.be) for a live demo (use code "movie")


# 1 : Prerequisites

- Anaconda (can be done without, manually pip install requirements inside environment.yml)

# 2 : Installation

- open terminal in the root folder of this project
- create Anaconda env : `conda env create --file=environment.yml`

If the dependencies inside the `environment.yml` file were to change, run the following to update
```bash
conda activate MovieGen
conda env update --file environment.yml --prune
```
- setup recommender:
    - activate anaconda environment : `conda activate MovieGen`
    - change directory to `src/setup`
    - run script to install dataset : `python dataset_installer.py` (Requires a Kaggle.com account + API token, the token json file can be placed in this setup folder)
    - run script to create similarity matrices : `python model_creator.py`

# 3 : Usage

- activate anaconda environment: `conda activate MovieGen`
- change directory to `src/frontend`
- run webserver: `flask --app main run --host "0.0.0.0" --port "3410"`
- open second terminal
- activate anaconda environment: `conda activate MovieGen`
- change directory to `src/backend`
- run backend: `python socket_server.py`

# 4 : Project structure

- dataset (where the dataset will be downloaded to during installation)
- Docker (all docker related files to deploy to a server)
- env (environment variables)
- logs (where the logs collected during operation will be saved)
- models (where the pre-computed recommendation models (similarity matrices) will be located after installation)
- src (all code)
    - backend (all code for the recommender)
        - my_dataclasses (dataclasses to represent a computed recommendation)
            - `movie.py` (represents a single recommended movie together with the information for explanations)
            - `result.py` (represents a complete recommendation consisting of multiple movies)
        - `combiner.py` (functions to combine the recommendations of two users based on least misery)
        - `packer.py` (packages the recommendation result to send it to the frontend)
        - `recommender.py` (makes the recommendations based on the user feedback)
        - `socker_server.py` (handles incoming requests from the frontend, returns the recommendation as an answer)
        - `visualiser.py` (computes all explanations for each recommendation)
    - frontend (all code for the Flask website)
        - flask_session (folder for Flask session (cookie) data)
        - routes (Flask routes)
        - static (css / images / js)
        - templates (HTML)
            - end_page_visual (result page with recommendations and explanations)
            - index (landing page)
            - movie_tinder (smartphone interface)
            - qr (page for scanning qr's)
    - setup (setup code, only used once after installation)
        - `dataset_installer.py` (installs the dataset from Kaggle.com)
        - `model_creator.py` (pre-computes the similarity matrices for later recomendations)

- environment.yml (all dependencies for the python environment)
- title_export.csv (list of all the movie titles)
