class ExpertSystem:
    """Экспертная система для подбора автомобилей"""
    
    def __init__(self, db):
        self.db = db

    def recommend(self, criteria):
        """
        Получение рекомендаций по автомобилям на основе критериев
        
        Args:
            criteria: словарь с опциональными критериями поиска:
                - brand: марка автомобиля
                - body_type: тип кузова
                - max_price: максимальная цена
                - min_price: минимальная цена
                - min_power: минимальная мощность
                - max_power: максимальная мощность
        
        Returns:
            список словарей с рекомендациями или строка с сообщением об ошибке
        """
        cars = self.db.get_cars(criteria)
        if not cars:
            return []
        
        # Сортировка по цене (по возрастанию)
        # cars уже является списком словарей благодаря dictionary=True в cursor
        recommendations = sorted(cars, key=lambda x: x['price'])
        
        # Возвращаем все подходящие автомобили
        result = []
        for car in recommendations:
            result.append({
                "brand": car['brand'],
                "model": car['model'],
                "body_type": car['body_type'],
                "price": car['price'],
                "power": car['power'],
                "description": car.get('description', '')
            })
        
        return result
