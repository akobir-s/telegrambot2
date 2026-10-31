from aiogram import Bot, Dispatcher, F
from aiogram.types import (Message,CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardMarkup,
                           InlineKeyboardButton, KeyboardButton )
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from models import (bot_token, connect, create_tables, ADMIN, groq_api,
                    inser_item, get_items, get_item_by_id, inser_order, get_my_orders)
from buttons import menu_buttons, cancel_button
import asyncio
from groq import Groq

client = Groq(api_key=groq_api)

bot = Bot(token=bot_token)
dp= Dispatcher()

class AddItems(StatesGroup):
    title = State()
    description = State()
    price = State()
    photo = State()


class OrderItem(StatesGroup):
    quantity = State()
    address = State()
    phone = State()


@dp.message(F.text=='/start')
async def start_bot(message: Message, state: FSMContext):
    print(message.from_user.id)
    await message.answer(f'Welcome to our bot👋{message.from_user.full_name}', reply_markup=menu_buttons())

@dp.message(F.text=='❌ Cancel')
async def add_items(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('❌ Canceled action', reply_markup=menu_buttons())

@dp.message(F.text=='📗 Menu')
async def menu_func(message: Message, state: FSMContext):
    items = await get_items()
    if not items:
        await message.answer('We dont have any items for now ')
        return
    buttons =[]
    for i in items:
        button = [InlineKeyboardButton(text=f"{i['title']}, {i['price']}tjk", callback_data=f"item:{i['id']}")]  # item:
        buttons.append(button)

    items_button = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(f'Please order from below', reply_markup=items_button)

@dp.message(F.text=='🛒 My Orders')
async def menu_func(message: Message, state: FSMContext):
    items = await get_my_orders(message.from_user.id)
    print(items)
    if not items:
        await message.answer('U  dont have any orders for now ')
        return
    text = ''
    for i in items:
        text += f'{i["title"]}\n {i["quantity"]}\n\n'


    await message.answer(text)


@dp.callback_query(F.data.startswith('item:'))
async def order(call: CallbackQuery, state: FSMContext):
    item_id = int(call.data.split(':')[1])   #data = item:1 --> [item, 1]
    item = await get_item_by_id(item_id)
    order = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅Order now', callback_data=f'order:{item["id"]}')]
    ])
    await call.message.answer_photo(photo=item['photo'],
            caption=f'Title: {item["title"]}\n'
                    f'Description: {item["description"]}\n'    
                    f'Price: {item["price"]} in somini'    
                , reply_markup=order)
    await call.message.delete()



@dp.callback_query(F.data.startswith('order:'))
async def order(call: CallbackQuery, state: FSMContext):
    item_id = int(call.data.split(':')[1])   #order 1
    await state.update_data(item_id = item_id)
    await call.message.answer('Engter quantity u want to order', reply_markup=cancel_button())
    await call.message.delete()
    await state.set_state(OrderItem.quantity)





@dp.message(OrderItem.quantity)
async def add_items(message: Message, state: FSMContext):
    if not message.text.isdigit() or  not int(message.text)>0:
        await message.answer('quantity shodu be a interger')
        return
    await state.update_data(quantity=int(message.text))
    await message.answer(f'Enter address for order ')
    await state.set_state(OrderItem.address)

@dp.message(OrderItem.address)
async def add_items(message: Message, state: FSMContext):
    if len(message.text)<5:
        await message.answer('Enter ur address fully it shodu be nmore then 5 letters')
        return
    await state.update_data(address=(message.text))
    await message.answer(f'Enter phone for order ')
    await state.set_state(OrderItem.phone)

@dp.message(OrderItem.phone)
async def add_items(message: Message, state: FSMContext):
    if len(message.text)<9:
        await message.answer('Enter ur phone fully it shodu be nmore then 9 letters')
        return
    data = await state.get_data()
    id = message.from_user.id
    try:
        await inser_order(id, message.text,data['address'], data['quantity'], data['item_id'] )
        await message.answer(f'Order  added successfully\n{data["address"]}', reply_markup=menu_buttons())
    except Exception as e:
        print(e, 'failed addign order')
        await message.answer(f'Order added failed\nTry again never give up', reply_markup=menu_buttons())
    finally:
        await state.clear()
    
    

@dp.message(F.text=='➕ Add Item', F.from_user.id==ADMIN)
async def add_items(message: Message, state: FSMContext):
    await message.answer(f'Enter Items title u want to add', reply_markup=cancel_button())
    await state.set_state(AddItems.title)


@dp.message(AddItems.title)
async def add_items(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(f'Enter Items description u want to add')
    await state.set_state(AddItems.description)

@dp.message(AddItems.description)
async def add_items(message: Message, state: FSMContext):
    if len(message.text) <3:
        await message.answer('Description shoudl be more then 3 letters')
        return
    await state.update_data(description=message.text)
    await message.answer(f'Enter Items price u want to add')
    await state.set_state(AddItems.price)

@dp.message(AddItems.price)
async def add_items(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except Exception as e:
        await message.answer('Price shodul be a number like 87.9')
        return
    
    await state.update_data(price=price)
    await message.answer(f'Send  Items photo u want to add')
    await state.set_state(AddItems.photo)

@dp.message(AddItems.photo, F.photo)
async def add_items(message: Message, state: FSMContext):
    photo_url = message.photo[-1].file_id
    print(photo_url, 'id file in telegram server')
    data =  state.get_data()
    try:
        await inser_item(data['title'],data['description'], data['price'], photo_url )
        await message.answer(f'Item added successfully\n{data["title"]}', reply_markup=menu_buttons())
    except Exception as e:
        print(e, 'failed addign item')
        await message.answer(f'Item added failed\nTry again never give up', reply_markup=menu_buttons())
    finally:
        await state.clear()

@dp.message()
async def ai_answer(message: Message):
    items = await get_items()
    text = ''
    for i in items:
        text += f" title:{i['title']},  description:{i['description']}, price:{i['price']}in somini \n"

    promt = f""" You are telegrambot ai ur name is Softbot that help clients to choose
    item from our restaratn and eat
    so be kind answer them in langguage they speak  mostly ur users aer from tajikistan
    so speak tajik langauge correctly and wel
    dont speak from urslef dont lie speak only what u know dont add smth fromurself
    user emoji like humans  
    THE TEXT that u want to look good for exampole bold or else we are coding in aiogram use html tegs that except aiogram they are only 4 
    DONT LIE ABOUT MENU ONLY SUGGEST FROM OUR MENU 
    HERE IS MENU FOR U {text}
    U CAN ANSER USER WITH HIS LANGAUGE IF HE WANT TO ORDER SMTH TELL HIM USE BUTTON 📗 Menu FOR SEE PHOTO AND DETAIL
    INFO OF ITEM AND IF HE WANT TO ORDER PUSH THE BUTTON OF ✅Order now 
    ONNLY ANSER QUETSION THAT ARE ABOUT OUR RESTARAUTN 

    """
    response = client.chat.completions.create(
        model='openai/gpt-oss-120b',
        messages=[
            {'role':'user', 'content': message.text},
            {'role':'system', 'content':promt},
        ]
    )
    await message.answer(response.choices[0].message.content, parse_mode='HTML')

    

async def main():
    await connect()
    await create_tables()
    print('bot started')
    await dp.start_polling(bot)



if __name__ =='__main__':
    asyncio.run(main())



