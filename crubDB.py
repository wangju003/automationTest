# 插入数据 data->table
def insertDB(tablename, data):
    import pandas as pd
    # from demo.demogetConnection import GetConnection
    from getConnection import GetConnection

    engine = GetConnection.engine

    df = pd.DataFrame(data)
    df.to_sql(tablename, con=engine, if_exists="append", index=False)