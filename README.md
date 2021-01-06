# About

- Runs a comparison of the commodity codes in the UK database against those in the XI database
- Purpose is to align the two datasets

### Usage

`python3 main.py record`

Runs through the two database and extracts commodity codes per given date into CSVs (one per initial digit)

`python3 main.py`

Runs the comparison

### Environment variables

| Variable    | Usage                    |
| ----------- | ------------------------ |
| USERNAME    | User name for database   |
| PASSWORD    | Password for database    |
| DATABASE_UK | URI to UK database       |
| DATABASE_XI | URI to XI database       |
| REF_DATE    | Date on which to compare |

