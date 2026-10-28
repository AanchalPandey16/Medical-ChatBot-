import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("""
               create table if not exists conversations (
                   id integer primary key autoincrement,
                   title text not null,
                   created_at timestamp default current_timestamp
               )            
               """)

cursor.execute("""
               create table if not exists messages (
                   id integer primary key autoincrement,
                   conversation_id integer not null,
                   role text not null,
                   content text not null, 
                   foreign key(conversation_id) references conversations(id)
               )
               """)

conn.commit()
conn.close()
print("Database and tables created successfully.")