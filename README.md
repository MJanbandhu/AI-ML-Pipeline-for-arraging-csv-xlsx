# AI-ML-Pipeline-for-arraging-csv-xlsx
This is only for expiremeting
## Project name: AI/ML Data Format Alignment Pipeline.
Purpose: take a schema file called data1 (only its column names and order matter), take a content file called data2 (its columns may be messy or different), then produce outputdata that is strictly aligned to the schema of data1.
How it works: the program reads both files, builds a column mapping from data1 columns to the closest matching data2 columns using fuzzy matching, creates a new dataframe with the exact column order from data1, fills each target column with the values from the matched data2 column, and leaves a column blank if there is no suitable match.
What you get in Jupyter: two upload widgets, a format selector, a Run button, a printed mapping table, a preview of the first rows of the aligned dataframe, and a download link for the generated file.
Supported formats: CSV and Excel (.xlsx and .xls).
Dependencies: Python 3.9+ recommended, pandas, numpy, ipywidgets, jupyter, openpyxl (for Excel).
Run in Jupyter: open a notebook, paste the Jupyter code, run the cell, upload data1 and data2, click Run Pipeline, then download the result.
Notes: the mapping is fuzzy by column name similarity; typos and spacing differences are handled. If a schema column cannot be matched, the output column is present and empty.

### Code information (Jupyter UI)

The code defines three main parts.
align_data takes the data1 dataframe and the data2 dataframe and returns an aligned dataframe and the mapping used.
preview_and_download prints the mapping, shows a head preview, writes the file to disk as CSV or Excel, and exposes a download link.
The UI block builds two upload widgets, an output-format dropdown, a Run button, and an output area; when the button is clicked, it reads the uploaded files, runs the alignment, then shows the preview and the download link.