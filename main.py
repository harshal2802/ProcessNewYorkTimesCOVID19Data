import pandas as pd
from newyork_times_covid19_data_processing import *


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
