"""
Chat&Talk GPT - Recipe Manager
Provides recipe search functionality using free APIs (TheMealDB)
"""
import requests
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("RecipeManager")

# TheMealDB API endpoints (free, no key required)
MEALDB_BASE_URL = "https://www.themealdb.com/api/json/v1/1"


class RecipeManager:
    """Manages recipe operations using TheMealDB free API"""
    
    def __init__(self, user_agent: str = "ChatAndTalkGPT/1.0 (Personal Assistant)"):
        """
        Initialize the RecipeManager
        
        Args:
            user_agent: User agent string for API requests
        """
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        logger.info("RecipeManager initialized with TheMealDB API")
    
    def _parse_ingredients(self, meal: Dict) -> List[str]:
        """
        Extract ingredients list from meal data
        
        Args:
            meal: Meal data dictionary from API
            
        Returns:
            List of ingredient strings
        """
        ingredients = []
        for i in range(1, 21):
            ingredient = meal.get(f"strIngredient{i}", "")
            measure = meal.get(f"strMeasure{i}", "")
            
            if ingredient and ingredient.strip():
                if measure and measure.strip():
                    ingredients.append(f"{measure.strip()} {ingredient.strip()}")
                else:
                    ingredients.append(ingredient.strip())
        
        return ingredients
    
    def _format_meal_response(self, meal: Dict) -> Dict:
        """
        Format meal data into standardized recipe response
        
        Args:
            meal: Raw meal data from API
            
        Returns:
            Formatted recipe dictionary
        """
        return {
            "id": meal.get("idMeal", ""),
            "name": meal.get("strMeal", ""),
            "category": meal.get("strCategory", ""),
            "area": meal.get("strArea", ""),
            "instructions": meal.get("strInstructions", ""),
            "image": meal.get("strMealThumb", ""),
            "ingredients": self._parse_ingredients(meal),
            "youtube": meal.get("strYoutube", ""),
            "source": meal.get("strSource", ""),
            "tags": meal.get("strTags", "").split(",") if meal.get("strTags") else []
        }
    
    async def search_by_name(self, name: str) -> Dict[str, Any]:
        """
        Search recipes by dish name
        
        Args:
            name: The dish name to search for
            
        Returns:
            Dictionary containing search results
        """
        try:
            url = f"{MEALDB_BASE_URL}/search.php"
            params = {"s": name.strip()}
            
            logger.info(f"Searching recipes by name: {name}")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            meals = data.get("meals") or []
            
            if not meals:
                return {
                    "success": True,
                    "total_results": 0,
                    "recipes": [],
                    "message": f"No recipes found for '{name}'"
                }
            
            recipes = [self._format_meal_response(meal) for meal in meals]
            
            logger.info(f"Found {len(recipes)} recipes for '{name}'")
            
            return {
                "success": True,
                "total_results": len(recipes),
                "recipes": recipes,
                "search_term": name
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout searching recipes for '{name}'")
            return {
                "success": False,
                "error": "Request timed out. Please try again.",
                "total_results": 0,
                "recipes": []
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching recipes: {e}")
            return {
                "success": False,
                "error": f"Failed to search recipes: {str(e)}",
                "total_results": 0,
                "recipes": []
            }
    
    async def search_by_ingredient(self, ingredient: str) -> Dict[str, Any]:
        """
        Find recipes by main ingredient
        
        Args:
            ingredient: The ingredient to search by
            
        Returns:
            Dictionary containing search results
        """
        try:
            url = f"{MEALDB_BASE_URL}/filter.php"
            params = {"i": ingredient.strip()}
            
            logger.info(f"Searching recipes by ingredient: {ingredient}")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            meals = data.get("meals") or []
            
            if not meals:
                return {
                    "success": True,
                    "total_results": 0,
                    "recipes": [],
                    "message": f"No recipes found with ingredient '{ingredient}'"
                }
            
            # Filter response to only include basic info (limited by API)
            recipes = []
            for meal in meals:
                recipes.append({
                    "id": meal.get("idMeal", ""),
                    "name": meal.get("strMeal", ""),
                    "image": meal.get("strMealThumb", ""),
                    "category": "",
                    "area": "",
                    "instructions": "",
                    "ingredients": [],
                    "youtube": "",
                    "source": "",
                    "tags": []
                })
            
            logger.info(f"Found {len(recipes)} recipes with ingredient '{ingredient}'")
            
            return {
                "success": True,
                "total_results": len(recipes),
                "recipes": recipes,
                "search_term": ingredient,
                "note": "For full recipe details, use get_recipe_details with the recipe ID"
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout searching recipes for ingredient '{ingredient}'")
            return {
                "success": False,
                "error": "Request timed out. Please try again.",
                "total_results": 0,
                "recipes": []
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching recipes by ingredient: {e}")
            return {
                "success": False,
                "error": f"Failed to search recipes: {str(e)}",
                "total_results": 0,
                "recipes": []
            }
    
    async def get_random_recipe(self) -> Dict[str, Any]:
        """
        Get a random recipe
        
        Returns:
            Dictionary containing a random recipe
        """
        try:
            url = f"{MEALDB_BASE_URL}/random.php"
            
            logger.info("Fetching random recipe")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            meals = data.get("meals") or []
            
            if not meals:
                return {
                    "success": False,
                    "error": "No random recipe found",
                    "total_results": 0,
                    "recipes": []
                }
            
            recipe = self._format_meal_response(meals[0])
            
            logger.info(f"Found random recipe: {recipe['name']}")
            
            return {
                "success": True,
                "total_results": 1,
                "recipes": [recipe]
            }
            
        except requests.exceptions.Timeout:
            logger.error("Timeout fetching random recipe")
            return {
                "success": False,
                "error": "Request timed out. Please try again.",
                "total_results": 0,
                "recipes": []
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching random recipe: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch random recipe: {str(e)}",
                "total_results": 0,
                "recipes": []
            }
    
    async def get_recipe_details(self, recipe_id: str) -> Dict[str, Any]:
        """
        Get full recipe details by ID
        
        Args:
            recipe_id: The recipe ID to lookup
            
        Returns:
            Dictionary containing full recipe details
        """
        try:
            url = f"{MEALDB_BASE_URL}/lookup.php"
            params = {"i": recipe_id.strip()}
            
            logger.info(f"Fetching recipe details for ID: {recipe_id}")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            meals = data.get("meals") or []
            
            if not meals:
                return {
                    "success": True,
                    "total_results": 0,
                    "recipes": [],
                    "message": f"No recipe found with ID '{recipe_id}'"
                }
            
            recipe = self._format_meal_response(meals[0])
            
            logger.info(f"Found recipe details: {recipe['name']}")
            
            return {
                "success": True,
                "total_results": 1,
                "recipes": [recipe]
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching recipe details for ID '{recipe_id}'")
            return {
                "success": False,
                "error": "Request timed out. Please try again.",
                "total_results": 0,
                "recipes": []
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching recipe details: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch recipe details: {str(e)}",
                "total_results": 0,
                "recipes": []
            }
    
    async def get_categories(self) -> Dict[str, Any]:
        """
        Get all recipe categories
        
        Returns:
            Dictionary containing all categories
        """
        try:
            url = f"{MEALDB_BASE_URL}/list.php"
            params = {"c": "list"}
            
            logger.info("Fetching recipe categories")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            categories = data.get("meals") or []
            
            category_list = [cat.get("strCategory", "") for cat in categories if cat.get("strCategory")]
            
            logger.info(f"Found {len(category_list)} categories")
            
            return {
                "success": True,
                "total_results": len(category_list),
                "categories": category_list
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching categories: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch categories: {str(e)}",
                "total_results": 0,
                "categories": []
            }
    
    async def get_recipes_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get recipes by category
        
        Args:
            category: The category to filter by
            
        Returns:
            Dictionary containing recipes in that category
        """
        try:
            url = f"{MEALDB_BASE_URL}/filter.php"
            params = {"c": category.strip()}
            
            logger.info(f"Fetching recipes for category: {category}")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            meals = data.get("meals") or []
            
            if not meals:
                return {
                    "success": True,
                    "total_results": 0,
                    "recipes": [],
                    "message": f"No recipes found in category '{category}'"
                }
            
            recipes = []
            for meal in meals:
                recipes.append({
                    "id": meal.get("idMeal", ""),
                    "name": meal.get("strMeal", ""),
                    "image": meal.get("strMealThumb", ""),
                    "category": category,
                    "area": "",
                    "instructions": "",
                    "ingredients": [],
                    "youtube": "",
                    "source": "",
                    "tags": []
                })
            
            logger.info(f"Found {len(recipes)} recipes in category '{category}'")
            
            return {
                "success": True,
                "total_results": len(recipes),
                "recipes": recipes,
                "category": category
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching recipes by category: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch recipes: {str(e)}",
                "total_results": 0,
                "recipes": []
            }


# Singleton instance
recipe_manager = RecipeManager()
