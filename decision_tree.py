"""
Дерево решений для подбора автомобилей.
Фильтры применяются последовательно в порядке: тип кузова → цена → марка → мощность.
"""


class FilterNode:
    """Узел дерева решений — один фильтр с переходом к следующему узлу."""

    def __init__(self, name, filter_func, next_node=None):
        """
        Args:
            name: название фильтра (для отладки и отображения)
            filter_func: функция (cars, criteria) -> filtered_cars
            next_node: следующий узел в дереве (FilterNode или None)
        """
        self.name = name
        self.filter_func = filter_func
        self.next_node = next_node

    def evaluate(self, cars, criteria):
        """
        Применить фильтр и передать результат следующему узлу.

        Args:
            cars: список автомобилей (словарей)
            criteria: словарь критериев от пользователя

        Returns:
            отфильтрованный список автомобилей
        """
        filtered = self.filter_func(cars, criteria)
        if self.next_node is None:
            return filtered
        return self.next_node.evaluate(filtered, criteria)


def _filter_body_type(cars, criteria):
    """Фильтр по типу кузова."""
    if not criteria.get("body_type"):
        return cars
    bt = criteria["body_type"].strip()
    return [c for c in cars if c.get("body_type") == bt]


def _filter_price(cars, criteria):
    """Фильтр по диапазону цены."""
    result = cars
    if criteria.get("min_price") is not None:
        min_p = criteria["min_price"]
        result = [c for c in result if c.get("price", 0) >= min_p]
    if criteria.get("max_price") is not None:
        max_p = criteria["max_price"]
        result = [c for c in result if c.get("price", 0) <= max_p]
    return result


def _filter_brand(cars, criteria):
    """Фильтр по марке."""
    if not criteria.get("brand"):
        return cars
    brand = criteria["brand"].strip()
    return [c for c in cars if c.get("brand") == brand]


def _filter_power(cars, criteria):
    """Фильтр по диапазону мощности."""
    result = cars
    if criteria.get("min_power") is not None:
        min_p = criteria["min_power"]
        result = [c for c in result if c.get("power", 0) >= min_p]
    if criteria.get("max_power") is not None:
        max_p = criteria["max_power"]
        result = [c for c in result if c.get("power", 0) <= max_p]
    return result


def build_car_decision_tree():
    """
    Строит дерево решений для подбора автомобилей.
    Порядок фильтров: тип кузова → цена → марка → мощность.

    Returns:
        корневой FilterNode дерева
    """
    power_node = FilterNode("power", _filter_power, next_node=None)
    brand_node = FilterNode("brand", _filter_brand, next_node=power_node)
    price_node = FilterNode("price", _filter_price, next_node=brand_node)
    body_type_node = FilterNode("body_type", _filter_body_type, next_node=price_node)
    return body_type_node


class CarDecisionTree:
    """
    Дерево решений для подбора автомобилей по фильтрам.
    Применяет фильтры в фиксированном порядке, соответствующем узлам дерева.
    """

    def __init__(self):
        self.root = build_car_decision_tree()

    def evaluate(self, cars, criteria):
        """
        Применить дерево решений к списку автомобилей и критериям.

        Args:
            cars: список словарей с полями brand, model, body_type, price, power, description
            criteria: словарь критериев (body_type, min_price, max_price, brand, min_power, max_power)

        Returns:
            отфильтрованный список автомобилей
        """
        if not cars:
            return []
        return self.root.evaluate(cars, criteria)

    def get_filter_order(self):
        """Возвращает порядок применения фильтров (для отображения)."""
        order = []
        node = self.root
        while node:
            order.append(node.name)
            node = node.next_node
        return order
