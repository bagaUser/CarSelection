import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QComboBox, QCheckBox, QGroupBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QStatusBar, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QCursor
from database import Database
from expert_system import ExpertSystem
from decision_tree import CarDecisionTree

# SQLite не требует конфигурации подключения
# База данных будет использовать файл cars.db в той же директории

class CarSelectionApp(QMainWindow):
    """Графический интерфейс экспертной системы выбора автомобиля на PyQt6"""
    
    def __init__(self):
        super().__init__()
        self.db = None
        self.system = None
        self.decision_tree = None  # Дерево решений по фильтрам (через expert_system)
        self.brands = []
        self.body_types = []
        self.current_results = []  # Сохраняем текущие результаты для tooltip
        
        self.init_ui()
        self.init_database()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Экспертная система выбора автомобиля")
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
        title_label = QLabel("🚗 Подбор автомобиля по характеристикам")
        title_font = QFont("Arial", 20, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Инструкция
        instruction_label = QLabel("Выберите одну или несколько характеристик для поиска:")
        instruction_font = QFont("Arial", 16)
        instruction_label.setFont(instruction_font)
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setStyleSheet("color: #7f8c8d; margin-bottom: 5px;")
        main_layout.addWidget(instruction_label)
        
        # Подсказка о порядке фильтров (дерево решений) — заполняется после init_database
        self.tree_order_label = QLabel("")
        self.tree_order_label.setFont(QFont("Arial", 10))
        self.tree_order_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tree_order_label.setStyleSheet("color: #95a5a6; margin-bottom: 8px;")
        main_layout.addWidget(self.tree_order_label)
        
        # Фрейм для фильтров (порядок = дерево решений: body_type → price → brand → power)
        filters_group = QGroupBox("Критерии поиска")
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
        
        # Таблица результатов
        results_label = QLabel("📊 Результаты поиска:")
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
        
        # Включаем отслеживание мыши для tooltip
        self.results_table.setMouseTracking(True)
        self.results_table.viewport().setMouseTracking(True)
        
        # Подключаем обработчик движения мыши
        self.results_table.cellEntered.connect(self.show_car_tooltip)
        
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
        
    def create_filters(self, layout):
        """Создание элементов фильтров в порядке дерева решений: тип кузова → цена → марка → мощность."""
        # --- Шаг 1: Тип кузова (узел body_type) ---
        step1_label = QLabel("Тип кузова")
        step1_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        step1_label.setStyleSheet("color: #2980b9; margin-top: 4px;")
        layout.addWidget(step1_label)
        body_layout = QHBoxLayout()
        body_label = QLabel("Тип кузова:")
        body_label.setMinimumWidth(150)
        body_label.setFont(QFont("Arial", 11))
        self.body_type_combo = QComboBox()
        self.body_type_combo.setFont(QFont("Arial", 11))
        self.body_type_combo.setEnabled(False)
        self.body_type_check = QCheckBox("Использовать")
        self.body_type_check.setFont(QFont("Arial", 10))
        self.body_type_check.toggled.connect(lambda checked: self.toggle_widget(self.body_type_combo, checked))
        body_layout.addWidget(body_label)
        body_layout.addWidget(self.body_type_combo, 1)
        body_layout.addWidget(self.body_type_check)
        layout.addLayout(body_layout)
        
        # --- Шаг 2: Цена (узел price) ---
        step2_label = QLabel("Цена")
        step2_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        step2_label.setStyleSheet("color: #2980b9; margin-top: 8px;")
        layout.addWidget(step2_label)
        min_price_layout = QHBoxLayout()
        min_price_label = QLabel("Мин. цена (руб.):")
        min_price_label.setMinimumWidth(150)
        min_price_label.setFont(QFont("Arial", 11))
        self.min_price_edit = QLineEdit()
        self.min_price_edit.setFont(QFont("Arial", 11))
        self.min_price_edit.setPlaceholderText("Введите минимальную цену")
        self.min_price_edit.setEnabled(False)
        self.min_price_check = QCheckBox("Использовать")
        self.min_price_check.setFont(QFont("Arial", 10))
        self.min_price_check.toggled.connect(lambda checked: self.toggle_widget(self.min_price_edit, checked))
        min_price_layout.addWidget(min_price_label)
        min_price_layout.addWidget(self.min_price_edit, 1)
        min_price_layout.addWidget(self.min_price_check)
        layout.addLayout(min_price_layout)
        max_price_layout = QHBoxLayout()
        max_price_label = QLabel("Макс. цена (руб.):")
        max_price_label.setMinimumWidth(150)
        max_price_label.setFont(QFont("Arial", 11))
        self.max_price_edit = QLineEdit()
        self.max_price_edit.setFont(QFont("Arial", 11))
        self.max_price_edit.setPlaceholderText("Введите максимальную цену")
        self.max_price_edit.setEnabled(False)
        self.max_price_check = QCheckBox("Использовать")
        self.max_price_check.setFont(QFont("Arial", 10))
        self.max_price_check.toggled.connect(lambda checked: self.toggle_widget(self.max_price_edit, checked))
        max_price_layout.addWidget(max_price_label)
        max_price_layout.addWidget(self.max_price_edit, 1)
        max_price_layout.addWidget(self.max_price_check)
        layout.addLayout(max_price_layout)
        
        # --- Шаг 3: Марка (узел brand) ---
        step3_label = QLabel("Марка")
        step3_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        step3_label.setStyleSheet("color: #2980b9; margin-top: 8px;")
        layout.addWidget(step3_label)
        brand_layout = QHBoxLayout()
        brand_label = QLabel("Марка:")
        brand_label.setMinimumWidth(150)
        brand_label.setFont(QFont("Arial", 11))
        self.brand_combo = QComboBox()
        self.brand_combo.setFont(QFont("Arial", 11))
        self.brand_combo.setEnabled(False)
        self.brand_check = QCheckBox("Использовать")
        self.brand_check.setFont(QFont("Arial", 10))
        self.brand_check.toggled.connect(lambda checked: self.toggle_widget(self.brand_combo, checked))
        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(self.brand_combo, 1)
        brand_layout.addWidget(self.brand_check)
        layout.addLayout(brand_layout)
        
        # --- Шаг 4: Мощность (узел power) ---
        step4_label = QLabel("Мощность")
        step4_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        step4_label.setStyleSheet("color: #2980b9; margin-top: 8px;")
        layout.addWidget(step4_label)
        min_power_layout = QHBoxLayout()
        min_power_label = QLabel("Мин. мощность (л.с.):")
        min_power_label.setMinimumWidth(150)
        min_power_label.setFont(QFont("Arial", 11))
        self.min_power_edit = QLineEdit()
        self.min_power_edit.setFont(QFont("Arial", 11))
        self.min_power_edit.setPlaceholderText("Введите минимальную мощность")
        self.min_power_edit.setEnabled(False)
        self.min_power_check = QCheckBox("Использовать")
        self.min_power_check.setFont(QFont("Arial", 10))
        self.min_power_check.toggled.connect(lambda checked: self.toggle_widget(self.min_power_edit, checked))
        min_power_layout.addWidget(min_power_label)
        min_power_layout.addWidget(self.min_power_edit, 1)
        min_power_layout.addWidget(self.min_power_check)
        layout.addLayout(min_power_layout)
        max_power_layout = QHBoxLayout()
        max_power_label = QLabel("Макс. мощность (л.с.):")
        max_power_label.setMinimumWidth(150)
        max_power_label.setFont(QFont("Arial", 11))
        self.max_power_edit = QLineEdit()
        self.max_power_edit.setFont(QFont("Arial", 11))
        self.max_power_edit.setPlaceholderText("Введите максимальную мощность")
        self.max_power_edit.setEnabled(False)
        self.max_power_check = QCheckBox("Использовать")
        self.max_power_check.setFont(QFont("Arial", 10))
        self.max_power_check.toggled.connect(lambda checked: self.toggle_widget(self.max_power_edit, checked))
        max_power_layout.addWidget(max_power_label)
        max_power_layout.addWidget(self.max_power_edit, 1)
        max_power_layout.addWidget(self.max_power_check)
        layout.addLayout(max_power_layout)
        
    def toggle_widget(self, widget, enabled):
        """Включение/выключение виджета"""
        widget.setEnabled(enabled)
        if isinstance(widget, QLineEdit) and not enabled:
            widget.clear()
        elif isinstance(widget, QComboBox) and not enabled:
            widget.setCurrentIndex(0)
            
    def clear_filters(self):
        """Очистить все фильтры"""
        self.brand_check.setChecked(False)
        self.body_type_check.setChecked(False)
        self.min_price_check.setChecked(False)
        self.max_price_check.setChecked(False)
        self.min_power_check.setChecked(False)
        self.max_power_check.setChecked(False)
        
        self.results_table.setRowCount(0)
        self.status_bar.showMessage("Фильтры очищены")
        
    def init_database(self):
        """Инициализация базы данных"""
        try:
            # SQLite - просто создаем экземпляр, путь к базе определяется автоматически
            self.db = Database()
            self.system = ExpertSystem(self.db)
            self.decision_tree = self.system.decision_tree
            
            # Отображаем порядок фильтров дерева решений
            _filter_names = {
                "body_type": "тип кузова",
                "price": "цена",
                "brand": "марка",
                "power": "мощность",
            }
            order = self.decision_tree.get_filter_order()
            order_ru = " → ".join(_filter_names.get(name, name) for name in order)
            self.tree_order_label.setText(f"Дерево решений: порядок фильтров — {order_ru}")
            
            # Загружаем списки для фильтров
            self.brands = self.db.get_unique_brands()
            self.body_types = self.db.get_unique_body_types()
            
            # Заполняем комбобоксы
            self.brand_combo.addItem("")
            self.brand_combo.addItems(self.brands)
            self.body_type_combo.addItem("")
            self.body_type_combo.addItems(self.body_types)
            
            # Проверяем количество записей через SQLAlchemy
            from sqlalchemy import func
            from database import Car
            try:
                count = self.db.session.query(func.count(Car.id)).scalar()
            except Exception:
                # Если не удалось получить через SQLAlchemy, используем простой запрос
                count = len(self.db.get_cars({}))
            
            if count > 0:
                status_msg = f"База данных подключена. В базе: {count} автомобилей."
            else:
                status_msg = "База данных подключена. База пуста."
                
            self.status_bar.showMessage(status_msg)
            
        except Exception as e:
            error_msg = str(e)
            detailed_msg = (f"Ошибка подключения к базе данных:\n{error_msg}\n\n"
                          f"Убедитесь, что:\n"
                          f"1. Файл cars.db существует или может быть создан\n"
                          f"2. У приложения есть права на чтение/запись в директорию")
            
            QMessageBox.critical(self, "Ошибка подключения", detailed_msg)
            self.status_bar.showMessage("Ошибка подключения к базе данных")
            
    def get_recommendations(self):
        """Получение и отображение рекомендаций"""
        if not self.db or not self.system:
            QMessageBox.critical(self, "Ошибка", "База данных не инициализирована.")
            return
            
        try:
            # Формируем критерии поиска
            criteria = {}
            
            # Марка
            if self.brand_check.isChecked():
                brand = self.brand_combo.currentText()
                if brand:
                    criteria['brand'] = brand
            
            # Тип кузова
            if self.body_type_check.isChecked():
                body_type = self.body_type_combo.currentText()
                if body_type:
                    criteria['body_type'] = body_type
            
            # Минимальная цена
            if self.min_price_check.isChecked():
                min_price_str = self.min_price_edit.text().strip()
                if min_price_str:
                    criteria['min_price'] = int(min_price_str)
            
            # Максимальная цена
            if self.max_price_check.isChecked():
                max_price_str = self.max_price_edit.text().strip()
                if max_price_str:
                    criteria['max_price'] = int(max_price_str)
            
            # Минимальная мощность
            if self.min_power_check.isChecked():
                min_power_str = self.min_power_edit.text().strip()
                if min_power_str:
                    criteria['min_power'] = int(min_power_str)
            
            # Максимальная мощность
            if self.max_power_check.isChecked():
                max_power_str = self.max_power_edit.text().strip()
                if max_power_str:
                    criteria['max_power'] = int(max_power_str)
            
            # Проверка, что хотя бы один критерий выбран
            if not criteria:
                QMessageBox.warning(self, "Предупреждение", 
                                  "Выберите хотя бы одну характеристику для поиска!")
                return
            
            # Валидация числовых значений
            if 'min_price' in criteria and criteria['min_price'] < 0:
                raise ValueError("Минимальная цена должна быть положительным числом")
            if 'max_price' in criteria and criteria['max_price'] < 0:
                raise ValueError("Максимальная цена должна быть положительным числом")
            if 'min_power' in criteria and criteria['min_power'] < 0:
                raise ValueError("Минимальная мощность должна быть положительным числом")
            if 'max_power' in criteria and criteria['max_power'] < 0:
                raise ValueError("Максимальная мощность должна быть положительным числом")
            if 'min_price' in criteria and 'max_price' in criteria:
                if criteria['min_price'] > criteria['max_price']:
                    raise ValueError("Минимальная цена не может быть больше максимальной")
            if 'min_power' in criteria and 'max_power' in criteria:
                if criteria['min_power'] > criteria['max_power']:
                    raise ValueError("Минимальная мощность не может быть больше максимальной")
            
            # Поиск через дерево решений (expert_system использует decision_tree)
            results = self.system.recommend(criteria)
            
            # Сохраняем результаты для tooltip
            self.current_results = results if isinstance(results, list) else []
            
            # Отображаем результаты в таблице
            self.results_table.setRowCount(0)
            
            if isinstance(results, str):
                QMessageBox.information(self, "Результат", results)
                self.status_bar.showMessage("Поиск выполнен")
                self.current_results = []
            else:
                if not results:
                    self.results_table.setRowCount(1)
                    no_results_item = QTableWidgetItem("Нет подходящих автомобилей по указанным критериям")
                    no_results_item.setFlags(Qt.ItemFlag.NoItemFlags)
                    self.results_table.setItem(0, 0, no_results_item)
                    self.results_table.setSpan(0, 0, 1, 6)
                    self.status_bar.showMessage("Автомобили не найдены")
                    self.current_results = []
                else:
                    # Отображаем все результаты сразу
                    self.results_table.setRowCount(len(results))
                    for i, car in enumerate(results):
                        # Номер
                        num_item = QTableWidgetItem(str(i + 1))
                        num_item.setToolTip(self.create_car_tooltip(car))
                        self.results_table.setItem(i, 0, num_item)
                        
                        # Марка
                        brand_item = QTableWidgetItem(car['brand'])
                        brand_item.setToolTip(self.create_car_tooltip(car))
                        self.results_table.setItem(i, 1, brand_item)
                        
                        # Модель
                        model_item = QTableWidgetItem(car['model'])
                        model_item.setToolTip(self.create_car_tooltip(car))
                        self.results_table.setItem(i, 2, model_item)
                        
                        # Тип кузова
                        body_item = QTableWidgetItem(car['body_type'])
                        body_item.setToolTip(self.create_car_tooltip(car))
                        self.results_table.setItem(i, 3, body_item)
                        
                        # Цена (форматированная)
                        formatted_price = f"{car['price']:,}".replace(',', ' ')
                        price_item = QTableWidgetItem(formatted_price)
                        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                        price_item.setToolTip(self.create_car_tooltip(car))
                        self.results_table.setItem(i, 4, price_item)
                        
                        # Мощность
                        power_item = QTableWidgetItem(str(car['power']))
                        power_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                        power_item.setToolTip(self.create_car_tooltip(car))
                        self.results_table.setItem(i, 5, power_item)
                    
                    self.status_bar.showMessage(f"Найдено {len(results)} автомобилей. Наведите курсор на строку для подробной информации.")
                    
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка ввода", 
                               f"Введите корректные числовые значения.\n{str(e)}")
            self.status_bar.showMessage("Ошибка ввода данных")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            self.status_bar.showMessage("Ошибка при выполнении поиска")
    
    def create_car_tooltip(self, car):
        """Создание текста tooltip с подробной информацией об автомобиле"""
        description = car.get('description', 'Описание отсутствует')
        formatted_price = f"{car['price']:,}".replace(',', ' ')
        
        # Форматируем описание, разбивая длинные строки
        max_line_length = 60
        words = description.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_line_length:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        if current_line:
            lines.append(' '.join(current_line))
        
        formatted_description = '\n'.join(lines) if lines else description
        # 2c3e50
        # e9eef2
        # bdc3c7
        tooltip_text = f"""<div style='font-size: 11pt;'>
<b style='font-size: 12pt; color: #edd70e;'>{car['brand']} {car['model']}</b>
<hr style='margin: 5px 0; border: 1px solid #e9eef2;'>
<b>Тип кузова:</b> {car['body_type']}<br>
<b>Цена:</b> <span style='color: #27ae60;'>{formatted_price} руб.</span><br>
<b>Мощность:</b> <span style='color: #3498db;'>{car['power']} л.с.</span>
<hr style='margin: 5px 0; border: 1px solid #e9eef2;'>
<b>Описание:</b><br>
<span style='color: #f4fc97;'>{formatted_description}</span>
</div>"""
        return tooltip_text
    
    def show_car_tooltip(self, row, column):
        """Показать tooltip при наведении на строку"""
        if row < len(self.current_results):
            car = self.current_results[row]
            tooltip_text = self.create_car_tooltip(car)
            
            # Устанавливаем tooltip для всех ячеек в строке
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                if item:
                    item.setToolTip(tooltip_text)
            
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
