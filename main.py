import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QComboBox, 
                             QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QStatusBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database import Database
from decision_tree import CarDecisionTree

# Логика подбора строится на дереве решений (decision_tree.py): БД → все авто → дерево фильтров → результаты

class CarSelectionApp(QMainWindow):
    """Подбор автомобиля по дереву решений (PyQt6). Логика от decision_tree.py."""
    
    def __init__(self):
        super().__init__()
        self.db = None
        self.decision_tree = None
        self.brands = []
        self.body_types = []
        self.current_results = []
        
        self.init_ui()
        self.init_database()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Экспертная система по выбору легкового автомобиля")
        self.setGeometry(100, 100, 1000, 750)
        self.setMinimumSize(900, 700)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title_label = QLabel("🚗 Подбор автомобиля")
        title_font = QFont("Arial", 20, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Критерии — только выпадающие списки (порядок: тип кузова → цена → марка → мощность)
        filters_group = QGroupBox("Критерии")
        filters_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        filters_layout = QVBoxLayout()
        filters_layout.setSpacing(12)
        
        # Создаем фильтры
        self.create_filters(filters_layout)
        filters_group.setLayout(filters_layout)
        main_layout.addWidget(filters_group)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.search_button = QPushButton("🔍 Найти автомобили")
        self.search_button.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self.search_button.setMinimumHeight(50)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.search_button.clicked.connect(self.get_recommendations)
        buttons_layout.addWidget(self.search_button)
        
        self.clear_button = QPushButton("🗑️ Очистить фильтры")
        self.clear_button.setFont(QFont("Arial", 11))
        self.clear_button.setMinimumHeight(50)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
        """)
        self.clear_button.clicked.connect(self.clear_filters)
        buttons_layout.addWidget(self.clear_button)
        
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        # Таблица результатов (после прохода по дереву решений)
        results_label = QLabel("📊 Результаты:")
        results_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        results_label.setStyleSheet("color: #2c3e50; margin-top: 10px;")
        main_layout.addWidget(results_label)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "№", "Марка", "Модель", "Тип кузова", "Цена (руб.)", "Мощность (л.с.)"
        ])
        
        # Настройка таблицы
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # №
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Марка
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Модель
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Тип кузова
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Цена
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Мощность
        
        self.results_table.setAlternatingRowColors(False)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setFont(QFont("Arial", 14))
        self.results_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                color: black;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: black;
            }
            QTableWidget::item:hover {
                background-color: #e8f4f8;
            }
        """)
        
        main_layout.addWidget(self.results_table)
        
        # Статусная строка
        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("Arial", 12))
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 5px;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
        
        # Применяем стиль к главному окну
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                color: #2c3e50;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
        
    # Диапазоны для выпадающих списков (отображаемое название, min, max)
    PRICE_OPTIONS = [
        ("Любая", None, None),
        ("до 1 млн", None, 1_000_000),
        ("1 – 2 млн", 1_000_000, 2_000_000),
        ("2 – 3 млн", 2_000_000, 3_000_000),
        ("3 – 5 млн", 3_000_000, 5_000_000),
        ("5 – 10 млн", 5_000_000, 10_000_000),
        ("10+ млн", 10_000_000, None),
    ]
    POWER_OPTIONS = [
        ("Любая", None, None),
        ("до 100 л.с.", None, 100),
        ("100 – 150 л.с.", 100, 150),
        ("150 – 200 л.с.", 150, 200),
        ("200 – 300 л.с.", 200, 300),
        ("300+ л.с.", 300, None),
    ]

    def create_filters(self, layout):
        """Четыре выпадающих списка по критериям (порядок дерева: тип кузова → цена → марка → мощность)."""
        def add_row(label_text, combo):
            row = QHBoxLayout()
            lbl = QLabel(label_text + ":")
            lbl.setMinimumWidth(120)
            lbl.setFont(QFont("Arial", 11))
            combo.setFont(QFont("Arial", 11))
            row.addWidget(lbl)
            row.addWidget(combo, 1)
            layout.addLayout(row)

        self.body_type_combo = QComboBox()
        add_row("Тип кузова", self.body_type_combo)

        self.price_combo = QComboBox()
        for name, min_p, max_p in self.PRICE_OPTIONS:
            self.price_combo.addItem(name, (min_p, max_p))
        add_row("Цена", self.price_combo)

        self.brand_combo = QComboBox()
        add_row("Марка", self.brand_combo)

        self.power_combo = QComboBox()
        for name, min_p, max_p in self.POWER_OPTIONS:
            self.power_combo.addItem(name, (min_p, max_p))
        add_row("Мощность", self.power_combo)

    def clear_filters(self):
        """Сброс выбора во всех выпадающих списках."""
        self.body_type_combo.setCurrentIndex(0)
        self.price_combo.setCurrentIndex(0)
        self.brand_combo.setCurrentIndex(0)
        self.power_combo.setCurrentIndex(0)
        self.results_table.setRowCount(0)
        self.status_bar.showMessage("Критерии сброшены")
        
    def init_database(self):
        """Инициализация БД и дерева решений."""
        try:
            self.db = Database()
            self.decision_tree = CarDecisionTree()
            self.brands = self.db.get_unique_brands()
            self.body_types = self.db.get_unique_body_types()
            self.body_type_combo.addItem("Любой")
            self.body_type_combo.addItems(self.body_types)
            self.brand_combo.addItem("Любая")
            self.brand_combo.addItems(self.brands)
            
            from sqlalchemy import func
            from database import Car
            try:
                count = self.db.session.query(func.count(Car.id)).scalar()
            except Exception:
                count = len(self.db.get_all_cars())
            self.status_bar.showMessage(
                f"БД подключена. Автомобилей: {count}. Подбор по критериям."
            )
            
        except Exception as e:
            error_msg = str(e)
            detailed_msg = (f"Ошибка подключения к базе данных:\n{error_msg}\n\n"
                          f"Убедитесь, что:\n"
                          f"1. Файл cars.db существует или может быть создан\n"
                          f"2. У приложения есть права на чтение/запись в директорию")
            
            QMessageBox.critical(self, "Ошибка подключения", detailed_msg)
            self.status_bar.showMessage("Ошибка подключения к базе данных")
            
    def get_recommendations(self):
        """Подбор по выбранным критериям из выпадающих списков (дерево решений)."""
        if not self.db or not self.decision_tree:
            QMessageBox.critical(self, "Ошибка", "БД или дерево решений не инициализированы.")
            return
        try:
            criteria = {}
            body_type = self.body_type_combo.currentText()
            if body_type and body_type != "Любой":
                criteria["body_type"] = body_type
            price_data = self.price_combo.currentData()
            if price_data and (price_data[0] is not None or price_data[1] is not None):
                if price_data[0] is not None:
                    criteria["min_price"] = price_data[0]
                if price_data[1] is not None:
                    criteria["max_price"] = price_data[1]
            brand = self.brand_combo.currentText()
            if brand and brand != "Любая":
                criteria["brand"] = brand
            power_data = self.power_combo.currentData()
            if power_data and (power_data[0] is not None or power_data[1] is not None):
                if power_data[0] is not None:
                    criteria["min_power"] = power_data[0]
                if power_data[1] is not None:
                    criteria["max_power"] = power_data[1]
            
            # Логика от decision_tree: все авто → дерево решений → отфильтрованный список
            all_cars = self.db.get_all_cars()
            filtered = self.decision_tree.evaluate(all_cars, criteria)
            results = sorted(filtered, key=lambda x: x["price"])
            results = [
                {
                    "brand": c["brand"],
                    "model": c["model"],
                    "body_type": c["body_type"],
                    "price": c["price"],
                    "power": c["power"],
                    "description": c.get("description", ""),
                }
                for c in results
            ]
            
            self.current_results = results
            self.results_table.setRowCount(0)
            if not results:
                self.results_table.setRowCount(1)
                no_item = QTableWidgetItem("Нет автомобилей по выбранным критериям")
                no_item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.results_table.setItem(0, 0, no_item)
                self.results_table.setSpan(0, 0, 1, 6)
                self.status_bar.showMessage("Ничего не найдено")
                self.current_results = []
            else:
                self.results_table.setRowCount(len(results))
                for i, car in enumerate(results):
                    self.results_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                    self.results_table.setItem(i, 1, QTableWidgetItem(car["brand"]))
                    self.results_table.setItem(i, 2, QTableWidgetItem(car["model"]))
                    self.results_table.setItem(i, 3, QTableWidgetItem(car["body_type"]))
                    formatted_price = f"{car['price']:,}".replace(",", " ")
                    price_item = QTableWidgetItem(formatted_price)
                    price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.results_table.setItem(i, 4, price_item)
                    power_item = QTableWidgetItem(str(car["power"]))
                    power_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.results_table.setItem(i, 5, power_item)
                self.status_bar.showMessage(f"Найдено {len(results)} автомобилей")
                    
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка ввода", 
                               f"Введите корректные числовые значения.\n{str(e)}")
            self.status_bar.showMessage("Ошибка ввода данных")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            self.status_bar.showMessage("Ошибка при выполнении поиска")
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if self.db:
            self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Установка стиля приложения
    app.setStyle('Fusion')
    
    window = CarSelectionApp()
    window.show()
    
    sys.exit(app.exec())
