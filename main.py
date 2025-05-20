import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import re
import json
import os

class AddItemDialog:
    def __init__(self, parent, item_prices, on_save):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Item")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.item_prices = item_prices
        self.on_save = on_save
        
        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Item name
        ttk.Label(main_frame, text="Item Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.item_name = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.item_name, width=30).grid(row=0, column=1, padx=5)
        
        # Price input
        ttk.Label(main_frame, text="Price:").grid(row=1, column=0, sticky=tk.W, pady=5)
        price_frame = ttk.Frame(main_frame)
        price_frame.grid(row=1, column=1, sticky=tk.W)
        
        self.plat_var = tk.StringVar(value="0")
        self.gold_var = tk.StringVar(value="0")
        self.silver_var = tk.StringVar(value="0")
        self.copper_var = tk.StringVar(value="0")
        
        ttk.Entry(price_frame, textvariable=self.plat_var, width=5).pack(side=tk.LEFT)
        ttk.Label(price_frame, text="p").pack(side=tk.LEFT, padx=2)
        ttk.Entry(price_frame, textvariable=self.gold_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(price_frame, text="g").pack(side=tk.LEFT, padx=2)
        ttk.Entry(price_frame, textvariable=self.silver_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(price_frame, text="s").pack(side=tk.LEFT, padx=2)
        ttk.Entry(price_frame, textvariable=self.copper_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(price_frame, text="c").pack(side=tk.LEFT, padx=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_item(self):
        try:
            # Get values
            name = self.item_name.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter an item name!")
                return
            
            # Check for case-insensitive duplicates
            for existing_item in self.item_prices.keys():
                if name.lower() == existing_item.lower():
                    messagebox.showerror("Error", f"An item with this name already exists: {existing_item}")
                    return
            
            # Convert price to copper
            plat = int(self.plat_var.get() or "0")
            gold = int(self.gold_var.get() or "0")
            silver = int(self.silver_var.get() or "0")
            copper = int(self.copper_var.get() or "0")
            
            total_copper = (plat * 1000) + (gold * 100) + (silver * 10) + copper
            
            # Save to price list
            self.item_prices[name] = total_copper
            self.on_save()
            
            messagebox.showinfo("Success", f"Added {name} to price list!")
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for the price!")

class DeleteItemsDialog:
    def __init__(self, parent, item_prices, on_delete):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Delete Items")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.item_prices = item_prices
        self.on_delete = on_delete
        self.selected_items = set()
        
        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create Treeview for items
        columns = ('Select', 'Item Name', 'Price')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.tree.heading('Select', text='Select')
        self.tree.heading('Item Name', text='Item Name')
        self.tree.heading('Price', text='Price')
        
        # Set column widths
        self.tree.column('Select', width=50, anchor='center')
        self.tree.column('Item Name', width=250)
        self.tree.column('Price', width=250)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid the tree and scrollbar
        self.tree.grid(row=0, column=0, columnspan=2, pady=10, sticky='nsew')
        scrollbar.grid(row=0, column=2, sticky='ns')
        
        # Bind click event for checkbox column
        self.tree.bind('<ButtonRelease-1>', self.on_click)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)
        
        self.delete_button = ttk.Button(button_frame, text="Delete Selected Items", 
                                      command=self.confirm_delete, state='disabled')
        self.delete_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Populate the tree
        self.populate_tree()
    
    def populate_tree(self):
        for item_name, price in sorted(self.item_prices.items()):
            formatted_price = self.format_currency(price)
            self.tree.insert('', 'end', values=('☐', item_name, formatted_price))
    
    def on_click(self, event):
        """Handle clicks on the tree"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":  # Checkbox column
                item = self.tree.identify_row(event.y)
                if item:
                    values = self.tree.item(item)['values']
                    item_name = values[1]
                    if values[0] == '☐':
                        self.tree.item(item, values=('☑', item_name, values[2]))
                        self.selected_items.add(item_name)
                    else:
                        self.tree.item(item, values=('☐', item_name, values[2]))
                        self.selected_items.discard(item_name)
                    
                    # Update delete button state
                    self.delete_button['state'] = 'normal' if self.selected_items else 'disabled'
    
    def format_currency(self, copper):
        """Convert copper to platinum/gold/silver/copper format"""
        platinum = copper // 1000
        gold = (copper % 1000) // 100
        silver = (copper % 100) // 10
        copper = copper % 10
        
        result = []
        if platinum > 0:
            result.append(f"{platinum}p")
        if gold > 0:
            result.append(f"{gold}g")
        if silver > 0:
            result.append(f"{silver}s")
        if copper > 0 or not result:
            result.append(f"{copper}c")
        
        return " ".join(result)
    
    def confirm_delete(self):
        if not self.selected_items:
            return
        
        # Create confirmation message
        items_list = "\n".join(f"- {item}" for item in sorted(self.selected_items))
        msg = f"Are you sure you want to delete the following items?\n\n{items_list}"
        
        if messagebox.askyesno("Confirm Deletion", msg):
            # Remove items from the price list
            for item in self.selected_items:
                del self.item_prices[item]
            
            # Update the tree
            for item in self.tree.get_children():
                item_name = self.tree.item(item)['values'][1]
                if item_name in self.selected_items:
                    self.tree.delete(item)
            
            # Call the callback to save changes
            self.on_delete()
            
            # Show success message
            messagebox.showinfo("Success", "Selected items have been deleted.")
            
            # Reset selection
            self.selected_items.clear()
            self.delete_button['state'] = 'disabled'

class VendorCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("EverQuest Vendor Calculator")
        self.root.geometry("450x300")  # Reduced window size
        self.root.resizable(False, False)  # Prevent window resizing
        
        # Server name mappings for file names
        self.SERVER_NAME_MAPPINGS = {
            "Agnarr": "agnarr",
            "Antonius Bayle - Kane Bayle": "antonius",
            "Aradune": "aradune",
            "Bertoxxulous - Sarym": "bertox",
            "Bristlebane - The Tribunal": "bristle",
            "Cazic-Thule - Fennin Ro": "cazic",
            "Drinal - Maelin Starpyre": "drinal",
            "Erollisi Marr - The Nameless": "erollisi",
            "Firiona Vie": "firiona",
            "Luclin - Stromm": "luclin",
            "Mangler": "mangler",
            "Mischief": "mischief",
            "Oakwynd": "oakwynd",
            "Povar - Quellious": "povar",
            "Ragefire": "ragefire",
            "Rizlona": "rizlona",
            "Teek": "teek",
            "The Rathe - Prexus": "rathe",
            "Tormax": "tormax",
            "Tunare - The Seventh Hammer": "tunare",
            "Vaniki": "vaniki",
            "Vox": "vox",
            "Xegony - Druzzil Ro": "xegony",
            "Yelinak": "yelinak",
            "Zek": "zek"
        }
        
        # EverQuest servers list
        self.EQ_SERVERS = list(self.SERVER_NAME_MAPPINGS.keys())
        
        # Default item prices dictionary (all values converted to copper)
        self.DEFAULT_ITEM_PRICES = {
            "Chunk of Meat": 13,  # 1s 3c
            "Wolf Meat": 10,      # 1s
            "Pristine Pyre Beetle Carapace": 95,  # 9s 5c
            "Cracked Pyre Beetle Carapace": 24,   # 2s 4c
            "Fire Beetle Eye": 27,               # 2s 7c
            "Snake Scales": 10,                  # 1s
            "Garter Snake Tongue": 6,             # 6c
            "Ruined Wolf Pelt": 10,              # 1s
            "Rusty Scimitar": 181,              # 1g 8s 1c
            "Tiny Dagger": 10,                   # 1s
            "Spell: Pendril's Animation": 19     # 1s 9c
        }
        
        # Load or create config
        self.config_file = "eq_calculator_config.json"
        self.items_file = "eq_calculator_items.json"
        self.load_config()
        self.load_items()
        
        # If no EQ path is set, show setup first
        if not self.eq_path:
            self.show_setup()
        else:
            self.setup_ui()
    
    def format_currency(self, copper):
        """Convert copper to platinum/gold/silver/copper format"""
        platinum = copper // 1000
        gold = (copper % 1000) // 100
        silver = (copper % 100) // 10
        copper = copper % 10
        
        result = []
        if platinum > 0:
            result.append(f"{platinum}p")
        if gold > 0:
            result.append(f"{gold}g")
        if silver > 0:
            result.append(f"{silver}s")
        if copper > 0 or not result:  # Show copper if it's the only value
            result.append(f"{copper}c")
        
        return " ".join(result)
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.eq_path = config.get('eq_path', '')
            else:
                self.eq_path = ''
        except Exception:
            self.eq_path = ''
    
    def save_config(self):
        config = {'eq_path': self.eq_path}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
    
    def load_items(self):
        """Load items from JSON file"""
        try:
            if os.path.exists(self.items_file):
                with open(self.items_file, 'r') as f:
                    saved_items = json.load(f)
                    # If the file is empty or doesn't have default items, add them
                    if not saved_items:
                        saved_items = self.DEFAULT_ITEM_PRICES
                        with open(self.items_file, 'w') as f:
                            json.dump(saved_items, f, indent=4)
                    self.ITEM_PRICES = saved_items
            else:
                # If file doesn't exist, create it with default items
                self.ITEM_PRICES = self.DEFAULT_ITEM_PRICES.copy()
                with open(self.items_file, 'w') as f:
                    json.dump(self.ITEM_PRICES, f, indent=4)
        except Exception as e:
            print(f"Error loading items: {str(e)}")
            # If there's an error, use default items and try to save them
            self.ITEM_PRICES = self.DEFAULT_ITEM_PRICES.copy()
            try:
                with open(self.items_file, 'w') as f:
                    json.dump(self.ITEM_PRICES, f, indent=4)
            except Exception as e:
                print(f"Error saving default items: {str(e)}")
    
    def save_items(self):
        """Save items to JSON file"""
        try:
            with open(self.items_file, 'w') as f:
                json.dump(self.ITEM_PRICES, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save items: {str(e)}")
    
    def show_setup(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Setup frame
        setup_frame = ttk.Frame(self.root, padding="20")
        setup_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(setup_frame, text="First Time Setup", font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(setup_frame, text="Please select your EverQuest installation folder:").grid(row=1, column=0, columnspan=2, pady=5)
        
        self.eq_path_var = tk.StringVar()
        ttk.Entry(setup_frame, textvariable=self.eq_path_var, width=50).grid(row=2, column=0, padx=5)
        ttk.Button(setup_frame, text="Browse", command=self.browse_eq_folder).grid(row=2, column=1)
        
        ttk.Button(setup_frame, text="Save and Continue", command=self.save_setup).grid(row=3, column=0, columnspan=2, pady=20)
    
    def browse_eq_folder(self):
        folder = filedialog.askdirectory(title="Select EverQuest Installation Folder")
        if folder:
            # Verify EQGame.exe exists in the folder
            if os.path.exists(os.path.join(folder, "EQGame.exe")):
                self.eq_path_var.set(folder)
            else:
                messagebox.showerror("Error", "EQGame.exe not found in selected folder. Please select the correct EverQuest installation folder.")
    
    def save_setup(self):
        if not self.eq_path_var.get():
            messagebox.showerror("Error", "Please select your EverQuest installation folder.")
            return
        
        self.eq_path = self.eq_path_var.get()
        self.save_config()
        
        # Clear setup and show main UI
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()
    
    def add_new_item(self):
        AddItemDialog(self.root, self.ITEM_PRICES, self.refresh_items)
    
    def refresh_items(self):
        # Save items to file
        self.save_items()
        # Recalculate totals with updated price list
        if self.char_name.get() and self.server_var.get():
            self.calculate_total()
    
    def show_delete_items(self):
        DeleteItemsDialog(self.root, self.ITEM_PRICES, self.refresh_items)
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Reset EQ Path button - moved left
        reset_frame = ttk.Frame(main_frame)
        reset_frame.grid(row=0, column=1, sticky='ne', padx=2, pady=2)
        ttk.Button(reset_frame, text="Reset EQ Path", 
                  command=self.reset_eq_path).pack(side=tk.RIGHT)
        
        # Character name input
        ttk.Label(main_frame, text="Character Name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.char_name = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.char_name, width=15).grid(row=1, column=1, padx=2)
        
        # Server selection
        ttk.Label(main_frame, text="Server:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.server_var = tk.StringVar()
        server_combo = ttk.Combobox(main_frame, textvariable=self.server_var, values=self.EQ_SERVERS, width=15)
        server_combo.grid(row=2, column=1, padx=2)
        
        # Calculate button
        ttk.Button(main_frame, text="Calculate Total Value", command=self.calculate_total).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Results display
        self.result_var = tk.StringVar()
        ttk.Label(main_frame, text="Total Value:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Label(main_frame, textvariable=self.result_var, font=('Arial', 10, 'bold')).grid(row=4, column=1, sticky=tk.W)
        
        # Button frame for Add/Delete items - moved left
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=1, padx=2, sticky='e')
        
        ttk.Button(button_frame, text="Add Item", command=self.add_new_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete Items", command=self.show_delete_items).pack(side=tk.LEFT, padx=2)
        
        # Create Treeview for itemized breakdown
        columns = ('Item Name', 'Quantity', 'Price', 'Total')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=5)  # Reduced height
        
        # Define headings and bind click events
        self.sort_column = None
        self.sort_reverse = False
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            # Adjust column widths
            if col == 'Item Name':
                self.tree.column(col, width=200)
            else:
                self.tree.column(col, width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid the tree and scrollbar
        self.tree.grid(row=5, column=0, columnspan=2, pady=5, sticky='nsew')
        scrollbar.grid(row=5, column=2, sticky='ns')
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
    
    def sort_treeview(self, col):
        """Sort tree contents when a column header is clicked"""
        # Get all items from the tree
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Determine if we need to reverse the sort
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        
        # Sort the items
        items.sort(reverse=self.sort_reverse)
        
        # Rearrange items in sorted positions
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Update column header to show sort direction
        for column in self.tree['columns']:
            if column == col:
                direction = "↓" if self.sort_reverse else "↑"
                self.tree.heading(column, text=f"{column} {direction}")
            else:
                self.tree.heading(column, text=column)
    
    def calculate_total(self):
        if not self.char_name.get() or not self.server_var.get():
            messagebox.showerror("Error", "Please enter your character name and select a server!")
            return
        
        # Get the shortened server name from the mapping
        server_name = self.SERVER_NAME_MAPPINGS[self.server_var.get()]
        
        # Construct the inventory file path with correct format: CharacterName_Server-Inventory.txt
        inventory_file = os.path.join(self.eq_path, f"{self.char_name.get()}_{server_name}-Inventory.txt")
        
        if not os.path.exists(inventory_file):
            messagebox.showerror("Error", f"Inventory file not found: {inventory_file}")
            return
        
        try:
            total_copper = 0
            # Clear existing items in the tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            with open(inventory_file, 'r') as file:
                # Try to detect delimiter
                first_line = file.readline().strip()
                delimiter = ',' if ',' in first_line else '\t'
                file.seek(0)
                
                reader = csv.reader(file, delimiter=delimiter)
                for row in reader:
                    if len(row) >= 5 and row[0].startswith("General"):
                        item_name = row[1]
                        count = int(row[3])
                        
                        # Case-insensitive item lookup
                        item_found = False
                        for stored_item, price in self.ITEM_PRICES.items():
                            if item_name.lower() == stored_item.lower():
                                item_price = price
                                item_total = item_price * count
                                total_copper += item_total
                                
                                # Add item to tree
                                self.tree.insert('', 'end', values=(
                                    item_name,
                                    count,
                                    self.format_currency(item_price),
                                    self.format_currency(item_total)
                                ))
                                item_found = True
                                break
            
            # Update total value display
            result = self.format_currency(total_copper)
            self.result_var.set(result)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def reset_eq_path(self):
        """Reset the EQ installation path and show setup screen"""
        if messagebox.askyesno("Reset EQ Path", 
                             "Are you sure you want to reset the EverQuest installation path?\n"
                             "You will need to select it again."):
            self.eq_path = ''
            self.save_config()
            # Clear main UI and show setup
            for widget in self.root.winfo_children():
                widget.destroy()
            self.show_setup()

if __name__ == "__main__":
    root = tk.Tk()
    app = VendorCalculator(root)
    root.mainloop() 