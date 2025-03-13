import sys
import json
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, 
                           QTableWidgetItem, QTabWidget, QMessageBox, QDialog, QFormLayout,
                           QHeaderView, QFrame, QSplitter, QMenu, QSizePolicy, QToolButton,
                           QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QAction, QColor, QPalette, QFont, QIcon, QPixmap

class FinanceCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Dictionary with translations
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
                'currency': "Currency:",
                'balance': "Balance"
            }
        }
        
        # List of currencies
        self.currencies = [
            "USD - $", "EUR - €", "GBP - £", "JPY - ¥", "CNY - ¥", "RUB - ₽",
            "AUD - $", "CAD - $", "CHF - Fr", "HKD - $", "SGD - $", "SEK - kr",
            "KRW - ₩", "TRY - ₺", "INR - ₹", "BRL - R$", "ZAR - R", "AED - د.إ",
            "THB - ฿", "MXN - $"
        ]
        
        self.current_lang = 'en'
        self.current_currency = self.currencies[0]  # Default to USD
        
        self.data_file = "finance_data.json"
        self.transactions = self.load_data()
        
        self.init_ui()
        
    def init_ui(self):
        # Main window setup
        self.setWindowTitle(self.get_text('title'))
        self.setMinimumSize(900, 700)
        
        # Set application icon
        self.setWindowIcon(QIcon("icons/app_icon.svg"))
        
        # Dark theme with improved styling
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #1a1a1a;
                color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #252525;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 10px 20px;
                margin-right: 2px;
                color: #b0b0b0;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #353535;
                border-bottom: 2px solid #4a86e8;
                color: #4a86e8;
            }
            QTabBar::tab:hover:!selected {
                background-color: #333333;
                color: #d0d0d0;
            }
            QTableWidget {
                gridline-color: #3a3a3a;
                background-color: #252525;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                color: #f0f0f0;
                selection-background-color: #4a86e8;
                selection-color: #ffffff;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2a2a2a;
            }
            QTableWidget::item:selected {
                background-color: #4a86e8;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #3a3a3a;
                color: #b0b0b0;
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 10px;
                background-color: #2d2d2d;
                color: #f0f0f0;
                selection-background-color: #4a86e8;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #4a86e8;
                background-color: #333333;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #3a3a3a;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            QComboBox::down-arrow {
                image: url(icons/expense_icon.svg);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                selection-background-color: #4a86e8;
                color: #f0f0f0;
                outline: none;
                border-radius: 6px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QLabel {
                color: #f0f0f0;
                font-weight: 500;
            }
            QFrame {
                background-color: #252525;
                border-radius: 8px;
                border: 1px solid #3a3a3a;
            }
            QSplitter::handle {
                background-color: #3a3a3a;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #3a3a3a;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Settings panel
        self.setup_settings_panel(main_layout)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        main_layout.addWidget(self.tab_widget)
        
        # Transactions tab
        self.transaction_tab = QWidget()
        self.tab_widget.addTab(self.transaction_tab, QIcon("icons/income_icon.svg"), self.get_text('add_transaction'))
        self.setup_transaction_tab()
        
        # Statistics tab
        self.stats_tab = QWidget()
        self.tab_widget.addTab(self.stats_tab, QIcon("icons/stats_icon.svg"), self.get_text('statistics'))
        self.setup_stats_tab()
        
    def setup_settings_panel(self, main_layout):
        settings_frame = QFrame()
        settings_frame.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Добавляем эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        settings_frame.setGraphicsEffect(shadow)
        
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(15, 10, 15, 10)
        
        # Логотип приложения
        logo_label = QLabel()
        logo_pixmap = QPixmap("icons/app_icon.svg")
        logo_label.setPixmap(logo_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        settings_layout.addWidget(logo_label)
        
        # Название приложения
        title_label = QLabel(self.get_text('title'))
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4a86e8;")
        settings_layout.addWidget(title_label)
        settings_layout.addStretch()
        
        # Currency
        currency_label = QLabel(self.get_text('currency'))
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(self.currencies)
        self.currency_combo.setCurrentText(self.current_currency)
        self.currency_combo.currentTextChanged.connect(self.on_currency_change)
        self.currency_combo.setFixedWidth(150)
        
        settings_layout.addWidget(currency_label)
        settings_layout.addWidget(self.currency_combo)
        
        main_layout.addWidget(settings_frame)
        
    def on_currency_change(self, currency):
        self.current_currency = currency
        self.update_transaction_list()
        
    def get_text(self, key):
        return self.translations[self.current_lang].get(key, key)
        
    def get_currency_symbol(self):
        return self.current_currency.split(' - ')[1]
        
    def setup_transaction_tab(self):
        layout = QVBoxLayout(self.transaction_tab)
        layout.setContentsMargins(0, 15, 0, 0)
        layout.setSpacing(20)
        
        # Form for adding transactions
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Добавляем эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        form_frame.setGraphicsEffect(shadow)
        
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Заголовок формы
        header_label = QLabel(self.get_text('add_transaction'))
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4a86e8;")
        form_layout.addRow("", header_label)
        
        # Amount field
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("0.00")
        form_layout.addRow(QLabel(self.get_text('amount')), self.amount_edit)
        
        # Type field
        self.type_combo = QComboBox()
        self.type_combo.addItems([self.get_text('income'), self.get_text('expense')])
        
        # Добавляем иконки к типам транзакций
        self.type_combo.setItemIcon(0, QIcon("icons/income_icon.svg"))
        self.type_combo.setItemIcon(1, QIcon("icons/expense_icon.svg"))
        
        form_layout.addRow(QLabel(self.get_text('type')), self.type_combo)
        
        # Category field
        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("Groceries, Transport, Salary...")
        form_layout.addRow(QLabel(self.get_text('category')), self.category_edit)
        
        # Add button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.add_button = QPushButton(self.get_text('add'))
        self.add_button.setIcon(QIcon("icons/income_icon.svg"))
        self.add_button.setIconSize(QSize(16, 16))
        self.add_button.clicked.connect(self.add_transaction)
        button_layout.addWidget(self.add_button)
        
        form_layout.addRow("", button_layout)
        
        layout.addWidget(form_frame)
        
        # Transactions table
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Добавляем эффект тени
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(15)
        shadow2.setColor(QColor(0, 0, 0, 80))
        shadow2.setOffset(0, 2)
        table_frame.setGraphicsEffect(shadow2)
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(15, 15, 15, 15)
        
        # Заголовок таблицы
        table_header = QLabel("Transactions")
        table_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4a86e8;")
        table_layout.addWidget(table_header)
        
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(4)
        self.transaction_table.setHorizontalHeaderLabels([
            self.get_text('date'),
            self.get_text('type'),
            self.get_text('category'),
            self.get_text('amount')
        ])
        
        # Table setup
        self.transaction_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.transaction_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.transaction_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.transaction_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.transaction_table.setAlternatingRowColors(True)
        self.transaction_table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #2a2a2a;
            }
        """)
        
        # Context menu for table
        self.transaction_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.transaction_table.customContextMenuRequested.connect(self.show_context_menu)
        
        table_layout.addWidget(self.transaction_table)
        layout.addWidget(table_frame)
        
        # Fill table with data
        self.update_transaction_list()
        
    def show_context_menu(self, position):
        menu = QMenu()
        
        edit_action = QAction(self.get_text('edit'), self)
        edit_action.triggered.connect(self.edit_selected_transaction)
        menu.addAction(edit_action)
        
        delete_action = QAction(self.get_text('delete'), self)
        delete_action.triggered.connect(self.delete_selected_transaction)
        menu.addAction(delete_action)
        
        menu.exec(self.transaction_table.mapToGlobal(position))
        
    def delete_selected_transaction(self):
        selected_rows = self.transaction_table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        date_str = self.transaction_table.item(row, 0).text()
        
        for i, transaction in enumerate(self.transactions):
            if transaction['date'] == date_str:
                self.transactions.pop(i)
                break
                
        self.save_data()
        self.update_transaction_list()
        
    def edit_selected_transaction(self):
        selected_rows = self.transaction_table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        date_str = self.transaction_table.item(row, 0).text()
        
        transaction = None
        for t in self.transactions:
            if t['date'] == date_str:
                transaction = t
                break
                
        if transaction:
            dialog = QDialog(self)
            dialog.setWindowTitle(self.get_text('edit_transaction'))
            dialog.setMinimumWidth(350)
            
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            form_layout = QFormLayout()
            form_layout.setSpacing(10)
            
            # Amount field
            amount_edit = QLineEdit(str(abs(transaction['amount'])))
            form_layout.addRow(QLabel(self.get_text('amount')), amount_edit)
            
            # Type field
            type_combo = QComboBox()
            type_combo.addItems([self.get_text('income'), self.get_text('expense')])
            type_combo.setCurrentText(transaction['type'])
            form_layout.addRow(QLabel(self.get_text('type')), type_combo)
            
            # Category field
            category_edit = QLineEdit(transaction['category'])
            form_layout.addRow(QLabel(self.get_text('category')), category_edit)
            
            layout.addLayout(form_layout)
            
            # Buttons
            button_layout = QHBoxLayout()
            cancel_button = QPushButton(self.get_text('cancel'))
            cancel_button.clicked.connect(dialog.reject)
            cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #505050;
                    color: #e0e0e0;
                }
                QPushButton:hover {
                    background-color: #606060;
                }
            """)
            
            save_button = QPushButton(self.get_text('save'))
            save_button.clicked.connect(dialog.accept)
            
            button_layout.addWidget(cancel_button)
            button_layout.addWidget(save_button)
            
            layout.addLayout(button_layout)
            
            if dialog.exec():
                try:
                    if not all([amount_edit.text(), type_combo.currentText(), category_edit.text()]):
                        QMessageBox.critical(self, self.get_text('error'), self.get_text('fill_fields'))
                        return
                        
                    amount = float(amount_edit.text())
                    if type_combo.currentText() == self.get_text('expense'):
                        amount = -amount
                        
                    transaction['amount'] = amount
                    transaction['type'] = type_combo.currentText()
                    transaction['category'] = category_edit.text()
                    
                    self.save_data()
                    self.update_transaction_list()
                    
                except ValueError:
                    QMessageBox.critical(self, self.get_text('error'), self.get_text('invalid_amount'))
        
    def setup_stats_tab(self):
        layout = QVBoxLayout(self.stats_tab)
        layout.setContentsMargins(0, 15, 0, 0)
        layout.setSpacing(20)
        
        # Buttons for selecting statistics type
        button_frame = QFrame()
        button_frame.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Добавляем эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        button_frame.setGraphicsEffect(shadow)
        
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(25, 20, 25, 20)
        
        # Заголовок
        stats_header = QLabel(self.get_text('statistics'))
        stats_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4a86e8;")
        button_layout.addWidget(stats_header)
        button_layout.addStretch()
        
        expenses_button = QPushButton(self.get_text('show_expenses'))
        expenses_button.setIcon(QIcon("icons/expense_icon.svg"))
        expenses_button.setIconSize(QSize(16, 16))
        expenses_button.clicked.connect(self.show_expense_pie_chart)
        
        balance_button = QPushButton(self.get_text('show_balance'))
        balance_button.setIcon(QIcon("icons/stats_icon.svg"))
        balance_button.setIconSize(QSize(16, 16))
        balance_button.clicked.connect(self.show_balance_trend)
        
        button_layout.addWidget(expenses_button)
        button_layout.addWidget(balance_button)
        
        layout.addWidget(button_frame)
        
        # Frame for charts
        self.plot_frame = QFrame()
        self.plot_frame.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Добавляем эффект тени
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(15)
        shadow2.setColor(QColor(0, 0, 0, 80))
        shadow2.setOffset(0, 2)
        self.plot_frame.setGraphicsEffect(shadow2)
        
        self.plot_layout = QVBoxLayout(self.plot_frame)
        self.plot_layout.setContentsMargins(25, 25, 25, 25)
        
        layout.addWidget(self.plot_frame)
        
    def add_transaction(self):
        try:
            amount_text = self.amount_edit.text()
            transaction_type = self.type_combo.currentText()
            category = self.category_edit.text()
            
            if not all([amount_text, transaction_type, category]):
                QMessageBox.critical(self, self.get_text('error'), self.get_text('fill_fields'))
                return
                
            amount = float(amount_text)
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
            
            # Clear input fields
            self.amount_edit.clear()
            self.type_combo.setCurrentIndex(0)
            self.category_edit.clear()
            
        except ValueError:
            QMessageBox.critical(self, self.get_text('error'), self.get_text('invalid_amount'))
            
    def update_transaction_list(self):
        self.transaction_table.setRowCount(0)
        
        for transaction in self.transactions:
            currency = transaction.get('currency', self.currencies[0])
            currency_symbol = currency.split(' - ')[1]
            
            row = self.transaction_table.rowCount()
            self.transaction_table.insertRow(row)
            
            # Date
            date_item = QTableWidgetItem(transaction['date'])
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.transaction_table.setItem(row, 0, date_item)
            
            # Type
            type_item = QTableWidgetItem(transaction['type'])
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Добавляем иконку к типу транзакции
            if transaction['type'] == self.get_text('income'):
                type_item.setIcon(QIcon("icons/income_icon.svg"))
            else:
                type_item.setIcon(QIcon("icons/expense_icon.svg"))
                
            self.transaction_table.setItem(row, 1, type_item)
            
            # Category
            category_item = QTableWidgetItem(transaction['category'])
            category_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.transaction_table.setItem(row, 2, category_item)
            
            # Amount
            amount_str = f"{abs(transaction['amount']):.2f} {currency_symbol}"
            amount_item = QTableWidgetItem(amount_str)
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            # Set color for amount depending on transaction type
            if transaction['amount'] < 0:
                amount_item.setForeground(QColor("#ff5252"))  # Red for expenses
            else:
                amount_item.setForeground(QColor("#66bb6a"))  # Green for income
                
            self.transaction_table.setItem(row, 3, amount_item)
            
    def show_expense_pie_chart(self):
        # Clear previous chart
        for i in reversed(range(self.plot_layout.count())):
            self.plot_layout.itemAt(i).widget().setParent(None)
            
        # Create DataFrame from transactions
        df = pd.DataFrame(self.transactions)
        
        # Filter only expenses and group by category
        if not df.empty:
            expenses = df[df['amount'] < 0].groupby('category')['amount'].sum().abs()
            
            if expenses.empty:
                QMessageBox.information(self, self.get_text('error'), self.get_text('no_expenses'))
                return
                
            # Create chart
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(8, 6), dpi=100, facecolor='#252525')
            
            # Color scheme - улучшенная цветовая схема
            colors = ['#4a86e8', '#ff9900', '#9c27b0', '#e53935', '#43a047', 
                     '#795548', '#607d8b', '#f44336', '#3f51b5', '#009688',
                     '#ff5722', '#8bc34a', '#ffc107', '#03a9f4', '#673ab7']
            
            wedges, texts, autotexts = ax.pie(
                expenses, 
                labels=expenses.index,
                autopct='%1.1f%%',
                textprops={'fontsize': 10, 'color': '#f0f0f0', 'fontweight': 'bold'},
                pctdistance=0.85,
                labeldistance=1.1,
                colors=colors,
                wedgeprops={'edgecolor': '#252525', 'linewidth': 2, 'antialiased': True},
                shadow=True
            )
            
            # Configure appearance
            ax.set_title(self.get_text('expenses_by_category'), fontsize=16, pad=20, color='#f0f0f0', fontweight='bold')
            
            # Add legend with improved styling
            ax.legend(
                wedges, 
                expenses.index,
                title="Categories",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=10,
                frameon=False,
                title_fontsize=12
            )
            
            plt.axis('equal')
            plt.tight_layout()
            
            # Add chart to form
            canvas = FigureCanvas(fig)
            self.plot_layout.addWidget(canvas)
        else:
            QMessageBox.information(self, self.get_text('error'), self.get_text('no_expenses'))
            
    def show_balance_trend(self):
        # Clear previous chart
        for i in reversed(range(self.plot_layout.count())):
            self.plot_layout.itemAt(i).widget().setParent(None)
            
        # Create DataFrame from transactions
        df = pd.DataFrame(self.transactions)
        
        if not df.empty:
            # Convert dates and sort
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate cumulative sum for balance
            df['balance'] = df['amount'].cumsum()
            
            # Create chart
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(8, 5), dpi=100, facecolor='#252525')
            
            # Configure balance line with improved styling
            ax.plot(
                df['date'], 
                df['balance'], 
                marker='o', 
                linestyle='-', 
                linewidth=3, 
                color='#4a86e8',
                markersize=8,
                markerfacecolor='#252525',
                markeredgewidth=2,
                markeredgecolor='#4a86e8'
            )
            
            # Add fill under line with gradient
            ax.fill_between(
                df['date'], 
                df['balance'], 
                alpha=0.3, 
                color='#4a86e8'
            )
            
            # Configure appearance with improved styling
            ax.set_title(self.get_text('balance_dynamics'), fontsize=16, pad=20, color='#f0f0f0', fontweight='bold')
            ax.set_xlabel(self.get_text('date'), fontsize=12, color='#e0e0e0', fontweight='bold')
            ax.set_ylabel(f"{self.get_text('balance')} ({self.get_currency_symbol()})", fontsize=12, color='#e0e0e0', fontweight='bold')
            
            # Grid setup with improved styling
            ax.grid(True, linestyle='--', alpha=0.3, color='#505050', linewidth=0.8)
            
            # Axis formatting with improved styling
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#505050')
            ax.spines['bottom'].set_color('#505050')
            
            # Улучшенное форматирование меток осей
            ax.tick_params(axis='both', colors='#e0e0e0', labelsize=10)
            
            plt.tight_layout()
            
            # Add chart to form
            canvas = FigureCanvas(fig)
            self.plot_layout.addWidget(canvas)
        else:
            QMessageBox.information(self, self.get_text('error'), self.get_text('no_expenses'))
            
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
        
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.transactions, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set global styles for application
    app.setStyle("Fusion")
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = FinanceCalculator()
    window.show()
    
    sys.exit(app.exec())
