from typing import List, Tuple, Dict, Any
import json


class Meal:
    """
    Class representing a user profile in the system.
    """

    def __init__(
        self,
        id: str,
        title: str,
        image: str,
        readyInMinutes: int,
        sourceUrl: str,
        nutrition: Dict[str, List[Dict[str, Any]]],
        summary: str,
        dishTypes: List[str],
        diets: List[str],
        spoonacularSourceUrl: str
    ) -> None:
        """
        Initializes a Meal object.

        Parameters:
            id (id): id of the meal
            title (str): name of the meal.
            image (str): url to the image of the meal.
            nutrition (Dict[str, float]): nutritional info
            summary (str): summary text about the meal
            readyInMinutes (int): how many minutes does it take to get ready. -1 if not set
            sourceUrl (str): url to the source of the recipe
            dishTypes (List[str]): what kind of dish is it (breakfast, drink, lunch, etc)
            diets (List[str]): which diets this meal is good for
            spoonacularSourceUrl (str): url to the spoonacular website
        """
        self.id = id
        self.image = image
        self.title = title
        self.readyInMinutes = readyInMinutes
        self.sourceUrl = sourceUrl
        self.nutrition = nutrition
        self.summary = summary
        self.dishTypes = dishTypes
        self.diets = diets
        self.spoonacularSourceUrl = spoonacularSourceUrl

    def to_dict(self):
        return {
            "id": self.id,
            "image": self.image,
            "title": self.title,
            "readyInMinutes": self.readyInMinutes,
            "sourceUrl": self.sourceUrl,
            "nutrition": self.nutrition,
            "summary": self.summary,
            "dishTypes": self.dishTypes,
            "diets": self.diets,
            "spoonacularSourceUrl": self.spoonacularSourceUrl
        }


class MealsData:
    """
    Class managing the data storage of the meals data.
    Stores meals in a JSON file.
    """

    def __init__(self, file_path="backend/meal_data/meals_database.json") -> None:
        """
        Initializes a MealsData object. Loads meals from the meals_database.json file if it exists.
        :param file_path (str): The path to the JSON file where meals are stored.
        """
        self.meals = {}
        self.file_path = file_path
        self.load_from_file()

    def add_meal(self, meal: Meal) -> None:
        """
        Add's a new meal to the data file.
        If the meal id already exists in the database, it raises a ValueError.
        :param meal (Meal): A meal object that will be added to the storage.
        """
        id: int = meal.id
        if id in self.meals:
            raise ValueError(f"Meal with id '{id}' already exists.")
        self.meals[id] = meal
        self.save_to_file()

    def save_to_file(self):
        """
        Saves meals to the JSON file where the data will be stored.
        """
        with open(self.file_path, "w") as file:
            json.dump({u: p.to_dict() for u, p in self.meals.items()}, file, indent=2)

    def load_from_file(self):
        """
        Loads user profiles from the JSON file.
        Raises an FileNotFoundError if the file does not exist."""
        try:
            with open(self.file_path, "r") as file:
                meals_data = json.load(file)
                for meal_id, meal in meals_data.items():
                    self.meals[meal_id] = Meal(**meal)
        except FileNotFoundError:
            pass

    def get_meal(self, id: int) -> Meal:
        """
        Returns the meal object for the given id. If no meal is found, it returns None.
        :param id (int): The id of the meal.
        :return (Meal): The meal object for the given id.
        """
        return self.meals.get(id, None)
