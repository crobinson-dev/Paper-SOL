import asyncio
import logging
import sys
import requests
from time import strftime, localtime
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command , CommandObject
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from aiogram.client.default import DefaultBotProperties
from solders.pubkey import Pubkey
import os
from db import WalletDatabase
from dotenv import load_dotenv
from seleniumbase import Driver
import re

load_dotenv()

# Bot token can be obtained via https://t.me/BotFather
TOKEN = os.getenv('BOT_TOKEN')

solana_client = Client("https://api.mainnet-beta.solana.com")
current_purchase = {}

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
dp = Dispatcher()

async def number_format(num: int):
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)

async def get_dex(ca: str):
    return requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{ca}").json()['pairs'][0]

async def new_pairs(message: Message):
    driver = Driver(uc=True)
    driver.open("https://birdeye.so/new-listings?chain=solana")
    driver.sleep(10)
    source = driver.wait_for_element('div.ant-table-body')
    driver.sleep(3)
    data = source.text
    new_tokens = data.split(' ago')
    new_tokens[0] = f"\n{new_tokens[0]}"
    links = driver.find_elements('a')
    tokens = {}
    for link in links:
        try:
            link = link.get_attribute('href')
            if re.search('https://birdeye.so/token/', link):
                tokens[link.replace('?chain=solana', '').replace('https://birdeye.so/token/', '')] = ""
        except:
            pass
    for token in new_tokens:
        try:
            format_string = token.split('\n')
            addy = format_string[2][:4]
            name_symbol = format_string[1].split(' - ')
            symbol = name_symbol[0]
            token_name = name_symbol[1]
            matching = [key for key in tokens.keys() if key.startswith(addy)][0]

            other = format_string[3].split(' ')
            volume = other[3]
            fdmc = other[7]
            tokens[matching] = {'symbol': symbol, 'name': token_name, 'volume': volume, 'fdmc': fdmc}
        except:
            pass
    out_data = []
    for address in tokens:
        try:
            out_data.append(f"{tokens[address]['symbol']} | {tokens[address]['name']} ➡️ {address}\n    Volume: {tokens[address]['volume']}\n    FDMC: {tokens[address]['fdmc']}")
        except:
            pass

    out_string = '/n'.join(out_data)
    current_purchase[message.chat.id]["edit_message"] = await current_purchase[message.chat.id]["edit_message"].edit_text(out_string)

async def sol_price():
    return requests.get("https://api.diadata.org/v1/assetQuotation/Solana/0x0000000000000000000000000000000000000000").json()['Price']

async def sol_fm(ca: str):
    return requests.get(f"https://api.solana.fm/v1/tokens/{ca}").json()

async def commit_trade_action(message: Message):
    await message.delete()
    wallet_balance = await wallet.get_user_balance(message.chat.id)
    if wallet_balance >= 1:
        first_sol = "0.25 SOL"
        second_sol = "0.5 SOL"
        third_sol = "1 SOL"
    else:
        first_sol = f"{wallet_balance * 0.25:.2f} SOL"
        second_sol = f"{wallet_balance * 0.5:.2f} SOL"
        third_sol = f"{wallet_balance * 0.75:.2f} SOL"
        
    first_percent = "10%"
    second_percent = "25%"
    third_percent = "50%"
    full = f"100% | {wallet_balance:.2f} SOL"

    sol_fm_data = await sol_fm(current_purchase[message.chat.id]['token'])

    spl_value = await sol_price() * .5

    response = await get_dex(current_purchase[message.chat.id]["token"])

    spl_amount = spl_value / float(response['priceUsd'])

    sol_amounts = [InlineKeyboardButton(text=first_sol, callback_data=f'ACT-{first_sol}'), InlineKeyboardButton(text=second_sol, callback_data=f'ACT-{second_sol}'), InlineKeyboardButton(text=third_sol, callback_data=f'ACT-{third_sol}')]
    percent_amounts = [InlineKeyboardButton(text=first_percent, callback_data=f'ACT-{first_percent}'), InlineKeyboardButton(text=second_percent, callback_data=f'ACT-{second_percent}'), InlineKeyboardButton(text=third_percent, callback_data=f'ACT-{third_percent}')]
    full_amount = [InlineKeyboardButton(text=full, callback_data=f'ACT-{full}')]
    purchase_amounts = InlineKeyboardBuilder([sol_amounts, full_amount, percent_amounts])
    current_purchase[message.chat.id]["edit_message"] = await current_purchase[message.chat.id]["edit_message"].edit_text(f"Buy ${response['baseToken']['symbol'] if '$' not in response['baseToken']['symbol'] else '$'+response['baseToken']['symbol']} ― ({response['baseToken']['name']}) 📈\n`{current_purchase[message.chat.id]['token']}`\n\nBalance: *{wallet_balance:,.2f} SOL*\nPrice: *${response['priceUsd']}* ― Liquidity: *${await number_format(response['liquidity']['usd'])}* ― MC: *${await number_format(response['fdv'])}*\n1h: *{response['priceChange']['h1']}%* ― 24h: *{response['priceChange']['h24']}%*\nRenounced {'❌' if sol_fm_data['tokenMetadata']['onChainInfo']['creators'] else '✅'}\n\n*0.5 SOL (${spl_value:,.2f})* ⇆ *{spl_amount:,.0f} {response['baseToken']['symbol']} (${spl_value:,.2f})*\n\nLiquidity SOL: *{await number_format(response['liquidity']['quote'])}*", reply_markup=purchase_amounts.as_markup())

