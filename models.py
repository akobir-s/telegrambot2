import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
ADMIN = int(os.getenv('ADMIN'))
conn = None

async def connect():
    global conn
    try:
        conn = await asyncpg.create_pool(
            database=os.getenv('DATABASE'),
            user=os.getenv('DB_USER'),
            port=os.getenv('PORT'),
            host=os.getenv('HOST'),
            password=os.getenv('DB_PASSWORD'),
        )
        print('connection successfullhy')
    except Exception as e:
        print(e, 'conencting failed')



async def create_tables():
    try:
        await conn.execute("""CREATE TABLE IF NOT EXISTS items(
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            price NUMERIC(10, 2) NOT NULL CHECK(price >=0),
            photo VARCHAR(255) 
        );
        CREATE TABLE IF NOT EXISTS orders(
            id SERIAL PRIMARY KEY,
            tg_id BIGINT NOT NULL,
            address VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            item_id INT REFERENCES items(id) ON DELETE CASCADE,            
            quantity INT NOT NULL CHECK(quantity >0)            
        );
        """)
        print('Tables are created')
    except Exception as e:
        print('tables creation failed', e)



   
    
async def inser_item(title, description, price, photo):
        await conn.execute(""" INSERT INTO items(title, description, price, photo) VALUES($1, $2, $3, $4)
        """, title, description, price, photo)
        print('Item added')

async def get_items():
        items =  await conn.fetch("""SELECT * FROM items""",)
        return items
    
async def get_item_by_id(item_id):
        item =  await conn.fetchrow("""SELECT * FROM items where id = $1""",item_id)
        return item
    

async def inser_order(tg_id, phone, address, quantity, item_id):
        await conn.execute(""" INSERT INTO orders(tg_id, phone, address, quantity, item_id) VALUES($1, $2, $3, $4, $5)
        """, tg_id, phone, address, quantity, item_id)
        print('Item added')





async def get_my_orders(tg_id):
        items =  await conn.fetch("""SELECT o.*, i.title FROM orders o join items i on i.id = o.item_id where tg_id =$1 """,tg_id)
        return items