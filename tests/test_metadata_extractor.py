import pandas as pd

from src.tools.metadata_extractor import extract_metadata

def main():

    dataframe = pd.read_csv("data/sample_superstore.csv",encoding="cp1252")

    metadata = extract_metadata(dataframe)

    print("\n===== Dataset Metadata =====\n")

    for key, value in metadata.items():
        print(f"{key}:\n{value}\n")


if __name__ == "__main__":
    main()