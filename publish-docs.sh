rm -r docs/data_access_files
jupyter nbconvert notebooks/data_access.ipynb --output-dir ./docs/ --execute --to markdown
