import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import csv
import os
import datetime

user_data = {}

# File paths
buyers_file = 'buyers.csv'
company_file = 'company.csv'
items_file = 'items.csv'
orders_file = 'orders.csv'
order_history_file = 'order_history.csv'

def center_window():
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')


def apply_styles(root):
    style = ttk.Style()

    # Стиль заголовков
    style.configure("TLabel", font=("Helvetica", 9), foreground="black")
    
    # Стиль для полей ввода
    style.configure("TEntry", fieldbackground="white", font=("Helvetica", 9))
    
    # Стиль для кнопок
    style.configure("TButton", background="white", font=("Helvetica", 9), foreground="black")
    
    # Устанавливаем стиль для кнопок при наведении
    style.map("TButton",
              background=[('active', 'white')],
              foreground=[('active', 'black')])

def load_csv(file_path):
    if os.path.exists(file_path):
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    return []

def save_csv(file_path, data, fieldnames):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Load existing data
buyers = load_csv(buyers_file)
companies = load_csv(company_file)
items = load_csv(items_file)
orders = load_csv(orders_file)
order_history = load_csv(order_history_file)

def generate_id(data):
    if not data:
        return 1
    return max(int(item['ID']) for item in data) + 1

def show_frame(frame_name):
    frame = frames[frame_name]
    if frame_name == "profile":
        load_profile(
            frame.name_entry, frame.address_entry, frame.number_entry, frame.avatar_label
        )
    elif frame_name == "order_status":
        load_orders(frame.tree)
    elif frame_name == "buy_product":
        load_buy_product_frame()
    elif frame_name == "order_history":
        frame.load_order_history()
    frame.tkraise()
    center_window() 




def load_orders(tree):
    tree.delete(*tree.get_children())  # Clear existing data
    if 'name' in user_data:
        for order in orders:
            if order['Наименование покупателя'] == user_data['name']:
                tree.insert("", tk.END, values=(
                    order.get('ID', ''),
                    order.get('Название товара', ''),
                    order.get('Количество', ''),
                    order.get('Итоговая цена', ''),
                    order.get('Дата заказа', ''),
                    order.get('Статус', '')
                ))
    else:
        messagebox.showerror("Ошибка", "Не удалось загрузить заказы: имя пользователя отсутствует.")


def load_profile(name_entry, address_entry, number_entry, avatar_label):
    name_entry.delete(0, tk.END)
    name_entry.insert(0, user_data.get('name', ''))
    address_entry.delete(0, tk.END)
    address_entry.insert(0, user_data.get('address', ''))
    number_entry.delete(0, tk.END)
    number_entry.insert(0, user_data.get('number', ''))
    # Если есть сохраненный путь к изображению, отображаем его
    if 'avatar' in user_data and user_data['avatar']:
        try:
            image = Image.open(user_data['avatar'])
            image = image.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            avatar_label.config(image=photo)
            avatar_label.image = photo
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")


