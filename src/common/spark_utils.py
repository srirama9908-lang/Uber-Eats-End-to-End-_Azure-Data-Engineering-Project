def standardize_columns(df):
    for c in df.columns:
        column_name = c.strip()

        if " " in column_name:
            column_name = column_name.lower().replace(" ", "_")
        else:
            column_name = column_name.lower()

        df = df.withColumnRenamed(c, column_name)

    return df