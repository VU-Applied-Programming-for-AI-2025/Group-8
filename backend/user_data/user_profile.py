from typing import List, Tuple

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
            hight: float,
            weight: float,
            skin_color: str,
            country: str,
            medication: List[str] = [],
            diet: List[str] = [],
            existing_conditions: List[str] = [],
            allergies: List[str] = []
            ) -> None:
        
        """
        Initializes a User Profile object.

        Parameters:
            username (str): The username of the user.
            password (str): The password of the user.
            name (str): The name of the user.
            age (int): The age of the user.
            sex (str): The sex of the user (male/female)
            hight (float): The hight of the user in cm.
            weight (float): The weight of the user in kg.
            skin_color (str): The skin color of the user (light, medium, dark).
            country (str): The country where the user lives.
            medication (List[str]): The medications that the user consumes.
            diet (List[str]): The user's diet's wishes (Gluten Free, Ketogenic, Vegetarian, Lacto-Vegetarian, Ovo-Vegetarian, Vegan, Pescetarian, Paleo, Primal, Low FODMAP, Whole30)
            existing_conditions (List[str]): The user's existing conditions.
            allergies (List[str]): The users allergies.
        """
        self.username = username
        self.password = password
        self.name = name
        self.age = age
        self.sex = sex
        self.hight = hight
        self.weight = weight
        self.skin_color = skin_color
        self.country = country
        self.medication = medication
        self.diet = diet
        self.existing_conditions = existing_conditions
        self.allergies = allergies


class UsersData:
    """
    Class representing a data storage of the users.
    """
    def __init__(self)-> None:
        """
        Initializes a Userdata object. 
        Creates an empty dictionary with username as the keys and their corresponding userprofile username as the value.
        """
        self.users = {} 
    
    def add_user(self, user_profile: UserProfile)-> None:
        """
        Add's a user profile to the users dictionary.
        If the username already exists in the database, it raises a ValueError.
        :param user_profile (UserProfile): A user profile object.
        """
        username: str = user_profile.username
        if username in self.users:
            raise ValueError(f"User with username '{username}' already exists.")
        self.users[username] = user_profile

    def get_user(self, username: str) -> UserProfile:
        """
        Returns the user profile object for the given username.
        :param username (str): The username of the user.
        :return (UserProfile): The user profile object for the given username.
        """
        return self.users.get(username, None)

    def user_authentication(self, username: str, password: str)-> Tuple[bool, str]:
        """
        Authenticates a user by checking if the provided username matches a stored one and if so, if the password matches the stored one.
        :param username (str): The username given by the user.
        :param password (str): The password given by the user.
        :return (Tuple[bool, str]): True if the parameters match the stored date, False otherwise. Gives a message with the result.
        """
        if username not in self.users:
            return False, 'Username not found in database'
        else:
            user_profile = self.get_user(username)
            if user_profile.username == username and user_profile.password == password:
                return True, "Authentication successful"
            else:
                return False, "Wrong password"
       
