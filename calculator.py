"""
Chat&Talk GPT - Calculator and Math Solver Module
Provides mathematical calculations, equation solving, and unit conversions
"""
import math
import logging
import re
from typing import Dict, Any, Optional
from fractions import Fraction

logger = logging.getLogger("CalculatorManager")


class CalculatorManager:
    """
    Calculator and Math Solver Manager for Chat&Talk GPT
    Handles mathematical expressions, equations, unit conversions, and provides math help.
    """
    
    def __init__(self):
        """Initialize the Calculator Manager"""
        # Define allowed functions for safe eval
        self.allowed_names = {
            "abs": abs,
            "round": round,
            "floor": math.floor,
            "ceil": math.ceil,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "log10": math.log10,
            "log": math.log,
            "ln": math.log,
            "exp": math.exp,
            "pow": pow,
            "pi": math.pi,
            "e": math.e,
            "factorial": math.factorial,
            "gcd": math.gcd,
            "degrees": math.degrees,
            "radians": math.radians,
            "cosh": math.cosh,
            "sinh": math.sinh,
            "tanh": math.tanh,
        }
        
        # Unit conversion factors
        self.unit_conversions = {
            # Length
            "km_miles": 0.621371,
            "miles_km": 1.60934,
            "m_ft": 3.28084,
            "ft_m": 0.3048,
            "cm_inch": 0.393701,
            "inch_cm": 2.54,
            "m_yard": 1.09361,
            "yard_m": 0.9144,
            "km_m": 1000,
            "m_km": 0.001,
            "cm_m": 0.01,
            "m_cm": 100,
            "mm_inch": 0.0393701,
            "inch_mm": 25.4,
            
            # Weight/Mass
            "kg_lbs": 2.20462,
            "lbs_kg": 0.453592,
            "g_oz": 0.035274,
            "oz_g": 28.3495,
            "kg_g": 1000,
            "g_kg": 0.001,
            "tonne_kg": 1000,
            "kg_tonne": 0.001,
            
            # Temperature (special handling needed)
            "celsius_fahrenheit": "special",
            "fahrenheit_celsius": "special",
            "celsius_kelvin": "special",
            "kelvin_celsius": "special",
            
            # Volume
            "l_gal": 0.264172,
            "gal_l": 3.78541,
            "ml_l": 0.001,
            "l_ml": 1000,
            "l_oz": 33.814,
            "oz_l": 0.0295735,
            
            # Area
            "sqkm_sqmile": 0.386102,
            "sqmile_sqkm": 2.58999,
            "sqm_sqft": 10.7639,
            "sqft_sqm": 0.092903,
            "sqm_sqyard": 1.19599,
            "sqyard_sqm": 0.836127,
            "acre_hectare": 0.404686,
            "hectare_acre": 2.47105,
            
            # Time
            "hour_min": 60,
            "min_hour": 1/60,
            "min_sec": 60,
            "sec_min": 1/60,
            "day_hour": 24,
            "hour_day": 1/24,
            "week_day": 7,
            "day_week": 1/7,
            "year_day": 365,
            "day_year": 1/365,
            
            # Speed
            "kmh_mph": 0.621371,
            "mph_kmh": 1.60934,
            "ms_kmh": 3.6,
            "kmh_ms": 1/3.6,
            
            # Data
            "byte_kb": 0.001,
            "kb_byte": 1000,
            "mb_gb": 0.001,
            "gb_mb": 1000,
            "tb_gb": 1000,
            "gb_tb": 0.001,
        }
        
        # Math help topics
        self.math_help_topics = {
            "area": {
                "circle": "Area = π × r² (r = radius)",
                "triangle": "Area = ½ × base × height",
                "rectangle": "Area = length × width",
                "square": "Area = side²",
                "trapezoid": "Area = ½ × (a + b) × h (a, b = parallel sides)",
                "parallelogram": "Area = base × height"
            },
            "perimeter": {
                "circle": "Circumference = 2 × π × r or π × d",
                "triangle": "Perimeter = a + b + c (sum of sides)",
                "rectangle": "Perimeter = 2 × (length + width)",
                "square": "Perimeter = 4 × side"
            },
            "volume": {
                "sphere": "Volume = (4/3) × π × r³",
                "cube": "Volume = side³",
                "cylinder": "Volume = π × r² × h",
                "cone": "Volume = (1/3) × π × r² × h",
                "pyramid": "Volume = (1/3) × base_area × height"
            },
            "surface_area": {
                "sphere": "Surface area = 4 × π × r²",
                "cube": "Surface area = 6 × side²",
                "cylinder": "Surface area = 2πr² + 2πrh",
                "cone": "Surface area = πr² + πr×s (s = slant height)"
            },
            "trigonometry": {
                "sine": "sin(θ) = opposite / hypotenuse",
                "cosine": "cos(θ) = adjacent / hypotenuse",
                "tangent": "tan(θ) = opposite / adjacent",
                "pythagorean": "a² + b² = c²",
                "law_of_sines": "a/sin(A) = b/sin(B) = c/sin(C)",
                "law_of_cosines": "c² = a² + b² - 2ab×cos(C)"
            },
            "algebra": {
                "quadratic": "x = (-b ± √(b²-4ac)) / 2a",
                "slope": "m = (y₂-y₁) / (x₂-x₁)",
                "point_slope": "y - y₁ = m(x - x₁)",
                "slope_intercept": "y = mx + b",
                "distance": "d = √((x₂-x₁)² + (y₂-y₁)²)",
                "midpoint": "M = ((x₁+x₂)/2, (y₁+y₂)/2)"
            },
            "statistics": {
                "mean": "Sum of values / number of values",
                "median": "Middle value when sorted (or average of middle two)",
                "mode": "Most frequently occurring value",
                "std_dev": "√(Σ(x-mean)² / n)",
                "variance": "Σ(x-mean)² / n"
            },
            "derivatives": {
                "constant": "d/dx(c) = 0",
                "power": "d/dx(xⁿ) = n×xⁿ⁻¹",
                "sum": "d/dx(f+g) = f' + g'",
                "product": "d/dx(f×g) = f'g + fg'",
                "quotient": "d/dx(f/g) = (f'g - fg') / g²",
                "chain": "d/dx(f(g(x))) = f'(g(x)) × g'(x)"
            },
            "integrals": {
                "constant": "∫c dx = cx + C",
                "power": "∫xⁿ dx = xⁿ⁺¹/(n+1) + C (n≠-1)",
                "exp": "∫e^x dx = e^x + C",
                "ln": "∫1/x dx = ln|x| + C",
                "sin": "∫sin(x) dx = -cos(x) + C",
                "cos": "∫cos(x) dx = sin(x) + C"
            }
        }
        
        logger.info("CalculatorManager initialized")
    
    def _preprocess_expression(self, expression: str) -> str:
        """Preprocess the expression to handle special cases"""
        expr = expression.strip()
        
        # Replace ^ with ** for exponentiation
        expr = expr.replace('^', '**')
        
        # Replace 'pi' with math.pi (already in allowed_names)
        # Replace 'e' with math.e (already in allowed_names)
        
        # Handle implicit multiplication: 2(3) -> 2*(3), (2)(3) -> (2)*(3)
        expr = re.sub(r'(\d)\(', r'\1*(', expr)
        expr = re.sub(r'\)(\d)', r')*\1', expr)
        expr = re.sub(r'\) \(', r')*(', expr)
        
        # Handle implicit multiplication with variables: 2x -> 2*x
        expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
        
        return expr
    
    async def calculate(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression string (e.g., "2 + 2", "sqrt(16)")
        
        Returns:
            Dictionary with success status, expression, result, and type
        """
        try:
            # Preprocess the expression
            processed_expr = self._preprocess_expression(expression)
            
            # Create safe evaluation environment
            eval_globals = {**self.allowed_names}
            
            # Evaluate the expression
            result = eval(processed_expr, {"__builtins__": {}}, eval_globals)
            
            # Handle complex numbers
            if isinstance(result, complex):
                return {
                    "success": True,
                    "expression": expression,
                    "result": str(result),
                    "type": "complex"
                }
            
            # Round to reasonable precision
            if isinstance(result, float):
                if result == int(result):
                    result = int(result)
                else:
                    result = round(result, 10)
            
            # Determine operation type
            op_type = "basic"
            if any(func in processed_expr.lower() for func in ['sqrt', 'sin', 'cos', 'tan', 'log', 'ln', 'exp']):
                op_type = "function"
            elif '**' in processed_expr:
                op_type = "exponent"
            
            logger.info(f"Calculated: {expression} = {result}")
            
            return {
                "success": True,
                "expression": expression,
                "result": result,
                "type": op_type
            }
            
        except ZeroDivisionError:
            logger.warning(f"Division by zero in expression: {expression}")
            return {
                "success": False,
                "expression": expression,
                "error": "Division by zero is not allowed",
                "type": "error"
            }
        except SyntaxError as e:
            logger.warning(f"Syntax error in expression: {expression} - {e}")
            return {
                "success": False,
                "expression": expression,
                "error": f"Invalid expression syntax: {str(e)}",
                "type": "error"
            }
        except Exception as e:
            logger.error(f"Calculation error for '{expression}': {e}")
            return {
                "success": False,
                "expression": expression,
                "error": f"Could not evaluate expression: {str(e)}",
                "type": "error"
            }
    
    async def solve_equation(self, equation: str) -> Dict[str, Any]:
        """
        Solve simple equations (linear and quadratic).
        
        Args:
            equation: Equation string (e.g., "2x + 5 = 15", "x^2 - 5x + 6 = 0")
        
        Returns:
            Dictionary with solution(s) and equation type
        """
        try:
            # Remove spaces
            eq = equation.replace(" ", "")
            
            # Check if it's an equation (contains =)
            if "=" not in eq:
                return {
                    "success": False,
                    "equation": equation,
                    "error": "No equation found. Please use format like '2x + 5 = 15'",
                    "type": "error"
                }
            
            # Split by =
            parts = eq.split("=")
            if len(parts) != 2:
                return {
                    "success": False,
                    "equation": equation,
                    "error": "Invalid equation format",
                    "type": "error"
                }
            
            left_side = parts[0]
            right_side = parts[1]
            
            # Move everything to left side: left - right = 0
            combined = f"({left_side})-({right_side})"
            
            # Try to identify quadratic vs linear
            # Check if there's x^2 or x**2
            if "x**2" in combined.replace("x^2", "x**2") or "x^2" in combined:
                return await self._solve_quadratic(equation, combined)
            else:
                return await self._solve_linear(equation, combined)
                
        except Exception as e:
            logger.error(f"Equation solving error for '{equation}': {e}")
            return {
                "success": False,
                "equation": equation,
                "error": f"Could not solve equation: {str(e)}",
                "type": "error"
            }
    
    async def _solve_linear(self, equation: str, combined: str) -> Dict[str, Any]:
        """Solve linear equation ax + b = 0"""
        try:
            # Replace x^2 to avoid confusion and preprocess for implicit multiplication
            expr = combined.replace("x^2", "x**2")
            expr = self._preprocess_expression(expr)
            
            # Use a proper approach: evaluate f(0) and f(1) to get coefficients
            # For linear: f(x) = ax + b
            # f(0) = b, f(1) = a + b
            # So: a = f(1) - f(0), b = f(0)
            
            # Replace x with values for evaluation
            expr_0 = expr.replace("x", "0")
            expr_1 = expr.replace("x", "1")
            
            f0 = eval(expr_0, {"__builtins__": {}}, self.allowed_names)
            f1 = eval(expr_1, {"__builtins__": {}}, self.allowed_names)
            
            b = f0  # constant term when x=0
            a = f1 - f0  # coefficient of x
            
            if a == 0:
                if b == 0:
                    return {
                        "success": True,
                        "equation": equation,
                        "solutions": ["all real numbers"],
                        "type": "linear",
                        "explanation": "Infinite solutions (identity)"
                    }
                else:
                    return {
                        "success": True,
                        "equation": equation,
                        "solutions": [],
                        "type": "linear",
                        "explanation": "No solution (contradiction)"
                    }
            
            x = -b / a
            x = round(x, 10)
            
            return {
                "success": True,
                "equation": equation,
                "solutions": [x],
                "type": "linear",
                "explanation": f"x = {x}"
            }
            
        except Exception as e:
            logger.error(f"Linear solve error: {e}")
            return {
                "success": False,
                "equation": equation,
                "error": f"Could not solve linear equation: {str(e)}",
                "type": "error"
            }
    
    async def _solve_quadratic(self, equation: str, combined: str) -> Dict[str, Any]:
        """Solve quadratic equation ax^2 + bx + c = 0"""
        try:
            # Replace x^2 with x**2 and preprocess for implicit multiplication
            expr = combined.replace("x^2", "x**2")
            expr = self._preprocess_expression(expr)
            
            # Use evaluation at x=0, 1, 2 to get coefficients
            # f(x) = ax² + bx + c
            # f(0) = c
            # f(1) = a + b + c  
            # f(2) = 4a + 2b + c
            
            expr_0 = expr.replace("x", "0")
            expr_1 = expr.replace("x", "1")
            expr_2 = expr.replace("x", "2")
            
            f0 = eval(expr_0, {"__builtins__": {}}, self.allowed_names)
            f1 = eval(expr_1, {"__builtins__": {}}, self.allowed_names)
            f2 = eval(expr_2, {"__builtins__": {}}, self.allowed_names)
            
            # Use finite differences to find coefficients
            c = f0
            a = (f2 - 2*f1 + f0) / 2
            b = (f1 - f0) - a
            
            # If not quadratic, handle as linear
            if abs(a) < 1e-10:
                if abs(b) < 1e-10:
                    if abs(c) < 1e-10:
                        return {
                            "success": True,
                            "equation": equation,
                            "solutions": ["all real numbers"],
                            "type": "linear",
                            "explanation": "Infinite solutions"
                        }
                    else:
                        return {
                            "success": True,
                            "equation": equation,
                            "solutions": [],
                            "type": "linear",
                            "explanation": "No solution"
                        }
                x = -c / b
                return {
                    "success": True,
                    "equation": equation,
                    "solutions": [round(x, 10)],
                    "type": "linear",
                    "explanation": f"x = {round(x, 10)}"
                }
            
            # Calculate discriminant
            discriminant = b**2 - 4*a*c
            
            if discriminant > 0:
                x1 = (-b + math.sqrt(discriminant)) / (2*a)
                x2 = (-b - math.sqrt(discriminant)) / (2*a)
                x1 = round(x1, 10)
                x2 = round(x2, 10)
                solutions = [x1, x2]
                explanation = f"Two real solutions: x = {x1} or x = {x2}"
            elif discriminant == 0:
                x = -b / (2*a)
                x = round(x, 10)
                solutions = [x]
                explanation = f"One repeated solution: x = {x}"
            else:
                # Complex roots
                real = -b / (2*a)
                imag = math.sqrt(-discriminant) / (2*a)
                real = round(real, 10)
                imag = round(imag, 10)
                solutions = [complex(real, imag), complex(real, -imag)]
                explanation = f"Two complex solutions: x = {real} ± {imag}i"
            
            return {
                "success": True,
                "equation": equation,
                "solutions": solutions,
                "type": "quadratic",
                "a": round(a, 10),
                "b": round(b, 10),
                "c": round(c, 10),
                "discriminant": round(discriminant, 10),
                "explanation": explanation
            }
            
        except Exception as e:
            logger.error(f"Quadratic solve error: {e}")
            return {
                "success": False,
                "equation": equation,
                "error": f"Could not solve quadratic equation: {str(e)}",
                "type": "error"
            }
    
    async def calculate_tip(self, amount: float, percentage: float) -> Dict[str, Any]:
        """
        Calculate tip amount and total.
        
        Args:
            amount: Bill amount
            percentage: Tip percentage (e.g., 15 for 15%)
        
        Returns:
            Dictionary with tip amount, total, and breakdown
        """
        try:
            if amount < 0:
                return {
                    "success": False,
                    "error": "Amount cannot be negative",
                    "type": "error"
                }
            
            if percentage < 0:
                return {
                    "success": False,
                    "error": "Percentage cannot be negative",
                    "type": "error"
                }
            
            tip_amount = round(amount * percentage / 100, 2)
            total = round(amount + tip_amount, 2)
            
            return {
                "success": True,
                "bill_amount": amount,
                "tip_percentage": percentage,
                "tip_amount": tip_amount,
                "total_amount": total,
                "type": "tip"
            }
            
        except Exception as e:
            logger.error(f"Tip calculation error: {e}")
            return {
                "success": False,
                "error": f"Could not calculate tip: {str(e)}",
                "type": "error"
            }
    
    async def convert_units(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """
        Convert between units.
        
        Args:
            value: Numeric value to convert
            from_unit: Source unit (e.g., "km", "miles", "kg")
            to_unit: Target unit (e.g., "miles", "km", "lbs")
        
        Returns:
            Dictionary with converted value and conversion info
        """
        try:
            # Normalize units to lowercase
            from_unit = from_unit.lower().strip()
            to_unit = to_unit.lower().strip()
            
            # Handle temperature conversions (special cases)
            if from_unit in ["celsius", "c", "°c"] and to_unit in ["fahrenheit", "f", "°f"]:
                result = value * 9/5 + 32
                return {
                    "success": True,
                    "value": value,
                    "from_unit": "Celsius",
                    "to_unit": "Fahrenheit",
                    "result": round(result, 2),
                    "formula": "°F = °C × 9/5 + 32",
                    "type": "temperature"
                }
            
            if from_unit in ["fahrenheit", "f", "°f"] and to_unit in ["celsius", "c", "°c"]:
                result = (value - 32) * 5/9
                return {
                    "success": True,
                    "value": value,
                    "from_unit": "Fahrenheit",
                    "to_unit": "Celsius",
                    "result": round(result, 2),
                    "formula": "°C = (°F - 32) × 5/9",
                    "type": "temperature"
                }
            
            if from_unit in ["celsius", "c", "°c"] and to_unit in ["kelvin", "k"]:
                result = value + 273.15
                return {
                    "success": True,
                    "value": value,
                    "from_unit": "Celsius",
                    "to_unit": "Kelvin",
                    "result": round(result, 2),
                    "formula": "K = °C + 273.15",
                    "type": "temperature"
                }
            
            if from_unit in ["kelvin", "k"] and to_unit in ["celsius", "c", "°c"]:
                result = value - 273.15
                return {
                    "success": True,
                    "value": value,
                    "from_unit": "Kelvin",
                    "to_unit": "Celsius",
                    "result": round(result, 2),
                    "formula": "°C = K - 273.15",
                    "type": "temperature"
                }
            
            # Normalize unit names for lookup
            unit_aliases = {
                "kilometer": "km", "kilometers": "km",
                "mile": "miles", "miles": "miles",
                "meter": "m", "meters": "m",
                "foot": "ft", "feet": "ft",
                "inch": "inch", "inches": "inch",
                "centimeter": "cm", "centimeters": "cm",
                "millimeter": "mm", "millimeters": "mm",
                "yard": "yard", "yards": "yard",
                "kilogram": "kg", "kilograms": "kg",
                "pound": "lbs", "pounds": "lbs", "lb": "lbs",
                "gram": "g", "grams": "g",
                "ounce": "oz", "ounces": "oz",
                "liter": "l", "liters": "l", "litre": "l", "litres": "l",
                "gallon": "gal", "gallons": "gal",
                "milliliter": "ml", "milliliters": "ml",
                "square_km": "sqkm", "sq_km": "sqkm", "km²": "sqkm",
                "square_mile": "sqmile", "sq_mile": "sqmile", "mi²": "sqmile",
                "square_meter": "sqm", "sq_m": "sqm", "m²": "sqm",
                "square_foot": "sqft", "sq_ft": "sqft", "ft²": "sqft",
                "acre": "acre", "acres": "acre",
                "hectare": "hectare", "hectares": "hectare",
                "hour": "hour", "hours": "hour",
                "minute": "min", "minutes": "min",
                "second": "sec", "seconds": "sec",
                "day": "day", "days": "day",
                "week": "week", "weeks": "week",
                "year": "year", "years": "year",
                "km/h": "kmh", "kmh": "kmh", "kph": "kmh",
                "mph": "mph",
                "m/s": "ms", "mps": "ms",
                "byte": "byte", "bytes": "byte",
                "kilobyte": "kb", "kilobytes": "kb",
                "megabyte": "mb", "megabytes": "mb",
                "gigabyte": "gb", "gigabytes": "gb",
                "terabyte": "tb", "terabytes": "tb",
            }
            
            from_unit_norm = unit_aliases.get(from_unit, from_unit)
            to_unit_norm = unit_aliases.get(to_unit, to_unit)
            
            # Try direct conversion
            conversion_key = f"{from_unit_norm}_{to_unit_norm}"
            reverse_key = f"{to_unit_norm}_{from_unit_norm}"
            
            if conversion_key in self.unit_conversions:
                factor = self.unit_conversions[conversion_key]
                result = value * factor
                return {
                    "success": True,
                    "value": value,
                    "from_unit": from_unit,
                    "to_unit": to_unit,
                    "result": round(result, 6),
                    "conversion_factor": factor,
                    "type": "conversion"
                }
            elif reverse_key in self.unit_conversions:
                factor = self.unit_conversions[reverse_key]
                result = value / factor
                return {
                    "success": True,
                    "value": value,
                    "from_unit": from_unit,
                    "to_unit": to_unit,
                    "result": round(result, 6),
                    "conversion_factor": 1/factor,
                    "type": "conversion"
                }
            else:
                # List available conversions for the from_unit
                available = [k for k in self.unit_conversions.keys() if k.startswith(from_unit_norm + "_")]
                available_from = [k.split("_")[1] for k in available]
                
                return {
                    "success": False,
                    "value": value,
                    "from_unit": from_unit,
                    "to_unit": to_unit,
                    "error": f"Conversion from '{from_unit}' to '{to_unit}' not supported",
                    "available_units": available_from,
                    "type": "error"
                }
                
        except Exception as e:
            logger.error(f"Unit conversion error: {e}")
            return {
                "success": False,
                "error": f"Could not convert units: {str(e)}",
                "type": "error"
            }
    
    async def calculate_percentage(self, value: float, percentage: float) -> Dict[str, Any]:
        """
        Calculate percentage of a value.
        
        Args:
            value: The base value
            percentage: The percentage to calculate (e.g., 20 for 20%)
        
        Returns:
            Dictionary with the calculated percentage and related info
        """
        try:
            result = round(value * percentage / 100, 4)
            
            return {
                "success": True,
                "value": value,
                "percentage": percentage,
                "result": result,
                "formula": f"{percentage}% of {value} = {result}",
                "type": "percentage"
            }
            
        except Exception as e:
            logger.error(f"Percentage calculation error: {e}")
            return {
                "success": False,
                "error": f"Could not calculate percentage: {str(e)}",
                "type": "error"
            }
    
    async def get_math_help(self, topic: str) -> Dict[str, Any]:
        """
        Get math formulas and help for a topic.
        
        Args:
            topic: Topic to get help on (e.g., "area", "trigonometry", "quadratic")
        
        Returns:
            Dictionary with formulas and explanations
        """
        try:
            topic = topic.lower().strip()
            
            # Direct topic match
            if topic in self.math_help_topics:
                return {
                    "success": True,
                    "topic": topic,
                    "formulas": self.math_help_topics[topic],
                    "type": "help"
                }
            
            # Search for partial matches
            results = {}
            for key, formulas in self.math_help_topics.items():
                if topic in key or key in topic:
                    results[key] = formulas
            
            if results:
                return {
                    "success": True,
                    "topic": topic,
                    "matching_topics": results,
                    "type": "help"
                }
            
            # Try to find related topics
            related = []
            for key in self.math_help_topics.keys():
                # Check if any formula name contains the topic
                for formula_name in self.math_help_topics[key].keys():
                    if topic in formula_name:
                        related.append(key)
                        break
            
            return {
                "success": False,
                "topic": topic,
                "error": f"Topic '{topic}' not found",
                "available_topics": list(self.math_help_topics.keys()),
                "related_topics": list(set(related)),
                "type": "error"
            }
            
        except Exception as e:
            logger.error(f"Math help error: {e}")
            return {
                "success": False,
                "error": f"Could not get math help: {str(e)}",
                "type": "error"
            }
    
    async def get_available_conversions(self) -> Dict[str, Any]:
        """
        Get list of available unit conversions.
        
        Returns:
            Dictionary with available conversion categories
        """
        categories = {
            "length": ["km ↔ miles", "m ↔ ft", "cm ↔ inch", "m ↔ yard", "mm ↔ inch"],
            "weight": ["kg ↔ lbs", "g ↔ oz", "kg ↔ g", "tonne ↔ kg"],
            "temperature": ["Celsius ↔ Fahrenheit", "Celsius ↔ Kelvin"],
            "volume": ["L ↔ gal", "mL ↔ L", "L ↔ oz"],
            "area": ["km² ↔ mi²", "m² ↔ ft²", "m² ↔ yd²", "acre ↔ hectare"],
            "time": ["hour ↔ min", "min ↔ sec", "day ↔ hour", "week ↔ day", "year ↔ day"],
            "speed": ["km/h ↔ mph", "m/s ↔ km/h"],
            "data": ["byte ↔ KB", "MB ↔ GB", "GB ↔ TB"]
        }
        
        return {
            "success": True,
            "categories": categories,
            "type": "conversions"
        }


# Create global calculator manager instance
calculator_manager = CalculatorManager()
