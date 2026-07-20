from datetime import datetime

def get_date_filter_sql(start_date: str = None, end_date: str = None, date_column: str = "date") -> tuple:
    """
    Generates SQL filter clause and parameters for date range.
    Example return: ("AND date BETWEEN ? AND ?", ["2023-01-01", "2023-12-31"])
    """
    conditions = []
    params = []
    if start_date:
        conditions.append(f"{date_column} >= ?")
        params.append(start_date)
    if end_date:
        conditions.append(f"{date_column} <= ?")
        params.append(end_date)
    
    sql = " AND ".join(conditions)
    return (f"AND {sql}" if sql else "", params)
