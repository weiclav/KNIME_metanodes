# Volcano_plot

## About
Volcano plot is an interactive application in Python for the data visualization.

You have to provide data columns for p-value and log fold change. Rows containing missing values are removed. In case of p-value = 0, there is imputed the minimal value in the given dataset or it is possible specify the replacement value in the application.

You can also specify other columns for annotations.

It starts the simple python webserver inside the Volcano plot application folder and opens the browser with the interactive Volcano plot application. 

The application contains a form for setting the input data, Volcano plot, summary table, table of selected proteins from graph and table with dataset, which can be filtered. The graph shows the filtered data from the last table.

## Local Deployment
1. Clone the repository using ```git clone``` or download and extract the [ZIP file](https://github.com/OmicsWorkflows/KNIME_metanodes).
2. Open terminal in the folder with volcano_plot.py, install pipenv and run ```pipenv install``` for creating virtualenv and installing dependencies from Pipfile.lock.
3. Run application using ```pipenv run python volcano_plot.py``` or ```pipenv run python volcano_plot.py -f 'filepath'``` if you want to import your data from terminal.
4. View Volcano plot in your browser at [localhost:8050]( http://127.0.0.1:8050/).

## List of used program and extensions and the respective licences
- Python 3 (The Python consists of the following Python 3.6 License. Licence terms are available here: https://docs.python.org/3.6/license.html)
- Dash (The Dash consists of the following MIT License. Licence terms are available here: https://github.com/plotly/dash/blob/master/LICENSE)
- Dash-bio (The dash-bio consists of the following MIT License. Licence terms are available here: https://github.com/plotly/dash-bio/blob/master/LICENSE
