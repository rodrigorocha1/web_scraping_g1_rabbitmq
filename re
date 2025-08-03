# import logging
# import sqlite3
#
# class DBHandler(logging.Handler):
#     def __init__(self, db_path='logs.db'):
#         super().__init__()
#         self.conn = sqlite3.connect(db_path)
#         self.cursor = self.conn.cursor()
#         self._create_table()
#
#     def _create_table(self):
#         self.cursor.execute('''
#             CREATE TABLE IF NOT EXISTS logs (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 level TEXT,
#                 message TEXT,
#                 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )
#         ''')
#         self.conn.commit()
#
#     def emit(self, record):
#         log_entry = self.format(record)
#         self.cursor.execute(
#             'INSERT INTO logs (level, message) VALUES (?, ?)',
#             (record.levelname, log_entry)
#         )
#         self.conn.commit()
#
#     def close(self):
#         self.conn.close()
#         super().close()
#
#
# # Configurando o logger com o handler do banco
# logger = logging.getLogger('meu_logger_db')
# logger.setLevel(logging.DEBUG)
#
# db_handler = DBHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
# db_handler.setFormatter(formatter)
#
# logger.addHandler(db_handler)
#
# # Usando o logger normalmente
# logger.info("Teste de log no banco!")
# logger.error("Erro gravado no banco!")