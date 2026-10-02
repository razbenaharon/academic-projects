# Stocks: SQL and Django Coursework

Schemas, queries and views for stock/investor data, plus Django models and views integrating SQL results.

## Contribution and provenance

`sql/` stores the SQL coursework; `django/` preserves the submitted app files and templates. Query helper files with .py extensions contain SQL text, not a separate data-science pipeline.

## Running

Use a database matching the SQL dialect/schema and wire the app into a configured Django project. The SQL includes SQL Server constructs such as ISNULL; do not assume SQLite compatibility.

## Evidence and limits

The original submission is a partial app: manage.py, settings and complete project configuration are absent. It is not advertised as a standalone deployable web application.

Imported coursework outputs and personal submission metadata have been removed from the public copy. The original OneDrive materials were not edited.