def upload_avatar(entry_widget, label_widget):
    filename = filedialog.askopenfilename(title="Select Avatar", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
    if filename:
        image = Image.open(filename)
        image = image.resize((100, 100), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        label_widget.config(image=photo)
        label_widget.image = photo  
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filename)  
  


def handle_registration(registration_type, name_entry, address_entry, number_entry, login_entry, password_entry, key_entry, avatar_path):
    global buyers, companies
    
    name = name_entry.get().strip()
    address = address_entry.get().strip()
    number = number_entry.get().strip()
    login = login_entry.get().strip()
    password = password_entry.get().strip()
    key = key_entry.get().strip()

    # Validate name (only letters)
    if not name.isalpha():
        messagebox.showerror("Ошибка", "Имя должно содержать только буквы.")
        return

    # Validate address (not empty)
    if not address:
        messagebox.showerror("Ошибка", "Адрес не может быть пустым.")
        return

    # Validate number (only digits)
    if not number.isdigit():
        messagebox.showerror("Ошибка", "Номер должен содержать только цифры.")
        return

    # Validate login (not empty)
    if not login:
        messagebox.showerror("Ошибка", "Логин не может быть пустым.")
        return

    # Validate password (not empty)
    if not password:
        messagebox.showerror("Ошибка", "Пароль не может быть пустым.")
        return

    # Check if login already exists
    if any(buyer['Логин'] == login for buyer in buyers) or any(company['Логин'] == login for company in companies):
        messagebox.showerror("Ошибка", "Логин уже существует.")
        return

    if registration_type == 'client':
        if key:
            messagebox.showerror("Ошибка", "Поле ключа должно быть пустым для клиентов.")
            return

        # Add buyer data to CSV
        new_id = generate_id(buyers)
        buyers.append({
            'ID': new_id,
            'Наименование': name,
            'Адрес': address,
            'Телефон': number,
            'Аватарка': avatar_path,  # Сохраняем путь к аватарке
            'Логин': login,
            'Пароль': password
        })
        save_csv(buyers_file, buyers, fieldnames=['ID', 'Наименование', 'Адрес', 'Телефон', 'Аватарка', 'Логин', 'Пароль'])
    else:
        if key != "123":
            messagebox.showerror("Ошибка", "Неверный ключ для регистрации компании.")
            return

        # Add company data to CSV
        new_id = generate_id(companies)
        companies.append({
            'ID': new_id,
            'Логин': login,
            'Пароль': password
        })
        save_csv(company_file, companies, fieldnames=['ID', 'Логин', 'Пароль'])

    show_frame("authorization")
    messagebox.showinfo("Регистрация", "Регистрация прошла успешно. Теперь войдите в систему.")



def handle_login(login_entry, password_entry):
    global buyers, companies

    login = login_entry.get()
    password = password_entry.get()
    apply_styles(root)
    
    # Check if the user is a client
    for buyer in buyers:
        if buyer['Логин'] == login and buyer['Пароль'] == password:
            user_data.update({
                'ID': buyer['ID'],
                'type': 'client',
                'name': buyer['Наименование'],
                'address': buyer['Адрес'],
                'number': buyer['Телефон'],
                'login': buyer['Логин'],
                'password': buyer['Пароль'],
                'avatar': buyer['Аватарка']  # Загружаем путь к аватарке
            })
            # Update the products view for the client
            update_products_view(frames['buy_product'].tree)
            show_frame("client_dashboard")
            return
    
    # Check if the user is a company
    for company in companies:
        if company['Логин'] == login and company['Пароль'] == password:
            user_data.update({
                'ID': company['ID'],
                'type': 'company',
                'login': company['Логин'],
                'password': company['Пароль'],
                'name': company['Логин']  # Add a default 'name' key for company users
            })
            # Bind the load_orders function after login
            show_frame("company_dashboard")
            return

    messagebox.showerror("Ошибка", "Неверный логин или пароль")



def create_registration_frame():
    frame = ttk.Frame(root)
    
    ttk.Label(frame, text="Регистрация").grid(row=0, column=1, pady=10)

    registration_type = tk.StringVar(value="client")

    ttk.Label(frame, text="Имя:").grid(row=2, column=0, pady=5)
    name_entry = ttk.Entry(frame)
    name_entry.grid(row=2, column=1, pady=5)
    
    ttk.Label(frame, text="Адрес:").grid(row=3, column=0, pady=5)
    address_entry = ttk.Entry(frame)
    address_entry.grid(row=3, column=1, pady=5)
    
    ttk.Label(frame, text="Номер:").grid(row=4, column=0, pady=5)
    number_entry = ttk.Entry(frame)
    number_entry.grid(row=4, column=1, pady=5)
    
    ttk.Label(frame, text="Аватарка:").grid(row=5, column=0, pady=5)
    avatar_label = tk.Label(frame)
    avatar_label.grid(row=5, column=3, pady=5)
    avatar_entry = tk.Entry(frame)
    avatar_entry.grid(row=5, column=1, pady=5)
    avatar_entry.config(state='disabled')
    ttk.Button(frame, text="Загрузить", command=lambda: upload_avatar(avatar_entry, avatar_label)).grid(row=5, column=2, pady=5)
    
    tk.Label(frame, text="Логин:").grid(row=6, column=0, pady=5)
    login_entry = ttk.Entry(frame)
    login_entry.grid(row=6, column=1, pady=5)
    
    tk.Label(frame, text="Пароль:").grid(row=7, column=0, pady=5)
    password_entry = ttk.Entry(frame, show="*")
    password_entry.grid(row=7, column=1, pady=5)
    
    lbl_key = tk.Label(frame, text="Ключ (для компании):")
    lbl_key.grid(row=8, column=0, pady=5)
    key_entry = ttk.Entry(frame)
    key_entry.grid(row=8, column=1, pady=5)
    
    def update_key_field():
        if registration_type.get() == "client":
            key_entry.config(state='disabled')
        else:
            key_entry.config(state='normal')
    
    ttk.Radiobutton(frame, text="Клиент", variable=registration_type, value="client", command=update_key_field).grid(row=1, column=0)
    ttk.Radiobutton(frame, text="Компания", variable=registration_type, value="company", command=update_key_field).grid(row=1, column=1)
    
    key_entry.config(state='disabled')  # Initially disable the key entry for clients
    
    ttk.Button(frame, text="Подтвердите", command=lambda: handle_registration(
        registration_type.get(), name_entry, address_entry, number_entry, login_entry, password_entry, key_entry, avatar_entry.get()
    )).grid(row=9, column=1, pady=10)
    ttk.Button(frame, text="Назад", command=lambda: show_frame("authorization")).grid(row=9, column=0, pady=10)
    
    return frame


def create_authorization_frame():
    frame = tk.Frame(root)

    ttk.Label(frame, text="Авторизация").grid(row=0, column=1, pady=10)
    
    ttk.Label(frame, text="Логин:").grid(row=1, column=0, pady=5)
    login_entry = ttk.Entry(frame)
    login_entry.grid(row=1, column=1, pady=5)
    
    ttk.Label(frame, text="Пароль:").grid(row=2, column=0, pady=5)
    password_entry = ttk.Entry(frame, show="*")
    password_entry.grid(row=2, column=1, pady=5)
    
    ttk.Button(frame, text="Войти", command=lambda: handle_login(login_entry, password_entry)).grid(row=3, column=1, pady=10)
    ttk.Button(frame, text="Регистрация", command=lambda: show_frame("registration")).grid(row=4, column=1, pady=10)
    
    return frame

def create_company_dashboard_frame():
    frame = ttk.Frame(root)

    ttk.Label(frame, text="Компания").grid(row=0, column=1, pady=10)
    
    ttk.Button(frame, text="Посмотреть заказы", command=lambda: show_frame("orders")).grid(row=1, column=1, pady=5)
    ttk.Button(frame, text="Добавить товар", command=lambda: show_frame("add_product")).grid(row=2, column=1, pady=5)
    ttk.Button(frame, text="Товары", command=lambda: show_frame("products")).grid(row=3, column=1, pady=5)
    ttk.Button(frame, text="Выйти", command=lambda: show_frame("authorization")).grid(row=4, column=1, pady=10)
    
    return frame

def create_client_dashboard_frame():
    frame = ttk.Frame(root)
    
    ttk.Label(frame, text="Клиент").grid(row=0, column=0, pady=10)

    ttk.Button(frame, text="Статус Заказа", command=lambda: show_frame("order_status")).grid(row=1, column=0, pady=5)
    ttk.Button(frame, text="История заказов", command=lambda: show_frame("order_history")).grid(row=2, column=0, pady=5)
    ttk.Button(frame, text="Купить товар", command=lambda: show_frame("buy_product")).grid(row=3, column=0, pady=5)
    ttk.Button(frame, text="Профиль", command=lambda: show_frame("profile")).grid(row=4, column=0, pady=5)
    ttk.Button(frame, text="Выйти", command=lambda: show_frame("authorization")).grid(row=5, column=0, pady=10)
    
    return frame

def handle_add_item(name_entry, price_entry, stock_entry, description_entry, delivery_var, image_label):
    global items
    
    name = name_entry.get().strip()
    price = price_entry.get().strip()
    stock = stock_entry.get().strip()
    description = description_entry.get().strip()
    delivery = delivery_var.get()
    image_path = image_label.image_path  # Сохраненный путь к изображению

    # Validate name (not empty)
    if not name:
        messagebox.showerror("Ошибка", "Название товара не может быть пустым.")
        return

    # Validate price (numeric)
    try:
        price = float(price)
    except ValueError:
        messagebox.showerror("Ошибка", "Цена должна быть числом.")
        return

    # Validate stock (integer)
    try:
        stock = int(stock)
    except ValueError:
        messagebox.showerror("Ошибка", "Количество на складе должно быть целым числом.")
        return
    
    new_id = generate_id(items)
    items.append({
        'ID': new_id,
        'Название': name,
        'Цена': price,
        'Наличие': stock,
        'Описание': description,
        'Доставка': 'Да' if delivery else 'Нет',
        'Компания ID': user_data['ID'],
        'Изображение': image_path  # Сохраняем путь к изображению
    })
    save_csv(items_file, items, fieldnames=['ID', 'Название', 'Цена', 'Наличие', 'Описание', 'Доставка', 'Компания ID', 'Изображение'])
    
    # Update the products view
    update_products_view(frames['products'].tree)
    
    show_frame("company_dashboard")
    messagebox.showinfo("Добавление товара", "Товар успешно добавлен.")


def upload_item_image(label_widget):
    filename = filedialog.askopenfilename(title="Select Item Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
    if filename:
        image = Image.open(filename)
        image = image.resize((100, 100), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        label_widget.config(image=photo)
        label_widget.image = photo
        label_widget.image_path = filename  



def handle_place_order(item_name, quantity, delivery, address):
    global orders, items

    item_name = item_name.strip()
    quantity = quantity.strip()

    # Validate item name (not empty)
    if not item_name:
        messagebox.showerror("Ошибка", "Название товара не может быть пустым.")
        return

    # Validate quantity (integer and greater than 0)
    try:
        quantity = int(quantity)
        if quantity <= 0:
            messagebox.showerror("Ошибка", "Количество должно быть больше нуля.")
            return
    except ValueError:
        messagebox.showerror("Ошибка", "Количество должно быть целым числом.")
        return

    # Validate delivery (not empty)
    if not delivery:
        messagebox.showerror("Ошибка", "Вариант доставки не может быть пустым.")
        return

    # Get the item details from the items list
    item = next((i for i in items if i['Название'] == item_name), None)
    if not item:
        messagebox.showerror("Ошибка", "Товар не найден.")
        return

    # Check if there is enough stock
    if int(item['Наличие']) < quantity:
        messagebox.showerror("Ошибка", "Недостаточное количество товара на складе.")
        return

    # Check if the delivery option is valid for the item
    if delivery == "Доставка" and item['Доставка'] == "Нет":
        messagebox.showerror("Ошибка", "У выбранного товара нет возможности доставки.")
        return

    # Calculate the total price
    total_price = int(quantity) * float(item['Цена'])
    if delivery == "Доставка":
        total_price += 200

    # Get the current date
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Create a new order
    new_id = generate_id(orders)
    new_order = {
        'ID': new_id,
        'Наименование покупателя': user_data['name'],
        'Адрес': address,
        'Статус': 'Размещен',
        'Название товара': item_name,
        'Количество': quantity,
        'Итоговая цена': f"{total_price:.2f} руб.",
        'Вариант доставки': delivery,
        'Дата заказа': current_date
    }
    orders.append(new_order)
    save_csv(orders_file, orders, fieldnames=['ID', 'Наименование покупателя', 'Адрес', 'Статус', 'Название товара', 'Количество', 'Итоговая цена', 'Вариант доставки', 'Дата заказа'])

    # Update the stock
    for i in items:
        if i['ID'] == item['ID']:
            i['Наличие'] = str(int(i['Наличие']) - quantity)
            break

    save_csv(items_file, items, fieldnames=['ID', 'Название', 'Цена', 'Наличие', 'Описание', 'Доставка', 'Компания ID', 'Изображение'])
    
    # Update the products view for the client
    update_products_view(frames['buy_product'].tree)

    messagebox.showinfo("Успех", "Заказ размещен успешно.")
    show_frame("client_dashboard")



def create_orders_frame():
    frame = ttk.Frame(root)
    
    columns = ("№", "Товар", "Количество", "Итоговая цена", "Дата заказа", "Статус", "Клиент")
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
    
    status_options = ["Размещен", "Заказ отправлен", "Заказ подтверждён", "Заказ доставлен"]

    def update_order_status(order_id, new_status):
        for order in orders:
            if order['ID'] == order_id:
                order['Статус'] = new_status
                save_csv(orders_file, orders, fieldnames=['ID', 'Наименование покупателя', 'Адрес', 'Статус', 'Название товара', 'Количество', 'Итоговая цена', 'Вариант доставки', 'Дата заказа'])
                load_company_orders(tree)
                break
    
    def on_tree_select(event):
        selected_items = tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            order_id = tree.item(selected_item, 'values')[0]
            selected_order = next(order for order in orders if order['ID'] == order_id)
            status_var.set(selected_order['Статус'])
    
    tree.bind('<<TreeviewSelect>>', on_tree_select)

    status_var = tk.StringVar()
    status_menu = ttk.Combobox(frame, textvariable=status_var, values=status_options)
    status_menu.grid(row=1, column=0, pady=10)
    ttk.Button(frame, text="Обновить статус", command=lambda: update_order_status(tree.item(tree.selection()[0], 'values')[0], status_var.get()) if tree.selection() else messagebox.showerror("Ошибка", "Выберите заказ для обновления статуса")).grid(row=1, column=1, pady=10)

    ttk.Button(frame, text="Назад", command=lambda: show_frame("company_dashboard")).grid(row=2, column=0, pady=10)
    ttk.Button(frame, text="Обновить", command=lambda: load_company_orders(tree)).grid(row=2, column=1, pady=10)
    
    # Store the tree reference in the frame
    frame.tree = tree
    frame.update_order_status = update_order_status
    
    return frame



def load_company_orders(tree):
    tree.delete(*tree.get_children())  # Clear existing data
    for order in orders:
        tree.insert("", tk.END, values=(
            order.get('ID', ''),
            order.get('Название товара', ''),
            order.get('Количество', ''),
            order.get('Итоговая цена', ''),
            order.get('Дата заказа', ''),
            order.get('Статус', ''),
            order.get('Наименование покупателя', '')
        ))

def delete_selected_item(tree):
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item, 'values')
        item_id = item[0]

        # Удаление товара из списка
        global items
        items = [i for i in items if i['ID'] != item_id]

        # Сохранение обновленного списка товаров в файл
        save_csv(items_file, items, fieldnames=['ID', 'Название', 'Цена', 'Наличие', 'Описание', 'Доставка', 'Компания ID', 'Изображение'])

        # Обновление таблицы
        update_products_view(tree)
        messagebox.showinfo("Успех", "Товар успешно удален.")
    else:
        messagebox.showerror("Ошибка", "Пожалуйста, выберите товар для удаления.")

def create_products_frame():
    frame = ttk.Frame(root)
    
    ttk.Label(frame, text="Товары").pack(pady=10)
    
    tree = ttk.Treeview(frame, columns=("ID", "Название", "Цена", "Наличие", "Доставка", "Описание", "Изображение"), show='headings')
    tree.heading("ID", text="ID")
    tree.heading("Название", text="Название")
    tree.heading("Цена", text="Цена")
    tree.heading("Наличие", text="Наличие")
    tree.heading("Доставка", text="Доставка")
    tree.heading("Описание", text="Описание")
    tree.heading("Изображение", text="Изображение")
    tree.pack(pady=10)
    
    for item in items:
        image_path = item.get('Изображение', '')
        tree.insert("", tk.END, values=(
            item.get('ID', ''),
            item.get('Название', ''),
            item.get('Цена', ''),
            item.get('Наличие', ''), 
            item.get('Доставка', ''),
            item.get('Описание', ''),
            image_path
        ))

    ttk.Button(frame, text="Назад", command=lambda: show_frame("company_dashboard")).pack(side=tk.LEFT, padx=5, pady=10)
    ttk.Button(frame, text="Удалить", command=lambda: delete_selected_item(tree)).pack(side=tk.RIGHT, padx=5, pady=10)  # Кнопка удаления товара

    frame.tree = tree
    
    return frame




def create_add_product_frame():
    frame = ttk.Frame(root)
    
    ttk.Label(frame, text="Добавить товар").grid(row=0, column=1, pady=10)
    
    ttk.Label(frame, text="Название:").grid(row=1, column=0, pady=5)
    name_entry = ttk.Entry(frame)
    name_entry.grid(row=1, column=1, pady=5)
    
    ttk.Label(frame, text="Цена:").grid(row=2, column=0, pady=5)
    price_entry = ttk.Entry(frame)
    price_entry.grid(row=2, column=1, pady=5)
    
    ttk.Label(frame, text="Наличие:").grid(row=3, column=0, pady=5)
    stock_entry = ttk.Entry(frame)
    stock_entry.grid(row=3, column=1, pady=5)
    
    ttk.Label(frame, text="Описание:").grid(row=4, column=0, pady=5)
    description_entry = ttk.Entry(frame)
    description_entry.grid(row=4, column=1, pady=5)
    
    delivery_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Доставка", variable=delivery_var).grid(row=5, column=1, pady=5)
    
    ttk.Label(frame, text="Изображение:").grid(row=6, column=0, pady=5)
    image_label = ttk.Label(frame)
    image_label.grid(row=6, column=1, pady=5)
    image_label.image_path = ""  # Инициализируем путь к изображению пустым значением

    ttk.Button(frame, text="Загрузить", command=lambda: upload_item_image(image_label)).grid(row=6, column=2, pady=5)
    
    ttk.Button(frame, text="Добавить", command=lambda: handle_add_item(
        name_entry, price_entry, stock_entry, description_entry, delivery_var, image_label
    )).grid(row=7, column=1, pady=10)
    ttk.Button(frame, text="Назад", command=lambda: show_frame("company_dashboard")).grid(row=7, column=0, pady=10)
    ttk.Button(frame, text="Импорт", command=lambda: import_items()).grid(row=7, column=2, pady=10)
    
    return frame

def import_items():
    filename = filedialog.askopenfilename(title="Select File", filetypes=[("CSV Files", "*.csv")])
    if filename:
        try:
            with open(filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                required_fields = {'Название', 'Цена', 'Наличие', 'Доставка', 'Описание', 'Изображение'}
                if not required_fields.issubset(reader.fieldnames):
                    missing_fields = required_fields - set(reader.fieldnames)
                    messagebox.showerror("Ошибка", f"Отсутствуют необходимые столбцы: {', '.join(missing_fields)}")
                    return

                for row in reader:
                    item = {
                        'ID': generate_id(items),  # Генерация уникального ID
                        'Название': row['Название'],
                        'Цена': row['Цена'],
                        'Наличие': row['Наличие'],
                        'Доставка': row['Доставка'],
                        'Описание': row['Описание'],
                        'Изображение': ''
                    }

                    image_path = row.get('Изображение', '')
                    if image_path and os.path.exists(image_path):
                        try:
                            image = Image.open(image_path)
                            image = image.resize((100, 100), Image.Resampling.LANCZOS)
                            saved_image_path = os.path.join('images', os.path.basename(image_path))
                            image.save(saved_image_path)
                            item['Изображение'] = saved_image_path
                        except Exception as e:
                            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")

                    items.append(item)

                save_csv(items_file, items, fieldnames=['ID', 'Название', 'Цена', 'Наличие', 'Описание', 'Доставка', 'Компания ID', 'Изображение'])
                update_products_view(frames['products'].tree)

            messagebox.showinfo("Информация", "Товары успешно импортированы.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось импортировать товары: {e}")




def update_products_view(tree):
    # Clear the existing items in the tree view
    tree.delete(*tree.get_children())
    
    # Re-populate the tree view with the updated items
    for item in items:
        image_path = item.get('Изображение', '')
        tree.insert("", tk.END, values=(
            item.get('ID', ''),
            item.get('Название', ''),
            item.get('Цена', ''),
            item.get('Наличие', ''),
            item.get('Доставка', ''),
            item.get('Описание', ''),
            image_path
        ))


def create_buy_product_frame():
    frame = ttk.Frame(root)
    
    ttk.Label(frame, text="Купить товар").grid(row=0, column=1, pady=10)
    
    columns = ("ID", "Название", "Цена", "Наличие", "Доставка", "Описание", "Изображение")
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    
    for item in items:
        image_path = item.get('Изображение', '')
        tree.insert("", tk.END, values=(
            item.get('ID', ''),
            item.get('Название', ''),
            item.get('Цена', ''),
            item.get('Наличие', ''),
            item.get('Доставка', ''),
            item.get('Описание', ''),
            image_path
        ))

    def on_item_select(event):
        selected_item = tree.selection()
        if selected_item:
            item = tree.item(selected_item, 'values')
            item_name_entry.delete(0, tk.END)
            item_name_entry.insert(0, item[1])
            update_total_price()
            display_image(item[6])  # Отображаем изображение
            update_delivery_options(item[4])  # Обновляем опции доставки
    
    tree.bind('<<TreeviewSelect>>', on_item_select)
    
    def display_image(image_path):
        if image_path:
            try:
                image = Image.open(image_path)
                image = image.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                image_label.config(image=photo)
                image_label.image = photo
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")
        else:
            image_label.config(image='')
            image_label.image = None

    def update_total_price(*args):
        try:
            quantity = int(quantity_entry.get())
            if quantity <= 0:
                total_price_var.set("Недопустимое количество")
                return
            selected_item = tree.selection()
            if selected_item:
                item = tree.item(selected_item, 'values')
                price = float(item[2])
                total_price_var.set(f"{quantity * price:.2f} руб.")
            else:
                total_price_var.set("Выберите товар")
        except ValueError:
            total_price_var.set("Недопустимое количество")

    def update_delivery_options(delivery_option):
        if delivery_option == "Нет":
            delivery_entry.set("Самовывоз")
            delivery_entry['state'] = 'disabled'
        else:
            delivery_entry['state'] = 'normal'

    ttk.Label(frame, text="Название товара:").grid(row=2, column=0, pady=5)
    item_name_entry = ttk.Entry(frame)
    item_name_entry.grid(row=2, column=1, pady=5)

    ttk.Label(frame, text="Количество:").grid(row=3, column=0, pady=5)
    quantity_entry = ttk.Entry(frame)
    quantity_entry.grid(row=3, column=1, pady=5)
    quantity_entry.bind("<KeyRelease>", update_total_price)
    
    ttk.Label(frame, text="Выберите доставку:").grid(row=4, column=0, pady=5)
    delivery_entry = ttk.Combobox(frame, values=["Доставка", "Самовывоз"])
    delivery_entry.grid(row=4, column=1, pady=5)
    
    ttk.Label(frame, text="Итоговая цена:").grid(row=5, column=0, pady=5)
    total_price_var = tk.StringVar()
    total_price_label = ttk.Label(frame, textvariable=total_price_var)
    total_price_label.grid(row=5, column=1, pady=5)

    ttk.Label(frame, text="Адрес:").grid(row=6, column=0, pady=5)
    address_entry = ttk.Entry(frame)
    address_entry.grid(row=6, column=1, pady=5)
    address_entry.insert(0, user_data.get('address', ''))

    ttk.Label(frame, text="Изображение товара:").grid(row=7, column=0, pady=5)
    image_label = ttk.Label(frame)
    image_label.grid(row=7, column=1, pady=5)

    ttk.Button(frame, text="Подтвердить", command=lambda: handle_place_order(
        item_name_entry.get(), quantity_entry.get(), delivery_entry.get(), address_entry.get()
    )).grid(row=8, column=1, pady=10)
    ttk.Button(frame, text="Назад", command=lambda: show_frame("client_dashboard")).grid(row=8, column=0, pady=10)
    
    frame.tree = tree
    frame.address_entry = address_entry
    
    return frame



def load_buy_product_frame():
    frames['buy_product'].address_entry.delete(0, tk.END)
    frames['buy_product'].address_entry.insert(0, user_data.get('address', ''))


def create_profile_frame():
    frame = ttk.Frame(root)
    
    ttk.Label(frame, text="Профиль").grid(row=0, column=1, pady=10)
    
    ttk.Label(frame, text="Имя:").grid(row=1, column=0, pady=5)
    name_entry = ttk.Entry(frame)
    name_entry.grid(row=1, column=1, pady=5)
    
    ttk.Label(frame, text="Адрес:").grid(row=2, column=0, pady=5)
    address_entry = ttk.Entry(frame)
    address_entry.grid(row=2, column=1, pady=5)
    
    ttk.Label(frame, text="Номер:").grid(row=3, column=0, pady=5)
    number_entry = ttk.Entry(frame)
    number_entry.grid(row=3, column=1, pady=5)
    
    ttk.Label(frame, text="Аватарка:").grid(row=4, column=0, pady=5)
    avatar_label = ttk.Label(frame)
    avatar_label.grid(row=4, column=1, pady=5)

    frame.name_entry = name_entry
    frame.address_entry = address_entry
    frame.number_entry = number_entry
    frame.avatar_label = avatar_label
    
    ttk.Button(frame, text="Назад", command=lambda: show_frame("client_dashboard")).grid(row=5, column=0, pady=10)
    
    return frame
    
def load_profile(name_entry, address_entry, number_entry, avatar_label):
    name_entry.delete(0, tk.END)
    name_entry.insert(0, user_data.get('name', ''))
    address_entry.delete(0, tk.END)
    address_entry.insert(0, user_data.get('address', ''))
    number_entry.delete(0, tk.END)
    number_entry.insert(0, user_data.get('number', ''))
    if 'avatar' in user_data and user_data['avatar']:
        try:
            image = Image.open(user_data['avatar'])
            image = image.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            avatar_label.config(image=photo)
            avatar_label.image = photo
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")



def create_order_status_frame():
    frame = ttk.Frame(root)
    
    columns = ("№", "Товар", "Количество", "Итоговая цена", "Дата заказа", "Статус")
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
    
    # Store the tree reference in the frame
    frame.tree = tree

    def collect_order():
        selected_items = frames['order_status'].tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            order_id = frames['order_status'].tree.item(selected_item, 'values')[0]
            order = next(order for order in orders if order['ID'] == order_id)
            if order['Статус'] == 'Заказ доставлен':
            # Remove order from orders list
                orders.remove(order)
            # Add order to history
                order['Дата доставки'] = datetime.datetime.now().strftime("%Y-%m-%d")
                order_history.append(order)
                save_csv(orders_file, orders, fieldnames=['ID', 'Наименование покупателя', 'Адрес', 'Статус', 'Название товара', 'Количество', 'Итоговая цена', 'Вариант доставки', 'Дата заказа'])
                save_csv(order_history_file, order_history, fieldnames=['ID', 'Наименование покупателя', 'Адрес', 'Статус', 'Название товара', 'Количество', 'Итоговая цена', 'Вариант доставки', 'Дата заказа', 'Дата доставки'])
                load_orders(frames['order_status'].tree)
                messagebox.showinfo("Успех", "Заказ успешно забран и перемещен в историю заказов.")
            else:
                messagebox.showerror("Ошибка", "Заказ ещё не доставлен.")

    
    ttk.Button(frame, text="Назад", command=lambda: show_frame("client_dashboard")).grid(row=1, column=0, pady=10)
    ttk.Button(frame, text="Забрать", command=collect_order).grid(row=1, column=1, pady=10)

    return frame


def create_order_history_frame():
    frame = ttk.Frame(root)
    
    columns = ("№", "Товар", "Количество", "Итоговая цена", "Дата заказа", "Дата доставки")
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=0, column=0, padx=10, pady=10)
    
    def load_order_history():
        tree.delete(*tree.get_children())  # Clear existing data
        if 'name' in user_data:
            for order in order_history:
                if order['Наименование покупателя'] == user_data['name']:
                    tree.insert("", tk.END, values=(
                        order.get('ID', ''),
                        order.get('Название товара', ''),
                        order.get('Количество', ''),
                        order.get('Итоговая цена', ''),
                        order.get('Дата заказа', ''),
                        order.get('Дата доставки', '')
                    ))
        else:
            messagebox.showerror("Ошибка", "Не удалось загрузить историю заказов: имя пользователя отсутствует.")
    
    ttk.Button(frame, text="Назад", command=lambda: show_frame("client_dashboard")).grid(row=1, column=0, pady=10)
    
    frame.tree = tree
    frame.load_order_history = load_order_history
    
    return frame



root = tk.Tk()
root.title("Магазин")
root.geometry("1430x600")

frames = {
    "registration": create_registration_frame(),
    "authorization": create_authorization_frame(),
    "company_dashboard": create_company_dashboard_frame(),
    "client_dashboard": create_client_dashboard_frame(),
    "orders": create_orders_frame(),
    "products": create_products_frame(),
    "add_product": create_add_product_frame(),
    "buy_product": create_buy_product_frame(),
    "profile": create_profile_frame(),
    "order_status": create_order_status_frame(),
    "order_history": create_order_history_frame(),
}

for frame in frames.values():
    frame.grid(row=0, column=0, sticky='nsew')

show_frame("authorization")
center_window() 

root.mainloop()