async def referral_menu():
    menu = InlineKeyboardBuilder([[InlineKeyboardButton(text=f"⬅ Back", callback_data='refresh_start'), InlineKeyboardButton(text="↺ Refresh", callback_data="refresh_referral")]])
    return menu

async def start_menu():
    trade_keyboard = [InlineKeyboardButton(text=f"Buy", callback_data='buy_token'), InlineKeyboardButton(text=f"Sell", callback_data="sell_token")]
    new_pairs_keyboard = [InlineKeyboardButton(text=f"🌱 New Pairs", callback_data='new_pairs')]
    settings_keyboard = [InlineKeyboardButton(text="Referral", callback_data="refresh_referral"), InlineKeyboardButton(text="↺ Refresh", callback_data="refresh_start")]
    
    menu = InlineKeyboardBuilder([trade_keyboard, new_pairs_keyboard, settings_keyboard])
    return menu

async def check_token(ca: str):
    return True if requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{ca}").json()['pairs'] else False

@dp.message(Command("start"))
async def command_start(message: Message, command: CommandObject):
    wallet_balance = await wallet.get_user_balance(message.from_user.id)
    menu = await start_menu()
    message_sent = await message.answer(f"*Solana*\nBalance: `{wallet_balance:.2f} SOL (${await sol_price() * wallet_balance:,.2f})`\n\nClick on the Refresh button to update your current balance.\n\nJoin our Telegram group @papertradesol for accouncements.\n\n⚠️@PaperSolBot is for educational and practical use. Your SOL wallet and balance is virtual and not on the Solana network. For more information please join our telegram group @papertradesol.", reply_markup=menu.as_markup(), parse_mode="Markdown")
    current_purchase[message.from_user.id] = {"edit_message": message_sent}

@dp.callback_query()
async def on_callback(query: CallbackQuery):
    if query.data == "buy_token":
        current_purchase[query.from_user.id]['action'] = "buy"
        message_sent = await current_purchase[query.from_user.id]['edit_message'].edit_text(f"Please give a valid contract address:", parse_mode="Markdown")
        current_purchase[query.from_user.id]['edit_message'] = message_sent
    elif query.data == "sell_token":
        current_purchase[query.from_user.id]['action'] = "sell"
        message_sent = await current_purchase[query.from_user.id]['edit_message'].edit_text(f"Please give a valid contract address:", parse_mode="Markdown")
        current_purchase[query.from_user.id]['edit_message'] = message_sent
    elif query.data == "refresh_start":
        try:
            wallet_balance = await wallet.get_user_balance(query.from_user.id)
            menu = await start_menu()
            message_sent = await current_purchase[query.from_user.id]['edit_message'].edit_text(f"*Solana*\nBalance: `{wallet_balance:.2f} SOL (${await sol_price() * wallet_balance:,.2f})`\n\nClick on the Refresh button to update your current balance.\n\nJoin our Telegram group @papertradesol for accouncements.\n\n⚠️@PaperSolBot is for educational and practical use. Your SOL wallet and balance is virtual and not on the Solana network. For more information please join our telegram group @papertradesol.", reply_markup=menu.as_markup(), parse_mode="Markdown")
            current_purchase[query.from_user.id]['edit_message'] = message_sent
        except:
            pass
    elif query.data == "new_pairs":
        await new_pairs()
    elif query.data == "refresh_referral":
        try:
            menu = await referral_menu()
            message_sent = await current_purchase[query.from_user.id]['edit_message'].edit_text(f"`Coming Soon...`\n\nClick on the Refresh button to update your current balance.\n\nJoin our Telegram group @papertradesol for accouncements.\n\n⚠️@PaperSolBot is for educational and practical use. Your SOL wallet and balance is virtual and not on the Solana network. For more information please join our telegram group @papertradesol.", reply_markup=menu.as_markup(), parse_mode="Markdown")
            current_purchase[query.from_user.id]['edit_message'] = message_sent
        except:
            pass
    if query.data.startswith("ACT-"):
        if query.data.endswith(" SOL"):
            sol_amount = int(query.data.replace("ACT-", "").split(" ")[-2])
            print(sol_amount)
        elif query.data.endswith("%"):
            percent = query.data.replace("ACT-", "")

            wallet_balance = await wallet.get_user_balance(query.from_user.id)
            sol_amount = wallet_balance * (int(percent.split("%")[0]) / 100)
            print(sol_amount)

@dp.message()
async def message_handler(message: Message):
    if message.from_user.id in current_purchase:
        if current_purchase[message.from_user.id]['action']:
            if await check_token(message.text):
                current_purchase[message.chat.id]['token'] = message.text
                await commit_trade_action(message)


async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    wallet = WalletDatabase('wallet_data')
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())