import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import json
import os

class FinanceCalculator:
    def __init__(self, root):
        self.root = root
        self.translations = {
            'en': {
                'title': "Finance Calculator",
                'amount': "Amount:",
                'type': "Type:",
                'category': "Category:",
                'add': "Add",
                'edit': "Edit",
                'delete': "Delete",
                'save': "Save",
                'cancel': "Cancel",
                'edit_transaction': "Edit Transaction",
                'income': "Income",
                'expense': "Expense",
                'date': "Date",
                'add_transaction': "Add Transaction",
                'statistics': "Statistics",
                'show_expenses': "Show Expenses by Category",
                'show_balance': "Show Balance Trend",
                'error': "Error",
                'fill_fields': "Please fill all fields",
                'invalid_amount': "Please enter a valid amount",
                'no_expenses': "No expense data available",
                'expenses_by_category': "Expenses by Category",
                'balance_dynamics': "Balance Dynamics",
                'currency': "Currency:"
            }
        }
        
        self.currencies = [
            "USD - $", "EUR - €", "GBP - £", "JPY - ¥", "CNY - ¥", "RUB - ₽",
            "AUD - $", "CAD - $", "CHF - Fr", "HKD - $", "SGD - $", "SEK - kr",
            "KRW - ₩", "TRY - ₺", "INR - ₹", "BRL - R$", "ZAR - R", "AED - د.إ",
            "THB - ฿", "MXN - $"
        ]
        
        self.current_lang = 'en'
        self.current_currency = self.currencies[0]
        
        self.setup_settings_panel()
        
        self.root.title(self.get_text('title'))
        self.root.geometry("800x600")
        
        self.data_file = "finance_data.json"
        self.transactions = self.load_data()
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        self.add_transaction_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.add_transaction_frame, text=self.get_text('add_transaction'))
        self.setup_transaction_tab()
        
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text=self.get_text('statistics'))
        self.setup_stats_tab()

    def setup_settings_panel(self):
        settings_frame = ttk.Frame(self.root)
        settings_frame.pack(fill='x', padx=10, pady=5)
        
        currency_frame = ttk.Frame(settings_frame)
        currency_frame.pack(side='left')
        
        ttk.Label(currency_frame, text=self.get_text('currency')).pack(side='left', padx=5)
        self.currency_var = tk.StringVar(value=self.current_currency)
        currency_combo = ttk.Combobox(currency_frame,
                                    textvariable=self.currency_var,
                                    values=self.currencies,
                                    state='readonly',
                                    width=15)
        currency_combo.pack(side='left')
        
        def on_currency_change(event):
            self.current_currency = self.currency_var.get()
            self.update_transaction_list()
            
        currency_combo.bind('<<ComboboxSelected>>', on_currency_change)

    def get_text(self, key):
        return self.translations[self.current_lang].get(key, key)

    def get_currency_symbol(self):
        return self.current_currency.split(' - ')[1]

    def setup_transaction_tab(self):
        form_frame = ttk.Frame(self.add_transaction_frame)
        form_frame.pack(fill='x', padx=5, pady=5)
        
        amount_frame = ttk.Frame(form_frame)
        amount_frame.pack(fill='x', pady=2)
        ttk.Label(amount_frame, text=self.get_text('amount')).pack(side='left', padx=(0, 5))
        self.amount_entry = ttk.Entry(amount_frame)
        self.amount_entry.pack(side='left', expand=True, fill='x')
        
        type_frame = ttk.Frame(form_frame)
        type_frame.pack(fill='x', pady=2)
        ttk.Label(type_frame, text=self.get_text('type')).pack(side='left', padx=(0, 5))
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(type_frame,
                                      textvariable=self.type_var,
                                      values=[self.get_text('income'), self.get_text('expense')],
                                      state='readonly')
        self.type_combo.pack(side='left', expand=True, fill='x')
        
        category_frame = ttk.Frame(form_frame)
        category_frame.pack(fill='x', pady=2)
        ttk.Label(category_frame, text=self.get_text('category')).pack(side='left', padx=(0, 5))
        self.category_entry = ttk.Entry(category_frame)
        self.category_entry.pack(side='left', expand=True, fill='x')
        
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill='x', pady=10)
        ttk.Button(button_frame,
                  text=self.get_text('add'),
                  command=self.add_transaction).pack(expand=True)
        
        table_frame = ttk.Frame(self.add_transaction_frame)
        table_frame.pack(expand=True, fill='both', pady=5)
        
        self.tree = ttk.Treeview(table_frame,
                                columns=('date', 'type', 'category', 'amount'),
                                show='headings')
        
        self.tree.heading('date', text=self.get_text('date'))
        self.tree.heading('type', text=self.get_text('type'))
        self.tree.heading('category', text=self.get_text('category'))
        self.tree.heading('amount', text=self.get_text('amount'))
        
        self.tree.column('date', width=150)
        self.tree.column('type', width=100)
        self.tree.column('category', width=150)
        self.tree.column('amount', width=100)
        
        scrollbar = ttk.Scrollbar(table_frame,
                                orient='vertical',
                                command=self.tree.yview)
        
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')
        
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label=self.get_text('edit'), command=self.edit_selected_transaction)
        self.context_menu.add_command(label=self.get_text('delete'), command=self.delete_selected_transaction)
        
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        self.update_transaction_list()

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def delete_selected_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        item_values = self.tree.item(selected_item)['values']
        date_str = item_values[0]
        
        for i, transaction in enumerate(self.transactions):
            if transaction['date'] == date_str:
                self.transactions.pop(i)
                break
        
        self.save_data()
        self.update_transaction_list()

    def edit_selected_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        item_values = self.tree.item(selected_item)['values']
        date_str = item_values[0]
        
        transaction = None
        for t in self.transactions:
            if t['date'] == date_str:
                transaction = t
                break
        
        if transaction:
            edit_window = tk.Toplevel(self.root)
            edit_window.title(self.get_text('edit_transaction'))
            edit_window.geometry('300x250')
            
            main_frame = ttk.Frame(edit_window, padding="10")
            main_frame.pack(fill='both', expand=True)
            
            ttk.Label(main_frame, text=self.get_text('amount')).pack(fill='x', pady=(0, 5))
            amount_var = tk.StringVar(value=str(abs(transaction['amount'])))
            amount_entry = ttk.Entry(main_frame, textvariable=amount_var)
            amount_entry.pack(fill='x', pady=(0, 10))
            
            ttk.Label(main_frame, text=self.get_text('type')).pack(fill='x', pady=(0, 5))
            type_var = tk.StringVar(value=transaction['type'])
            type_combo = ttk.Combobox(main_frame,
                                    textvariable=type_var,
                                    values=[self.get_text('income'), self.get_text('expense')],
                                    state='readonly')
            type_combo.pack(fill='x', pady=(0, 10))
            
            ttk.Label(main_frame, text=self.get_text('category')).pack(fill='x', pady=(0, 5))
            category_var = tk.StringVar(value=transaction['category'])
            category_entry = ttk.Entry(main_frame, textvariable=category_var)
            category_entry.pack(fill='x', pady=(0, 10))
            
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill='x', pady=(10, 0))
            
            def save_changes():
                try:
                    if not all([amount_var.get(), type_var.get(), category_var.get()]):
                        messagebox.showerror(self.get_text('error'),
                                           self.get_text('fill_fields'))
                        return
                    
                    amount = float(amount_var.get())
                    if type_var.get() == self.get_text('expense'):
                        amount = -amount
                    
                    transaction['amount'] = amount
                    transaction['type'] = type_var.get()
                    transaction['category'] = category_var.get()
                    
                    self.save_data()
                    self.update_transaction_list()
                    
                    edit_window.destroy()
                    
                except ValueError:
                    messagebox.showerror(self.get_text('error'),
                                       self.get_text('invalid_amount'))
            
            ttk.Button(button_frame,
                      text=self.get_text('cancel'),
                      command=edit_window.destroy).pack(side='left', padx=(0, 5))
            
            ttk.Button(button_frame,
                      text=self.get_text('save'),
                      command=save_changes).pack(side='left')
            
            edit_window.transient(self.root)
            edit_window.grab_set()
            edit_window.focus_set()

    def setup_stats_tab(self):
        content_frame = ttk.Frame(self.stats_frame)
        content_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(button_frame,
                  text=self.get_text('show_expenses'),
                  command=self.show_expense_pie_chart).pack(side='left', padx=5)
        
        ttk.Button(button_frame,
                  text=self.get_text('show_balance'),
                  command=self.show_balance_trend).pack(side='left', padx=5)
        
        self.plot_frame = ttk.Frame(content_frame)
        self.plot_frame.pack(fill='both', expand=True)

    def add_transaction(self):
        try:
            amount = float(self.amount_entry.get())
            transaction_type = self.type_var.get()
            category = self.category_entry.get()
            
            if not all([amount, transaction_type, category]):
                messagebox.showerror(self.get_text('error'), self.get_text('fill_fields'))
                return
            
            if transaction_type == self.get_text('expense'):
                amount = -amount
            
            transaction = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": transaction_type,
                "category": category,
                "amount": amount,
                "currency": self.current_currency
            }
            
            self.transactions.append(transaction)
            self.save_data()
            self.update_transaction_list()
            
            self.amount_entry.delete(0, tk.END)
            self.type_combo.set('')
            self.category_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror(self.get_text('error'), self.get_text('invalid_amount'))

    def update_transaction_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for transaction in self.transactions:
            currency = transaction.get('currency', self.currencies[0])
            currency_symbol = currency.split(' - ')[1]
            
            self.tree.insert('', 'end', values=(
                transaction['date'],
                transaction['type'],
                transaction['category'],
                f"{abs(transaction['amount']):.2f} {currency_symbol}"
            ))

    def show_expense_pie_chart(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        df = pd.DataFrame(self.transactions)
        
        expenses = df[df['amount'] < 0].groupby('category')['amount'].sum().abs()
        
        if expenses.empty:
            messagebox.showinfo(self.get_text('error'), self.get_text('no_expenses'))
            return

        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(8, 6))
        
        wedges, texts, autotexts = ax.pie(expenses, 
                                         labels=expenses.index,
                                         autopct='%1.1f%%',
                                         textprops={'fontsize': 9},
                                         pctdistance=0.85,
                                         labeldistance=1.1)
        
        ax.set_title(self.get_text('expenses_by_category'))
        
        ax.legend(wedges, expenses.index,
                 title="Categories",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.axis('equal')
        
        plt.subplots_adjust(right=0.85)
        
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def show_balance_trend(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        df = pd.DataFrame(self.transactions)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        df['balance'] = df['amount'].cumsum()
        
        fig, ax = plt.subplots(figsize=(6, 4))
        df.plot(x='date', y='balance', ax=ax)
        ax.set_title(self.get_text('balance_dynamics'))
        ax.set_xlabel(self.get_text('date'))
        ax.set_ylabel(f"{self.get_text('balance')} ({self.get_currency_symbol()})")
        
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.transactions, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceCalculator(root)
    root.mainloop()
