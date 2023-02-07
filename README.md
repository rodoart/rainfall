
[![LinkedIn][linkedin-shield]](https://www.linkedin.com/in/rodolfo-arturo-gonzález-trillo-93829219a)

<!-- PROJECT LOGO -->
<br />
<p align="center">
    <img src="https://i.ibb.co/9pNKXTv/git-logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Rainfall Analysis and Prediction</h3>

  <p align="center">
    This project is an exploratory and predictive analysis of the CONAGUA dataset that contains data taken daily on rainfall, temperature, and evaporation throughout all of Mexico. The city of Durango, Durango, is analyzed, but the provided rainfall library can be used as a pipeline for the download, cleaning and ordering of data from any other city.
  </p>
</p>




## Introduction

Climate is perhaps one of the most important elements for defining a region and its inhabitants: animals, native plants, water availability depend on it, which form the basis of local ecology and its relationships with human society.




CONAGUA and its National Meteorological Service collect real-time data from more than 1,000 weather stations in Mexico. On their [web page](https://smn.conagua.gob.mx/tools/RESOURCES/estacion/EstacionesClimatologicas.kmz) they grant access to this data in a `.kmz` file, which is used by various geographic information software and From here, access the historical information of each weather station.

![Image of weather stations in Google Earth Pro.](https://i.ibb.co/5WLZNSQ/republica.jpg)


In this project, I used Python to scrape the links from the kmz file. The `rainfall.make_dataset.StationsDataFrame` class can be used to download the data for each station or for an entire municipality or state. The `DailyMedians` method is used to organize the data by day, while the `rainfall.make_dataset.PeriodicMedians` class can be used to make the weekly or monthly average.

Due to the variable nature of each region, presenting an automatic exploratory analysis method is practically impossible, so I present an example of [how to do this analysis for the city of Durango, Durango](notebooks/2.1_rainfall-data_exploration_durango_durango.ipynb) . I have included seasonal analysis and correlation of variables. The conclusions of this analysis can be found in reports.

I have also made predictions for the rain variable using neural networks, random forests and grid search to optimize. This process is automated in the module: INSERT NAME HERE.
  
## Installation guide

Please read [install.md](install.md) for details on how to set up this project.

## Project Organization

    ├── LICENSE
    ├── tasks.py           <- Invoke with commands like `notebook`.
    ├── README.md          <- The top-level README for developers using this project.
    ├── install.md         <- Detailed instructions to set up this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries.
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures         <- Generated graphics and figures to be used in reporting.
    │
    ├── environment.yml    <- The requirements file for reproducing the analysis environment.
    │
    ├── .here              <- File that will stop the search if none of the other criteria
    │                         apply when searching head of project.
    │
    ├── setup.py           <- Makes project pip installable (pip install -e .)
    │                         so rainfall can be imported.
    │
    └── rainfall               <- Source code for use in this project.
        ├── __init__.py    <- Makes rainfall a Python module.
        │
        ├── data           <- Scripts to download or generate data.
        │   └── make_dataset.py
        │
        ├── features       <- Scripts to turn raw data into features for modeling.
        │   └── build_features.py
        │
        ├── models         <- Scripts to train models and then use trained models to make
        │   │                 predictions.
        │   ├── predict_model.py
        │   └── train_model.py
        │
        ├── utils          <- Scripts to help with common tasks.
            └── paths.py   <- Helper functions to relative file referencing across project.
        │
        └── visualization  <- Scripts to create exploratory and results oriented visualizations.
            └── visualize.py

---



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/rodolfo-arturo-gonzalez-trillo-93829219a