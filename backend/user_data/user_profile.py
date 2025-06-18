from typing import List, Tuple, Dict
import json


class UserProfile:
    """
    Class representing a user profile in the system.
    """

    def __init__(
        self,
        username: str,
        password: str,
        name: str,
        age: int,
        sex: str,
        height: float,
        weight: float,
        skin_color: str,
        country: str,
        medication: List[str] = [],
        diet: List[str] = [],
        existing_conditions: List[str] = [],
        allergies: List[str] = [],
        saved_recipes=[],
        analysis_results: Dict[str, int] = {},
        mealplan=[],
    ) -> None:
        """
        Initializes a User Profile object.

        Parameters:
            username (str): The username of the user.
            password (str): The password of the user.
            name (str): The name of the user.
            age (int): The age of the user.
            sex (str): The sex of the user (male/female)
            height (float): The height of the user in cm.
            weight (float): The weight of the user in kg.
            skin_color (str): The skin color of the user (light, medium, dark).
            country (str): The country where the user lives.
            medication (List[str]): The medications that the user consumes.
            diet (List[str]): The user's diet's wishes (none, gluten free, ketogenic, vegetarian, lacto-vegetarian, ovo-vegetarian, vegan, pescetarian, paloe, primal, low fodmap, whole30).
            existing_conditions (List[str]): The user's existing conditions.
            allergies (List[str]): The users allergies.
            saved_recipes
            analysis_results
            mealplan: The user's generated meal plan.
        """
        self.username = username
        self.password = password
        self.name = name
        self.age = age
        self.sex = sex
        self.height = height
        self.weight = weight
        self.skin_color = skin_color
        self.country = country
        self.medication = medication
        self.diet = diet
        self.existing_conditions = existing_conditions
        self.allergies = allergies
        self.saved_recipes = saved_recipes
        self.analysis_results = analysis_results
        self.mealplan = mealplan

        # Validates the information
        if not username:
            raise ValueError("Username is required")
        if not password:
            raise ValueError("Password is required")
        if not name:
            raise ValueError("Name is required")
        if not isinstance(age, int):
            raise ValueError(
                f"Age needs to be an integer, but it was {type(age)} and the value was {age}"
            )
        if not age:
            raise ValueError("Age is required")
        if not sex:
            raise ValueError("Sex is required")
        if not isinstance(height, float):
            raise ValueError("Height needs to be a float")
        if not height:
            raise ValueError("Height is required")
        if not isinstance(weight, float):
            raise ValueError(
                f"Weight must be a float, but it was {type(weight)} and the value was {weight}"
            )
        if not weight:
            raise ValueError("Weight is required")
        if not skin_color:
            raise ValueError("Skin color is required")
        if not country:
            raise ValueError("Country is required")


class UsersData:
    """
    Class managing the data storage of the user profiles.
    Stores user profiles in a JSON file.
    """

    def __init__(self, file_path="backend/user_data/users.json") -> None:
        """
        Initializes a Userdata object. Loads user profiles from the users.json file if it exists.
        :param file_path (str): The path to the JSON file where user profiles are stored.
        """
        self.users = {}
        self.file_path = file_path
        self.load_from_file()

    def add_user(self, user_profile: UserProfile) -> None:
        """
        Add's a new user profile to the data file.
        If the username already exists in the database, it raises a ValueError.
        :param user_profile (UserProfile): A user profile object that will be added to the storage.
        """
        username: str = user_profile.username
        if username in self.users:
            raise ValueError(f"User with username '{username}' already exists.")
        self.users[username] = user_profile
        self.save_to_file()

    def save_to_file(self):
        """
        Saves user profiles to the JSON file where the data will be stored.
        """
        with open(self.file_path, "w") as file:
            json.dump({u: vars(p) for u, p in self.users.items()}, file)

    def load_from_file(self):
        """
        Loads user profiles from the JSON file.
        Raises an FileNotFoundError if the file does not exist."""
        try:
            with open(self.file_path, "r") as file:
                user_data = json.load(file)
                for username, user_profile in user_data.items():
                    self.users[username] = UserProfile(**user_profile)
        except FileNotFoundError:
            pass

    def get_user(self, username: str) -> UserProfile:
        """
        Returns the user profile object for the given username. If no user is found, it returns None.
        :param username (str): The username of the user.
        :return (UserProfile): The user profile object for the given username.
        """
        return self.users.get(username, None)

    def user_authentication(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticates a user by checking if the provided username matches a stored one and if so, if the password matches the stored one.
        :param username (str): The username given by the user.
        :param password (str): The password given by the user.
        :return (Tuple[bool, str]): True if the parameters match the stored date, False otherwise. Gives a message with the result.
        """
        if username not in self.users:
            return False, "Username not found in database"
        else:
            user_profile = self.get_user(username)
            if user_profile.username == username and user_profile.password == password:
                return True, "Authentication successful"
            else:
                return False, "Wrong password"
