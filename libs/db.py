import sqlite3

class WalletDatabase:
    def __init__(self, table) -> None:
        self.connection = sqlite3.connect(f"../data/data.db")
        self.table = table
        self.cursor = self.connection.cursor()

    async def create_table(self, column_info:dict):
        columns = ""
        for i, v in column_info.items():
            columns += f'{i} {v},'

        columns = columns[:-1]

        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.table} ({columns});""")

        self.connection.commit()

    async def insert_into_table(self, values:dict): 
        insert_data = tuple(values.values())
        self.cursor.execute(f"""INSERT INTO {self.table} VALUES({', '.join(['?'] * len(insert_data))})""", insert_data)
        self.connection.commit()

    async def get_row_data(self, condition:str, value:str):
        return self.cursor.execute(f"""SELECT * FROM {self.table} WHERE {condition} = ?""", (value,)).fetchall()
    
    async def get_table_data(self):
        return self.cursor.execute(f"""SELECT * FROM {self.table}""").fetchall()
    
    async def update_row_data(self, update_column:str, condition_column:str, update_value:str, condition_value:str):
        self.cursor.execute(f"""UPDATE {self.table} SET {update_column} = ? WHERE {condition_column} = ?""", (update_value, condition_value))
        self.connection.commit()

    async def get_user_balance(self, user_id: int):
        row_data = await self.get_row_data('user_id', user_id)
        dict_format = await self.dict_format(row_data[0])
        return dict_format['wallet_balance']

    async def profit_accounts(self):
        return self.cursor.execute(f"""SELECT * FROM {self.table} WHERE wallet_balance >= ?""", (10,)).fetchall()
    
    async def dict_format(self, data:tuple):
        if self.table == "wallet_data":
            return {
                'user_id': data[0],
                'wallet_balance': data[1]
            }