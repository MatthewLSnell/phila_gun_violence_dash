# Plotly Dash Shootings Data Visualization Application

This application is an interactive tool developed using Plotly Dash to visualize gun violence trends and patterns in Philadelphia from 2015 through Present.  By transforming raw data into insightful visualizations, the application seeks to provide a more nuanced understanding of trends and patterns in shooting incidents. Through a range of interactive features, users can customize their view, filter data, and gain detailed insights into gun violence incidents per year and police district. 

## Project Description

The application leverages a dataset of shooting incidents and performs several data transformations to format, clean, and enhance the data. The enriched data is then presented in several visualizations to provide various perspectives about the shooting incidents. Users can filter and interact with these visualizations to drill down into specific details.

## Installation

Before running the application, install the required Python libraries. You can do this by running the following command in your terminal:

```bash
pip install -r requirements.txt
```

## Data Pipeline
The application employs a data pipeline that performs several operations to prepare the data for visualization:

- **Starting the pipeline:** A copy of the original dataset is made to ensure data integrity.
- **Conversion to DateTime:** The 'date' column is converted to DateTime format for time series analysis.
- **Adding time series features:** Several time-based features are extracted such as the weekday, week number, month, and hour.
- **Adding Features:** Based on the data, new features are added like 'victim_outcome', 'non_fatal', and 'shooting_incidents'.
- **Dropping missing data:** Rows with missing 'dist' (district) values are dropped to maintain data accuracy.

## Visualizations
The application includes the following visualizations:

- **Shootings Per Year Bar Chart:** Displays the number of shootings each year, segmented by the victim outcome (fatal or non-fatal).
- **Shootings Per Month Bar Chart:** Shows the number of shootings each month.
- **Shootings Heatmap:** A heatmap that displays shootings data across different time dimensions.
- **Shootings Per Hour Bar Chart:** Visualizes the number of shootings during each hour of the day.
- **Shootings Per Police District Map:** A choropleth map that presents the number of shootings in each police district.
Each visualization has interactive features, such as hover effects, to display additional data and provide more context.

## Contributing
Contributions are welcome! If you would like to contribute to this project, please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
