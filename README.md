<h1 align="center">Paper SOL Trader</h1>
<div class="heading" align="center">
  <div class="links">
    <a href="https://linkedin.com/in/colin-rob"><img src="https://img.shields.io/badge/LinkedIn-blue?logo=linkedin" alt="website"/></a>
    <a href="https://github.com/crobinson-dev"><img src="https://img.shields.io/badge/Github-white?logo=github&logoColor=000000" alt="website"></a>
    <a href="https://crobinson.dev"><img src="https://img.shields.io/badge/Website-black?logo=framer&logoColor=ffffff" alt="website"></a>
    <a href="https://ko-fi.com/crobinson_dev"><img src="https://img.shields.io/badge/KoFi-red?logo=kofi&logoColor=ffffff" alt="website"></a>
  </div>
  
  <i>Paper Trade Solana in Telegram</i>
  <img alt="paper_sol" src="assets/paper_sol.png"> </img>

  <a href="https://github.com/crobinson-dev/Paper-SOL/stargazers"><img src="https://img.shields.io/github/stars/crobinson-dev/Paper-SOL" alt="Stars Badge"/></a>
  <a href="https://github.com/crobinson-dev/Paper-SOL/network/members"><img src="https://img.shields.io/github/forks/crobinson-dev/Paper-SOL" alt="Forks Badge"/></a>
  <a href="https://github.com/crobinson-dev/Paper-SOL/pulls"><img src="https://img.shields.io/github/issues-pr/crobinson-dev/Paper-SOL?color=ffccff" alt="Pull Requests Badge"/></a>
  <a href="https://github.com/crobinson-dev/Paper-SOL/issues"><img src="https://img.shields.io/github/issues/crobinson-dev/Paper-SOL?color=ffccff" alt="Issues Badge"/></a>
  <a href="https://github.com/crobinson-dev/Paper-SOL/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/crobinson-dev/Paper-SOL?color=ffccff"></a>
  <a href="https://github.com/crobinson-dev/Paper-SOL/blob/master/LICENSE"><img src="https://img.shields.io/github/license/crobinson-dev/Paper-SOL?color=ffccff" alt="License Badge"/></a>

</div>

### Categories
  - [Introduction](#introduction)
  - [Categories](#categories-)
    - [Buy 🪙](#buy-)
    - [Sell 📈](#sell-)
    - [New Pairs 🌱](#new-pairs-)
  - [Packages](#packages-)

## Introduction
Paper SOL is a python program that utilizes the Telegram API to use the interface to interact with users. It uses markups and database systems to ttrack the user's current balance. 

#### How It Works
1. Download the required python packages using the following command:
```
pip install -m requirements.txt
```
2. Contact @BotFather on Telegram to receive a Telegram Bot Token
3. Copy the Bot Token and Paste into the *.env* file in your local directory
4. Run the following command to start the program:
```
python main.py
```
5. Message your bot to get started

## Categories

#### Buy 🪙

1. Following the **Buy** Markup the Bot will prompt for an SPL Token Contact Address
2. The Bot will then search the *solana.fm* API for the SPL Token information including name and price
3. The Bot will then ask how much SOL to put in by Solana amount or percent of current SOL Balance
4. It will then add the purchase to the dictionary

#### Sell 📈

1. Following the **Sell** Markup the Bot will prompt for a 
2. The Bot will then search the *solana.fm* API for the SPL Token information including name and price
3. The Bot will then ask how much SOL to put in by Solana amount or percent of current SOL Balance
4. It will then sell the token and remove it from the dictionary

#### New Pairs 🌱

Upon clicking the New Pairs the program will open the undetected chrome browser to scrape the new token data from *birdeye.so*.
It will then present all the tokens to the user with the pertinent information about the token.

## License

[![GNU](https://licensebuttons.net/l/GPL/2.0/88x62.png)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html#SEC1)
