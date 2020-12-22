import argparse
import pandas as pd

# --------------------- Get Command line arguments---------------------


def get_command_line_args():
    """
    Function to read command line arguments

    Returns:
    -------
    args: object with following arguments
        - covid19_csv_path: string, URL/Path for latest data from
                            New York Times COVID-19 Data
        - population_csv_path: string, URL/Path for 2019
                                Population Estimate Data
        - output_file_path: string, Path of output csv file
    """
    parser = argparse.ArgumentParser(
        description="""Prepare Covid19 cases summary with population
                        for New York Times COVID-19 Data""")

    parser.add_argument(
        '--covid19_csv_path',
        type=str,
        default="https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv",
        help="URL/Path for latest data from New York Times COVID-19 Data")

    parser.add_argument(
        '--population_csv_path',
        type=str,
        default="https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv",
        help="URL/Path for 2019 Population Estimate Data")

    parser.add_argument(
        '--output_file_path',
        type=str,
        default="./aggregated_covid19_data_with_population.csv",
        help="Path of output csv file")

    args = parser.parse_args()
    return args

# ----------------------Clean Data-------------------------------------


def preprocess_covid19_df(df_covid: pd.DataFrame) -> pd.DataFrame:
    """
    Function to preprocess New York times covid 19 data

    Explanation:
        Drop records with null values: Drop records with null values in
            "fips", "date", "cases", "deaths" columns
        Typecast to integer: cases and deaths to integer
        Typecast date to datetime64[ns]

    Parameters:
    ----------
    df: pd.Datafame object with New York Times COVID-19 Data having
        columns:
            fips: string
            date: string
            county: string
            state: string
            cases: string, The total number of cases of Covid-19, 
                    including both confirmed and probable
            deaths: string, The total number of deaths from Covid-19,
                    including both confirmed and probable. 
    Returns:
    -------
    df: pd.Datafame object with preprocessed New York Times COVID-19 
        Data having columns:
            fips: string
            date: datetime64[ns]
            cases: integer
            deaths: integer
    """
    feature_list = ["fips", "date", "cases", "deaths"]

    # feature selection
    df_covid = df_covid[feature_list]

    df_covid = df_covid.dropna(subset=feature_list)

    df_covid = df_covid.astype(dtype={"cases": int,
                                      "deaths": int,
                                      "date": "datetime64[ns]"})
    return df_covid


def preprocess_population_df(df_population: pd.DataFrame) \
        -> pd.DataFrame:
    """
    Function to preprocess the Population Estimate Data 2019

    Explanation:
        generate fips code: combine "STATE" and "COUNTY" columns
            to generate fips code
        typecast POPESTIMATE2019: typecast "POPESTIMATE2019" as integer

    Parameters:
    ----------
    df_population: pd.DataFrame object having Population Estimate Data 2019
    with columns:
            "STATE":string
            "COUNTY":string
            "POPESTIMATE2019":string

    Returns:
    -------
    df_population: pd.DataFrame object having Population Estimate Data 2019
    with columns:
            "POPESTIMATE2019":integer
            "fips":string
    """
    # columns to keep
    feature_list = ["fips", "POPESTIMATE2019"]

    # create fips code by concatenating STATE and COUNTY codes
    df_population["fips"] = df_population["STATE"].str.strip() \
        + df_population["COUNTY"].str.strip()

    df_population = df_population.astype(dtype={"POPESTIMATE2019": "int"})

    return df_population[feature_list]

# ----------Combine Covid19 data with population estimate--------------


