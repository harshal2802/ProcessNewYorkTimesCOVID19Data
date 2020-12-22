import pandas as pd
from newyork_times_covid19_data_processing import *

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

# -----------------------------main function --------------------------


def main():
    """
    """
    # Step 1 Get input arguments
    args = get_command_line_args()

    # Step 2 Get input data from source
    df_covid = pd.read_csv(args.covid19_csv_path, dtype=object)

    df_population = pd.read_csv(
        args.population_csv_path, dtype=object, encoding="ISO-8859-1")

    # Step 3 Clean input data
    df_covid = preprocess_covid19_df(df_covid)

    df_population = preprocess_population_df(df_population)

    # Step 4
    df_combined = combine_data(df_covid, df_population)

    # Step 5
    df_stats = calculate_stats(df_combined)

    # Step 6
    df_stats.to_csv(args.output_file_path)


if __name__ == "__main__":
    main()
