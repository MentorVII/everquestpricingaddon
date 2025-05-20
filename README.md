# EverQuest Vendor Calculator

A simple tool to calculate the total vendor value of items in your EverQuest character's inventory.

## Installation

1. Download the `EQ Vendor Calculator.exe` file
2. **Important Security Step**: Before running the application:
   - Right-click on the `EQ Vendor Calculator.exe` file
   - Select "Properties"
   - At the bottom of the Properties window, check the box that says "Unblock"
   - Click "Apply" and then "OK"
   - This step is necessary because the file was downloaded from the internet

## First Time Setup

1. Run the `EQ Vendor Calculator.exe`
2. When prompted, select your EverQuest installation folder (the folder containing EQGame.exe)
3. The application will create two configuration files in the same directory:
   - `eq_calculator_config.json` (stores your EQ installation path)
   - `eq_calculator_items.json` (stores the item price list)

## Usage

1. Enter your character name
2. Select your server from the dropdown list
3. Click "Calculate Total Value" to see the total vendor value of items in your inventory
4. The grid below will show a breakdown of each item's value

## Features

- Calculates total vendor value of items in your inventory
- Supports all current EverQuest servers
- Add custom items and their prices
- Delete items from the price list
- Sort items by clicking column headers
- Reset EQ installation path if needed

## Troubleshooting

If you need to change your EverQuest installation path:
1. Click the "Reset EQ Path" button
2. Select your new EverQuest installation folder

## Notes

- The application looks for inventory files in the format: `CharacterName_Server-Inventory.txt`
- Make sure your inventory file is in your EverQuest installation directory
- Item prices are stored locally and can be customized 