def combine_data(df_covid: pd.DataFrame, df_population: pd.DataFrame)\
        -> pd.DataFrame:
    """
    Function to combine covid19 data with population data using
    left join on "fips" column

    Explanation: We are applying the left join because we need
    latest population estimate data from df_population. The combined
    dataframe can later be used for generating the stats

    Parameter:
    ---------
    df_covid: pd.DataFrame object with processed New York Times
        COVID-19 Data having columns:
            "fips": string
            "date": datetime64[ns]
            "cases": integer
            "deaths": integer

    df_population: pd.DataFrame object with Population Estimate
        Data 2019 having columns:
            "fips": string
            "POPESTIMATE2019": integer
    Returns:
    -------
    df_combined: pd.DataFrame object with combined data having
        columns:
            "fips": string
            "date": datetime64[ns]
            "cases": integer
            "deaths": integer
            "POPESTIMATE2019": integer
    """
    #
    df_combined = df_covid.merge(df_population, on="fips", how="left")

    feature_list = ["fips", "date", "cases", "deaths", "POPESTIMATE2019"]

    return df_combined[feature_list]

# -----------Calculate Statistics on combined dataframe----------------


def calculate_stats_by_county(df_county: pd.DataFrame) -> pd.DataFrame:
    """
    Function to generate statistics for filtered dataframe by fips code

    Explanation:
    -----------
        - population: Updated population estimate by including cumulative
        deaths into account.
        - daily_cases: Total number of daily cases for a given date and fips.
        - daily_deaths:Total number of daily cases for a given date and fips.
        - cumulative_cases_to_date: It is same as cases, i.e. The total
        number of cases of Covid-19, including both confirmed and probable.
        - cumulative_deaths_to_date: It is same as cases, i.e. The total
        number of cases of Covid-19, including both confirmed and probable.

    Parameters:
    ----------
    df: pd.DataFrame object with data filtered by fips code from
        combined dataframe having following columns:
            "date": datetime64[ns]
            "cases": integer
            "deaths": integer
            "POPESTIMATE2019": integer
    Returns:
    ----------
    df: pd.DataFrame object with generated stats on the data filtered
        by fips code from combined dataframe having following columns:
            "date": datetime64[ns]
            "population":integer
            "daily_cases":integer
            "daily_deaths":integer
            "cumulative_cases_to_date":integer
            "cumulative_deaths_to_date":integer
    """
    df_county = df_county.sort_values(by="date")
    df_county.index = df_county.date

    # calculate daily cases count
    # daily_cases[i] = cases[i]-cases[i-1] except value at 0th index
    # Assumption:
    #  - Date column is contious that is there is no missing date value
    #  in entire filtered dataframe by fips code
    #  - The value in Date column is sorted increasing order
    df_county["daily_cases"] = df_county['cases'] - \
        df_county['cases'].shift(fill_value=0)

    # calculate daily deaths count
    df_county["daily_deaths"] = df_county['deaths'] - \
        df_county['deaths'].shift(fill_value=0)

    # rename columns
    df_county.rename(columns={"cases": "cumulative_cases_to_date",
                              "deaths": "cumulative_deaths_to_date"},
                     inplace=True)
    # calculate updated population to date
    df_county["population"] = (df_county["POPESTIMATE2019"]
                               - df_county["cumulative_deaths_to_date"])

    # keep only required columns
    feature_list = ["population", "daily_cases",
                    "daily_deaths", "cumulative_cases_to_date",
                    "cumulative_deaths_to_date"]

    df_county = df_county[feature_list]

    return df_county


def calculate_stats(df_combined: pd.DataFrame) -> pd.DataFrame:
    """
    Function to generate statistics defined in "calculate_stats"
    function for each fips code in combined dataframe

    Parameters:
    ----------
    df: pd.DataFrame object with combined data having
        columns:
            "fips": string
            "date": datetime64[ns]
            "cases": integer
            "deaths": integer
            "POPESTIMATE2019": integer

    Returns:
    -------
    df: pd.DataFrame object with generated statistics on combined
        dataframe having following columns:
            "fips": string
            "date": datetime64[ns]
            "population":integer
            "daily_cases":integer
            "daily_deaths":integer
            "cumulative_cases_to_date":integer
            "cumulative_deaths_to_date":integer
    """

    df = df_combined.groupby("fips")\
        .apply(lambda df_fips: calculate_stats_by_county(df_fips))

    feature_list = ["population", "daily_cases",
                    "daily_deaths", "cumulative_cases_to_date",
                    "cumulative_deaths_to_date"]
    df = df[feature_list]

    return df
