# Plotly Dash Shootings Data Visualization Application

This application is an interactive tool developed using Plotly Dash to visualize gun violence trends and patterns in Philadelphia from 2015 through Present.  By transforming raw data into insightful visualizations, the application seeks to provide a more nuanced understanding of gun violence trends and patterns in Philadelphia. 

[Exploratory Data Analysis of Philadelphia's Gun Violence: 
An Interactive Exploration of Gun Violence Trends and Patterns in Philadelphia (2015 - Present)](http://masnell5.pythonanywhere.com/)

## Analysis
This Dash application provides a comprehensive visualization and analysis of gun violence incidents in Philadelphia, highlighting trends and patterns in various views.

The interactive features of the app allow users to explore different aspects of the shootings data, including:

- **Shootings Per Year:** This bar chart displays the total number of shootings for each year, segmented by the victim outcome (either fatal or non-fatal). It offers insights into the annual trend of shooting incidents.

- **Shootings Per Month:** This bar chart provides a monthly breakdown of shooting incidents. Users can examine the distribution of shootings throughout the year and identify any seasonal trends.

- **Shootings Per Hour:** This visualization breaks down the shootings by the hour of the day, providing insights into the times of day when shooting incidents are most prevalent.

- **Daily Distribution of Shooting Incidents Per Day Heatmap:** This heatmap represents the daily distribution of shooting incidents. It allows users to identify patterns and trends in the occurrence of daily shootings over the course of a year.

- **Shootings Per Police District Choropleth Map:** This map displays the number of shootings per police district, providing a geographical overview of shooting incidents.

The application also includes a dropdown feature, enabling users to filter the data by specific years and police districts. This feature allows for more targeted analysis, helping users to examine trends and patterns within specific time periods or geographical areas.

The purpose of this tool is to promote data-driven understanding and decision-making. By visualizing and exploring the data in an interactive manner, users can gain a more nuanced understanding of the context and implications of shooting incidents.

## Installation

Before running the application, create a virtual environment and install the required Python libraries. You can do this by running the following command in your terminal:

```bash
pip install -r requirements.txt
```

## Data
The data used in this Dash application is sourced from the City of Philadelphia's Open Data platform. The specific dataset represents shooting victims in the city and is provided as a public service by the Philadelphia Police Department. It includes important information such as the date, time, and location of each incident, as well as details about the victim and the outcome of the incident.

The dataset is accessible through the following API endpoint provided by the city's CartoDB account: https://phl.carto.com/api/v2/sql?q=SELECT+*,+ST_Y(the_geom)+AS+lat,+ST_X(the_geom)+AS+lng+FROM+shootings&filename=shootings&format=csv&skipfields=cartodb_id

