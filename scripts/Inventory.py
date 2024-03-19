import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
import base64
import sqlite3
import datetime
import io


def connect_db():
    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS items (name TEXT, image BLOB, price REAL, selling_price REAL, quantity INTEGER, location TEXT, stock_date TEXT, notes TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS presets (preset_name TEXT, item_name TEXT, price REAL, selling_price REAL, location TEXT)''')
    conn.commit()



def save_item(name, image_base64, price, selling_price, quantity, location, stock_date, notes):
    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()
    cur.execute("SELECT price FROM items WHERE name = ? ORDER BY price DESC LIMIT 1", (name,))
    result = cur.fetchone()

    if result is not None:
        old_price = result[0]
    
        if old_price != price:
            price_change = "up" if price > old_price else "down"
            messagebox.showinfo("Price Change Alert", f"The price of {name} has gone {price_change} from {old_price} to {price}.")

            user_input = messagebox.askyesno("Change Selling Price", "Do you want to change the selling price?")
            if user_input:
                new_selling_price = simpledialog.askfloat("Input", "Enter the new selling price:")
                if new_selling_price is None:
                    messagebox.showinfo("Insert Cancelled", "The item insert has been cancelled.")

                    return False
                
                else:
                    cur.execute("INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, image_base64, price, new_selling_price, quantity, location, stock_date, notes))
                    conn.commit()
                    messagebox.showinfo("Update Successful", f"The selling price has been updated to {new_selling_price}.")

                    return True
            else:
                user_input = messagebox.askyesno("Confirmation", "Is this item okay to insert without changing the price?")
                if user_input:
                    cur.execute("INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, image_base64, price, selling_price, quantity, location, stock_date, notes))
                    conn.commit()
                    messagebox.showinfo("Insert Successful", "The item has been inserted.")

                    return True
                else:
                    messagebox.showinfo("Insert Cancelled", "The item was not inserted.")

                    return False
    else:
        cur.execute("INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, image_base64, price, selling_price, quantity, location, stock_date, notes))
        conn.commit()
        messagebox.showinfo("Insert Successful", "Item has been inserted")
        return True




def add_preset(preset_name, item_name, price, selling_price, location):
    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO presets VALUES (?, ?, ?, ?, ?)', (preset_name, item_name, price, selling_price, location))
    conn.commit()

    
    
def remove_pre(preset_name):
    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()
    cur.execute('DELETE FROM presets WHERE preset_name = ?', (preset_name,))
    conn.commit()





class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management")
        self.root.configure(bg='white')
        self.root.geometry("400x340") 

        self.entry_name = tk.Entry(root, highlightthickness=1, highlightbackground='#2B2748')
        self.entry_name.grid(row=1, column=1)
        tk.Label(root, text="Name", bg='white').grid(row=1, column=0)

        self.entry_quantity = tk.Entry(root, highlightthickness=1, highlightbackground='#2B2748')
        self.entry_quantity.grid(row=1, column=3)
        tk.Label(root, text="Quantity", bg='white').grid(row=1, column=2)

        self.entry_price = tk.Entry(root, highlightthickness=1, highlightbackground='#2B2748')
        self.entry_price.grid(row=2, column=1)
        self.entry_price.bind("<KeyRelease>", self.calculate_margin)
        tk.Label(root, text="Price $", bg='white').grid(row=2, column=0)

        self.sell_input_price = tk.Entry(root, highlightthickness=1, highlightbackground='#2B2748')
        self.sell_input_price.grid(row=2, column=3)
        self.sell_input_price.bind("<KeyRelease>", self.calculate_margin)
        tk.Label(root, text="Sell Price $", bg='white').grid(row=2, column=2)

        tk.Label(root, text="Location", bg='white').grid(row=3, column=0, pady=(15, 5))  

        self.loc_input = tk.Entry(root, width=53, highlightthickness=1, highlightbackground='#2B2748')
        self.loc_input.grid(row=3, column=1, columnspan=3, pady=(15, 5))  

        self.text_notes = tk.Text(root, height=5, width=40, highlightthickness=1, highlightbackground='#2B2748')
        self.text_notes.grid(row=4, column=1, columnspan=3, pady=(0, 15))
        tk.Label(root, text="Notes:", bg='white').grid(row=4, column=0)

        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TButton', background='#2B2748', foreground='white', borderwidth=0)

        self.image_label = tk.Label(root)
        self.image_label.grid(row=0, column=1, columnspan=3)
        self.image_label.configure(bg='white')

        button_frame = tk.Frame(root, width=460)
        button_frame.place(relx=0.5, rely=0.9, anchor='center')
        button_frame.configure(bg='white')
        
        btn_upload_img = ttk.Button(button_frame, text="Upload Image", style='TButton', command=self.upload_image)
        btn_upload_img.grid(row=0, column=0, padx=10)

        btn_add_itm = ttk.Button(button_frame, text="Add Item", style='TButton', command=self.add_item)
        btn_add_itm.grid(row=0, column=1, padx=10)

        btn_show = ttk.Button(button_frame, text="Show Items", style='TButton', command=self.show_item_list)
        btn_show.grid(row=0, column=2, padx=10)

        btn_manage_presets = ttk.Button(button_frame, text="Manage Presets", style='TButton', command=self.preset_window)
        btn_manage_presets.grid(row=0, column=3, padx=10)










    def preset_window(self):
        self.preset_window = Toplevel(self.root)
        self.preset_window.title("Preset Management")
        self.preset_window.configure(bg='white')
        self.setup_preset(self.preset_window)

    def setup_preset(self, window):
        tk.Label(window, text="Preset List", bg='white').grid(row=0, column=0)
    
        self.preset_list = tk.Listbox(window)
        self.preset_list.grid(row=1, column=0)
        self.preset_list.bind('<<ListboxSelect>>', self.display_pre)

        info_frame = tk.Frame(window)
        info_frame.grid(row=1, column=1, rowspan=4)
        info_frame.configure(bg='white')

        self.itm_label = tk.Label(info_frame)
        self.itm_label.grid(row=0, column=0, sticky='w')
        self.itm_label.configure(bg='white')

        self.price_label = tk.Label(info_frame)
        self.price_label.grid(row=1, column=0, sticky='w')
        self.price_label.configure(bg='white')

        self.sell_price_label = tk.Label(info_frame)
        self.sell_price_label.grid(row=2, column=0, sticky='w')
        self.sell_price_label.configure(bg='white')

        self.loc_label = tk.Label(info_frame)
        self.loc_label.grid(row=3, column=0, sticky='w')
        self.loc_label.configure(bg='white')

        self.load_presets()

        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TButton', background='#2B2748', foreground='white', borderwidth=0)

        btn_add_preset = ttk.Button(window, text="+", style='TButton', command=self.add_preset_window)
        btn_add_preset.grid(row=2, column=0)

        insert_preset = ttk.Button(window, text="Insert Preset", style='TButton', command=self.transfer_data)
        insert_preset.grid(row=2, column=1, padx=10)

        remove_pre = ttk.Button(window, text="Remove Preset", style='TButton', command=self.remove_pre)
        remove_pre.grid(row=2, column=2)

    def transfer_data(self):
        selected_preset = self.preset_list.get(self.preset_list.curselection())

        conn = sqlite3.connect('stock.db')
        cur = conn.cursor()
        cur.execute("SELECT item_name, price, selling_price, location FROM presets WHERE preset_name = ?", (selected_preset,))
        preset_info = cur.fetchone()

        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, preset_info[0])

        self.entry_price.delete(0, tk.END)
        self.entry_price.insert(0, preset_info[1])

        self.sell_input_price.delete(0, tk.END)
        self.sell_input_price.insert(0, preset_info[2])

        self.loc_input.delete(0, tk.END)
        self.loc_input.insert(0, preset_info[3])



    def display_pre(self, event):
        selected_preset = self.preset_list.get(self.preset_list.curselection())

        conn = sqlite3.connect('stock.db')
        cur = conn.cursor()
        cur.execute("SELECT item_name, price, selling_price, location FROM presets WHERE preset_name = ?", (selected_preset,))
        preset_info = cur.fetchone()

        self.itm_label.config(text=f"Item Name: {preset_info[0]}")
        self.price_label.config(text=f"Price: {preset_info[1]}")
        self.sell_price_label.config(text=f"Selling Price: {preset_info[2]}")
        self.loc_label.config(text=f"Location: {preset_info[3]}")
        
    def remove_pre(self):
        selected_preset = self.preset_list.get(self.preset_list.curselection())

        conn = sqlite3.connect('stock.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM presets WHERE preset_name = ?", (selected_preset,))
        conn.commit()
        conn.close()

        self.load_presets()

    def reset_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_quantity.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.sell_input_price.delete(0, tk.END)
        self.loc_input.delete(0, tk.END)
        self.text_notes.delete("1.0", tk.END)

        global uploaded_image
        uploaded_image = None
        self.image_label.config(image='', text='No Image Uploaded')

    def add_item(self):
        global image_path

        name = self.entry_name.get()
        price = float(self.entry_price.get())
        selling_price = float(self.sell_input_price.get())
        quantity = int(self.entry_quantity.get())
        location = self.loc_input.get()
        stock_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notes = self.text_notes.get("1.0", tk.END)
        
        if not self.image_path:
            messagebox.showerror("Error", "Image is required")
            return

        if hasattr(self, 'image_path'):
            image_base64 = self.convert_image_to_base64(self.image_path)
        
        check = save_item(name, image_base64, price, selling_price, quantity, location, stock_date, notes)
        if check:
            messagebox.showinfo("Success", "Item added successfully")
            self.reset_form()

    def calculate_margin(self, event=None):
        try:
            price = float(self.entry_price.get())
            selling_price = float(self.sell_input_price.get())

            if price > 0:
                margin = ((selling_price - price) / price) * 100
                self.text_notes.delete("1.0", tk.END)
                self.text_notes.insert("1.0", f"Margin: {margin:.2f}%")
            else:
                self.text_notes.delete("1.0", tk.END)
                self.text_notes.insert("1.0", "Invalid price input.")

        except ValueError:
            self.text_notes.delete("1.0", tk.END)

    def show_item_list(self):
        global root, item_frame, header_frame, item_canvas, v_scroll, h_scroll
        root = Toplevel(self.root)
        root.title("Item List")
        root.geometry("1000x600")  

        header_frame = tk.Frame(root)
        headers = ["Stock Date", "Title", "Image", "Price", "Selling Price", "Quantity", "Location"]
        header_widths = [12, 5, 35, 0, 12, 0, 15] 

        for i, (header, width) in enumerate(zip(headers, header_widths)):
            label = tk.Label(header_frame, text=header, font=('bold', 12), width=width)
            label.grid(row=0, column=i, sticky='w')

        header_frame.pack(side="top", fill="x")

        item_canvas = tk.Canvas(root)
        v_scroll = tk.Scrollbar(root, orient="vertical", command=item_canvas.yview)
        h_scroll = tk.Scrollbar(root, orient="horizontal", command=item_canvas.xview)
        item_canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        item_canvas.pack(side="left", fill="both", expand=True)

        item_frame = tk.Frame(item_canvas)
        item_canvas.create_window((0, 0), window=item_frame, anchor="nw")

        item_frame.bind("<Configure>", lambda e: item_canvas.configure(scrollregion=item_canvas.bbox("all")))
        item_frame.images = [] 

        self.refresh_item_list()

    def refresh_item_list(self):
        for widget in item_frame.winfo_children():
            widget.destroy()

        conn = sqlite3.connect('stock.db')
        cur = conn.cursor()
        cur.execute("SELECT name, image, price, selling_price, quantity, location, stock_date, notes FROM items")
        rows = cur.fetchall()

        for index, row in enumerate(rows):
            tk.Label(item_frame, text=f"{row[6]}").grid(row=index, column=0, sticky="w")

            tk.Label(item_frame, text=row[0]).grid(row=index, column=1, sticky="w")  # Name

            image_data = base64.b64decode(row[1])
            image = Image.open(io.BytesIO(image_data))
            
            resized_image = image.resize((300, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)
            item_frame.images.append(photo)

            tk.Label(item_frame, image=photo).grid(row=index, column=2)  # Image
            tk.Label(item_frame, text=f"Price: ${row[2]}").grid(row=index, column=3, sticky="w")
            tk.Label(item_frame, text=f"Selling Price: ${row[3]}").grid(row=index, column=4, sticky="w")
            tk.Label(item_frame, text=f"Quantity: {row[4]}").grid(row=index, column=5, sticky="w")
            tk.Label(item_frame, text=f"Location: {row[5]}").grid(row=index, column=6, sticky="w")

    def add_preset_window(self):
        preset_window = tk.Toplevel()
        preset_window.title("Add Preset")

        tk.Label(preset_window, text="Preset Name").grid(row=0, column=0)
        self.preset_name_entry = tk.Entry(preset_window)
        self.preset_name_entry.grid(row=0, column=1)

        tk.Label(preset_window, text="Item Name").grid(row=1, column=0)
        self.name_input = tk.Entry(preset_window)
        self.name_input.grid(row=1, column=1)

        tk.Label(preset_window, text="Price").grid(row=2, column=0)
        self.price_entry = tk.Entry(preset_window)
        self.price_entry.grid(row=2, column=1)

        tk.Label(preset_window, text="Selling Price").grid(row=3, column=0)
        self.selling_price_entry = tk.Entry(preset_window)
        self.selling_price_entry.grid(row=3, column=1)

        tk.Label(preset_window, text="Location").grid(row=4, column=0)
        self.location_entry = tk.Entry(preset_window)
        self.location_entry.grid(row=4, column=1)

        submit_button = tk.Button(preset_window, text="Submit", command=self.remove_pre)
        submit_button.grid(row=5, column=0, columnspan=2)

    def remove_pre(self):
        preset_name = self.preset_name_entry.get()
        item_name = self.name_input.get()
        price = self.price_entry.get()
        selling_price = self.selling_price_entry.get()
        location = self.location_entry.get()

        self.add_preset_to_db(preset_name, item_name, price, selling_price, location)

    def add_preset_to_db(self, preset_name, item_name, price, selling_price, location):
        conn = sqlite3.connect('stock.db')
        cur = conn.cursor()
        cur.execute('''INSERT INTO presets (preset_name, item_name, price, selling_price, location) VALUES (?, ?, ?, ?, ?)''', (preset_name, item_name, price, selling_price, location))
        conn.commit()

        self.load_presets()

    def load_presets(self):
        conn = sqlite3.connect('stock.db')
        cur = conn.cursor()
        cur.execute("SELECT preset_name FROM presets")
        presets = cur.fetchall()

        self.preset_list.delete(0, tk.END)

        for preset in presets:
            self.preset_list.insert(tk.END, preset[0])

    def convert_image_to_base64(self, image_path, event=None):
        with Image.open(image_path) as img:
            img = img.resize((128, 128), Image.LANCZOS)
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue())
            return img_str
        
        
    def upload_image(self, event=None):
        global image_path, uploaded_image
        self.image_path = filedialog.askopenfilename()
        if self.image_path:
            image = Image.open(self.image_path)
            image = image.resize((100, 100), Image.Resampling.LANCZOS)
            uploaded_image = ImageTk.PhotoImage(image)
            self.image_label.config(image=uploaded_image)
pass
















def main():
    root = tk.Tk()
    app = InventoryApp(root)
    connect_db()
    root.mainloop()

if __name__ == "__main__":
    main()