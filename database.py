import sys
import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

class Car(Base):
    """Модель автомобиля для SQLAlchemy"""
    __tablename__ = 'cars'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    body_type = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)
    power = Column(Integer, nullable=False)
    description = Column(Text)
    
    def to_dict(self):
        """Преобразование объекта в словарь"""
        return {
            'id': self.id,
            'brand': self.brand,
            'model': self.model,
            'body_type': self.body_type,
            'price': self.price,
            'power': self.power,
            'description': self.description
        }

class Database:
    def __init__(self, db_path='cars.db'):
        """
        Инициализация базы данных SQLite через SQLAlchemy.
        Использует файл cars.db в той же директории, что и приложение.
        
        Args:
            db_path: путь к файлу базы данных (по умолчанию 'cars.db')
        """
        # Определяем путь к базе данных относительно исполняемого файла
        if getattr(sys, 'frozen', False):
            # Если приложение собрано (cx_Freeze, PyInstaller и т.д.)
            base_path = os.path.dirname(sys.executable)
        else:
            # Если запущено как скрипт
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        self.db_path = os.path.join(base_path, db_path)
        self.engine = None
        self.SessionLocal = None
        self.session = None
        self._connect()
    
    def _connect(self):
        """Подключение к SQLite базе данных через SQLAlchemy"""
        try:
            # Создаем engine для SQLite
            database_url = f"sqlite:///{self.db_path}"
            self.engine = create_engine(
                database_url,
                echo=False,  # Установите True для отладки SQL запросов
                connect_args={"check_same_thread": False}  # Для SQLite
            )
            
            # Создаем фабрику сессий
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Создаем сессию
            self.session = self.SessionLocal()
            
            # Создаем таблицы, если их нет
            Base.metadata.create_all(bind=self.engine)
            
            # Инициализируем базу данных
            self._init_database()
            
        except SQLAlchemyError as e:
            error_msg = (
                f"Ошибка подключения к базе данных: {str(e)}\n\n"
                f"Путь к базе данных: {self.db_path}\n\n"
                f"Убедитесь, что:\n"
                f"1. Файл cars.db существует или может быть создан\n"
                f"2. У приложения есть права на чтение/запись в директорию"
            )
            raise ConnectionError(error_msg)
    
    def _init_database(self):
        """Проверка и заполнение базы данных, если она пустая"""
        try:
            # Проверяем количество записей
            count = self.session.query(Car).count()
            
            # Если база пустая, заполняем данными
            if count == 0:
                self._populate_database()
        except SQLAlchemyError as e:
            print(f"Предупреждение при инициализации базы: {e}")
    
    def _populate_database(self):
        """Заполнение базы данных автомобилями"""
        cars_data = [
            # Эконом класс
            Car(brand="Toyota", model="Corolla", body_type="Седан", price=1500000, power=122, description="Надежный седан с отличной экономичностью"),
            Car(brand="Toyota", model="Camry", body_type="Седан", price=2500000, power=181, description="Комфортный бизнес-седан"),
            Car(brand="Toyota", model="RAV4", body_type="Внедорожник", price=3000000, power=203, description="Популярный кроссовер"),
            Car(brand="Honda", model="Civic", body_type="Седан", price=1600000, power=143, description="Спортивный седан с отличной динамикой"),
            Car(brand="Honda", model="CR-V", body_type="Внедорожник", price=2800000, power=190, description="Надежный кроссовер"),
            Car(brand="Honda", model="Accord", body_type="Седан", price=2400000, power=192, description="Просторный седан"),
            Car(brand="Nissan", model="Sentra", body_type="Седан", price=1400000, power=130, description="Доступный седан"),
            Car(brand="Nissan", model="Altima", body_type="Седан", price=2300000, power=188, description="Стильный седан среднего класса"),
            Car(brand="Nissan", model="Rogue", body_type="Внедорожник", price=2700000, power=181, description="Семейный кроссовер"),
            Car(brand="Mazda", model="Mazda3", body_type="Седан", price=1700000, power=155, description="Динамичный седан с отличной управляемостью"),
            Car(brand="Mazda", model="CX-5", body_type="Внедорожник", price=2900000, power=194, description="Стильный кроссовер"),
            Car(brand="Hyundai", model="Elantra", body_type="Седан", price=1450000, power=147, description="Современный седан"),
            Car(brand="Hyundai", model="Sonata", body_type="Седан", price=2200000, power=180, description="Просторный седан"),
            Car(brand="Hyundai", model="Tucson", body_type="Внедорожник", price=2600000, power=177, description="Практичный кроссовер"),
            Car(brand="Kia", model="Rio", body_type="Седан", price=1300000, power=123, description="Бюджетный седан"),
            Car(brand="Kia", model="Optima", body_type="Седан", price=2100000, power=185, description="Стильный седан"),
            Car(brand="Kia", model="Sportage", body_type="Внедорожник", price=2500000, power=177, description="Компактный кроссовер"),
            
            # Средний класс
            Car(brand="Volkswagen", model="Jetta", body_type="Седан", price=1800000, power=150, description="Немецкое качество"),
            Car(brand="Volkswagen", model="Passat", body_type="Седан", price=2700000, power=220, description="Премиальный седан"),
            Car(brand="Volkswagen", model="Tiguan", body_type="Внедорожник", price=3100000, power=220, description="Премиальный кроссовер"),
            Car(brand="Skoda", model="Octavia", body_type="Седан", price=1900000, power=150, description="Практичный седан"),
            Car(brand="Skoda", model="Superb", body_type="Седан", price=2800000, power=220, description="Просторный седан"),
            Car(brand="Skoda", model="Kodiaq", body_type="Внедорожник", price=3200000, power=245, description="Семейный кроссовер"),
            Car(brand="Ford", model="Focus", body_type="Хэтчбек", price=1600000, power=150, description="Динамичный хэтчбек"),
            Car(brand="Ford", model="Fusion", body_type="Седан", price=2300000, power=181, description="Американский седан"),
            Car(brand="Ford", model="Explorer", body_type="Внедорожник", price=3500000, power=300, description="Большой внедорожник"),
            Car(brand="Chevrolet", model="Cruze", body_type="Седан", price=1500000, power=154, description="Доступный седан"),
            Car(brand="Chevrolet", model="Malibu", body_type="Седан", price=2400000, power=163, description="Просторный седан"),
            Car(brand="Chevrolet", model="Equinox", body_type="Внедорожник", price=3000000, power=252, description="Семейный кроссовер"),
            
            # Премиум класс
            Car(brand="Mercedes-Benz", model="C-Class", body_type="Седан", price=3500000, power=204, description="Премиальный седан"),
            Car(brand="Mercedes-Benz", model="E-Class", body_type="Седан", price=5000000, power=245, description="Бизнес-класс"),
            Car(brand="Mercedes-Benz", model="GLC", body_type="Внедорожник", price=4800000, power=211, description="Премиальный кроссовер"),
            Car(brand="BMW", model="3 Series", body_type="Седан", price=3600000, power=184, description="Спортивный седан"),
            Car(brand="BMW", model="5 Series", body_type="Седан", price=5200000, power=249, description="Премиальный седан"),
            Car(brand="BMW", model="X3", body_type="Внедорожник", price=4900000, power=184, description="Спортивный кроссовер"),
            Car(brand="Audi", model="A4", body_type="Седан", price=3400000, power=190, description="Премиальный седан"),
            Car(brand="Audi", model="A6", body_type="Седан", price=5100000, power=245, description="Бизнес-класс"),
            Car(brand="Audi", model="Q5", body_type="Внедорожник", price=4700000, power=252, description="Премиальный кроссовер"),
            Car(brand="Lexus", model="ES", body_type="Седан", price=3700000, power=215, description="Японская надежность"),
            Car(brand="Lexus", model="RX", body_type="Внедорожник", price=5000000, power=295, description="Премиальный кроссовер"),
            Car(brand="Infiniti", model="Q50", body_type="Седан", price=3300000, power=208, description="Спортивный седан"),
            Car(brand="Infiniti", model="QX50", body_type="Внедорожник", price=4500000, power=268, description="Премиальный кроссовер"),
            
            # Спортивные
            Car(brand="Subaru", model="WRX", body_type="Седан", price=2800000, power=268, description="Спортивный седан с полным приводом"),
            Car(brand="Subaru", model="Forester", body_type="Внедорожник", price=2700000, power=182, description="Надежный кроссовер"),
            Car(brand="Mitsubishi", model="Lancer", body_type="Седан", price=1600000, power=148, description="Доступный седан"),
            Car(brand="Mitsubishi", model="Outlander", body_type="Внедорожник", price=2400000, power=166, description="Практичный кроссовер"),
            
            # Дополнительные записи
            Car(brand="Toyota", model="Prius", body_type="Хэтчбек", price=2200000, power=122, description="Гибридный автомобиль"),
            Car(brand="Toyota", model="Highlander", body_type="Внедорожник", price=3800000, power=295, description="Большой кроссовер"),
            Car(brand="Toyota", model="4Runner", body_type="Внедорожник", price=4000000, power=270, description="Внедорожник"),
            Car(brand="Honda", model="Pilot", body_type="Внедорожник", price=3600000, power=280, description="Семейный внедорожник"),
            Car(brand="Honda", model="Ridgeline", body_type="Пикап", price=3500000, power=280, description="Пикап"),
            Car(brand="Nissan", model="Pathfinder", body_type="Внедорожник", price=3400000, power=284, description="Большой кроссовер"),
            Car(brand="Nissan", model="Frontier", body_type="Пикап", price=2800000, power=152, description="Пикап"),
            Car(brand="Mazda", model="CX-9", body_type="Внедорожник", price=3800000, power=250, description="Большой кроссовер"),
            Car(brand="Mazda", model="CX-30", body_type="Внедорожник", price=2200000, power=186, description="Компактный кроссовер"),
            Car(brand="Hyundai", model="Palisade", body_type="Внедорожник", price=4200000, power=291, description="Большой кроссовер"),
            Car(brand="Hyundai", model="Santa Fe", body_type="Внедорожник", price=3200000, power=235, description="Средний кроссовер"),
            Car(brand="Kia", model="Sorento", body_type="Внедорожник", price=3200000, power=191, description="Семейный кроссовер"),
            Car(brand="Kia", model="Telluride", body_type="Внедорожник", price=4100000, power=291, description="Большой кроссовер"),
            Car(brand="Volkswagen", model="Atlas", body_type="Внедорожник", price=3800000, power=276, description="Большой кроссовер"),
            Car(brand="Volkswagen", model="Arteon", body_type="Седан", price=3200000, power=268, description="Спортивный седан"),
            Car(brand="Skoda", model="Kamiq", body_type="Внедорожник", price=1800000, power=110, description="Компактный кроссовер"),
            Car(brand="Ford", model="Edge", body_type="Внедорожник", price=3100000, power=250, description="Средний кроссовер"),
            Car(brand="Ford", model="Mustang", body_type="Купе", price=3500000, power=450, description="Спортивное купе"),
            Car(brand="Chevrolet", model="Traverse", body_type="Внедорожник", price=3600000, power=310, description="Большой кроссовер"),
            Car(brand="Chevrolet", model="Tahoe", body_type="Внедорожник", price=5500000, power=355, description="Большой внедорожник"),
            
            # Премиум дополнения
            Car(brand="Mercedes-Benz", model="GLE", body_type="Внедорожник", price=6500000, power=362, description="Премиальный внедорожник"),
            Car(brand="Mercedes-Benz", model="S-Class", body_type="Седан", price=12000000, power=429, description="Флагманский седан"),
            Car(brand="BMW", model="X5", body_type="Внедорожник", price=6500000, power=340, description="Премиальный внедорожник"),
            Car(brand="BMW", model="7 Series", body_type="Седан", price=11000000, power=340, description="Флагманский седан"),
            Car(brand="Audi", model="Q7", body_type="Внедорожник", price=6300000, power=333, description="Премиальный внедорожник"),
            Car(brand="Audi", model="A8", body_type="Седан", price=10000000, power=340, description="Флагманский седан"),
            Car(brand="Lexus", model="LS", body_type="Седан", price=8500000, power=416, description="Флагманский седан"),
            Car(brand="Lexus", model="LX", body_type="Внедорожник", price=9000000, power=409, description="Люксовый внедорожник"),
            Car(brand="Infiniti", model="QX80", body_type="Внедорожник", price=7500000, power=400, description="Большой внедорожник"),
            
            # Дополнительные бренды
            Car(brand="Volvo", model="S60", body_type="Седан", price=3200000, power=250, description="Безопасный седан"),
            Car(brand="Volvo", model="XC60", body_type="Внедорожник", price=4200000, power=250, description="Безопасный кроссовер"),
            Car(brand="Volvo", model="XC90", body_type="Внедорожник", price=5500000, power=316, description="Большой кроссовер"),
            Car(brand="Jaguar", model="XE", body_type="Седан", price=3500000, power=250, description="Британский седан"),
            Car(brand="Jaguar", model="F-Pace", body_type="Внедорожник", price=4800000, power=340, description="Спортивный кроссовер"),
            Car(brand="Land Rover", model="Discovery", body_type="Внедорожник", price=5200000, power=300, description="Внедорожник"),
            Car(brand="Land Rover", model="Range Rover", body_type="Внедорожник", price=12000000, power=557, description="Люксовый внедорожник"),
            
            # Более дешевые варианты
            Car(brand="Lada", model="Granta", body_type="Седан", price=600000, power=90, description="Бюджетный седан"),
            Car(brand="Lada", model="Vesta", body_type="Седан", price=900000, power=106, description="Популярный седан"),
            Car(brand="Lada", model="XRAY", body_type="Внедорожник", price=1100000, power=106, description="Компактный кроссовер"),
            Car(brand="Renault", model="Logan", body_type="Седан", price=700000, power=82, description="Доступный седан"),
            Car(brand="Renault", model="Duster", body_type="Внедорожник", price=1300000, power=114, description="Доступный кроссовер"),
            Car(brand="Renault", model="Koleos", body_type="Внедорожник", price=2000000, power=171, description="Средний кроссовер"),
            Car(brand="Peugeot", model="308", body_type="Хэтчбек", price=1400000, power=130, description="Французский хэтчбек"),
            Car(brand="Peugeot", model="3008", body_type="Внедорожник", price=2200000, power=165, description="Стильный кроссовер"),
            Car(brand="Citroen", model="C4", body_type="Хэтчбек", price=1300000, power=110, description="Компактный хэтчбек"),
            Car(brand="Citroen", model="C5 Aircross", body_type="Внедорожник", price=2100000, power=180, description="Комфортный кроссовер"),
            
            # Еще записи
            Car(brand="Toyota", model="Yaris", body_type="Хэтчбек", price=1200000, power=109, description="Компактный хэтчбек"),
            Car(brand="Toyota", model="C-HR", body_type="Внедорожник", price=2300000, power=122, description="Стильный кроссовер"),
            Car(brand="Honda", model="Fit", body_type="Хэтчбек", price=1100000, power=130, description="Компактный хэтчбек"),
            Car(brand="Honda", model="HR-V", body_type="Внедорожник", price=2100000, power=141, description="Компактный кроссовер"),
            Car(brand="Nissan", model="Versa", body_type="Седан", price=1000000, power=122, description="Доступный седан"),
            Car(brand="Nissan", model="Kicks", body_type="Внедорожник", price=1500000, power=122, description="Компактный кроссовер"),
            Car(brand="Mazda", model="CX-3", body_type="Внедорожник", price=1800000, power=148, description="Маленький кроссовер"),
            Car(brand="Hyundai", model="Accent", body_type="Седан", price=950000, power=120, description="Бюджетный седан"),
            Car(brand="Hyundai", model="Kona", body_type="Внедорожник", price=1800000, power=147, description="Компактный кроссовер"),
            Car(brand="Kia", model="Forte", body_type="Седан", price=1200000, power=147, description="Доступный седан"),
            Car(brand="Kia", model="Seltos", body_type="Внедорожник", price=1700000, power=147, description="Компактный кроссовер"),
            Car(brand="Ford", model="Fiesta", body_type="Хэтчбек", price=1000000, power=120, description="Компактный хэтчбек"),
            Car(brand="Ford", model="Escape", body_type="Внедорожник", price=2600000, power=250, description="Средний кроссовер"),
            Car(brand="Chevrolet", model="Trax", body_type="Внедорожник", price=1400000, power=155, description="Компактный кроссовер"),
            Car(brand="Chevrolet", model="Blazer", body_type="Внедорожник", price=3200000, power=308, description="Средний кроссовер"),
        ]
        
        try:
            # Добавляем все записи
            self.session.add_all(cars_data)
            self.session.commit()
            print(f"✓ Добавлено {len(cars_data)} автомобилей в базу данных")
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Ошибка при заполнении базы данных: {e}")

    def get_cars(self, criteria):
        """
        Гибкий поиск автомобилей по опциональным критериям
        
        Args:
            criteria: словарь с опциональными ключами:
                - 'brand': марка автомобиля (точное совпадение)
                - 'body_type': тип кузова
                - 'max_price': максимальная цена
                - 'min_price': минимальная цена
                - 'min_power': минимальная мощность
                - 'max_power': максимальная мощность
        
        Returns:
            список словарей с данными автомобилей
        """
        try:
            query = self.session.query(Car)
            
            # Применяем фильтры
            if criteria.get('brand'):
                query = query.filter(Car.brand == criteria['brand'])
            
            if criteria.get('body_type'):
                query = query.filter(Car.body_type == criteria['body_type'])
            
            if criteria.get('max_price'):
                query = query.filter(Car.price <= criteria['max_price'])
            
            if criteria.get('min_price'):
                query = query.filter(Car.price >= criteria['min_price'])
            
            if criteria.get('min_power'):
                query = query.filter(Car.power >= criteria['min_power'])
            
            if criteria.get('max_power'):
                query = query.filter(Car.power <= criteria['max_power'])
            
            # Выполняем запрос и преобразуем в словари
            cars = query.all()
            return [car.to_dict() for car in cars]
            
        except SQLAlchemyError as e:
            print(f"Ошибка при поиске автомобилей: {e}")
            return []
    
    def get_unique_brands(self):
        """Получить список уникальных марок автомобилей"""
        try:
            brands = self.session.query(Car.brand).distinct().order_by(Car.brand).all()
            return [brand[0] for brand in brands]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении марок: {e}")
            return []
    
    def get_unique_body_types(self):
        """Получить список уникальных типов кузова"""
        try:
            body_types = self.session.query(Car.body_type).distinct().order_by(Car.body_type).all()
            return [body_type[0] for body_type in body_types]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении типов кузова: {e}")
            return []

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()
    
    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка контекстного менеджера"""
        self.close()
