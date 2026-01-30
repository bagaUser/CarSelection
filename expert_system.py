from decision_tree import CarDecisionTree


class ExpertSystem:
    """Экспертная система для подбора автомобилей на основе дерева решений по фильтрам."""

    def __init__(self, db):
        self.db = db
        self.decision_tree = CarDecisionTree()

    def recommend(self, criteria):
        """
        Получение рекомендаций по автомобилям на основе критериев.
        Фильтрация выполняется деревом решений в порядке:
        тип кузова → цена → марка → мощность.

        Args:
            criteria: словарь с опциональными критериями поиска:
                - brand: марка автомобиля
                - body_type: тип кузова
                - max_price: максимальная цена
                - min_price: минимальная цена
                - min_power: минимальная мощность
                - max_power: максимальная мощность

        Returns:
            список словарей с рекомендациями
        """
        all_cars = self.db.get_all_cars()
        if not all_cars:
            return []

        filtered_cars = self.decision_tree.evaluate(all_cars, criteria)
        if not filtered_cars:
            return []

        recommendations = sorted(filtered_cars, key=lambda x: x["price"])
        result = []
        for car in recommendations:
            result.append({
                "brand": car["brand"],
                "model": car["model"],
                "body_type": car["body_type"],
                "price": car["price"],
                "power": car["power"],
                "description": car.get("description", ""),
            })
        return result
