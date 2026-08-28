import pandas as pd

from logger import logger


def read_file() -> pd.DataFrame:
    input_path = "data/Search Keyword Lists.xlsx"
    logger.info("Reading keyword workbook: %s", input_path)
    
    try:
        df = pd.read_excel(input_path)
    except Exception:
        logger.exception("Failed to read keyword workbook: %s", input_path)
        raise
    logger.info("Read %d rows from keyword workbook", len(df))
    return df

if __name__ == "__main__":
    read_file()