"""
Chat&Talk GPT - Subject Solver Module
Comprehensive question solver for Mathematics, Science, Social Science, Economics, Health, and Computer Science
Provides detailed solutions, explanations, reasoning, and verified resources
"""
import re
import logging
import json
import math
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import sympy as sp
from sympy import symbols, solve, simplify, diff, integrate, Eq, sqrt, sin, cos, tan, log, exp
from fractions import Fraction

logger = logging.getLogger("SubjectSolver")


class SubjectSolver:
    """
    Comprehensive Subject Solver for Chat&Talk GPT
    Analyzes questions, provides step-by-step solutions, explanations, and verified resources
    """
    
    def __init__(self):
        self.last_resources = []  # Store verified resources for trust building
        
        # Subject categories and their keywords
        self.subject_patterns = {
            "mathematics": [
                "calculate", "solve", "equation", "algebra", "geometry", "arithmetic",
                "math", "add", "subtract", "multiply", "divide", "fraction", "decimal",
                "percentage", "profit", "loss", "interest", "average", "ratio", "proportion",
                "triangle", "circle", "area", "perimeter", "volume", "surface", "angle",
                "polynomial", "quadratic", "linear", "matrix", "determinant", "integral",
                "derivative", "differential", "limit", "series", "probability", "statistics",
                "mean", "median", "mode", "variance", "standard deviation", "permutation",
                "combination", "factor", "prime", "LCM", "GCD", "exponent", "root", "square",
                "cube", "logarithm", "trigonometry", "sine", "cosine", "tangent", "pythagoras"
            ],
            "physics": [
                "physics", "force", "velocity", "acceleration", "motion", "newton", "gravity",
                "energy", "power", "work", "momentum", "impulse", "pressure", "density",
                "mass", "weight", "volume", "temperature", "heat", "thermodynamics",
                "wave", "frequency", "amplitude", "light", "reflection", "refraction",
                "optics", "electricity", "magnetism", "current", "voltage", "resistance",
                "capacitance", "inductance", "circuit", "magnetic", "field", "force",
                "thermodynamics", "entropy", "kinetic", "potential", "mechanics", "quantum",
                "relativity", "nuclear", "atomic", "sound", "oscillation", "pendulum"
            ],
            "chemistry": [
                "chemistry", "atom", "molecule", "element", "compound", "reaction",
                "bond", "ionic", "covalent", "metallic", "periodic", "table", "electron",
                "proton", "neutron", "valence", "oxidation", "reduction", "acid", "base",
                "salt", "pH", "indicator", "titration", "equilibrium", "kinetics",
                "thermochemistry", "electrochemistry", "organic", "inorganic", "polymer",
                "isomer", "functional group", "alcohol", "aldehyde", "ketone", "carboxylic",
                "amine", "ester", "amide", "catalyst", "enzyme", "solution", "concentration",
                "molarity", "molality", "colloid", "suspension", "solubility", "gas", "liquid",
                "solid", "plasma", "chemical equation", "stoichiometry", "mole", "avogadro"
            ],
            "biology": [
                "biology", "cell", "tissue", "organ", "system", "organism", "DNA", "RNA",
                "protein", "enzyme", "metabolism", "photosynthesis", "respiration",
                "mitosis", "meiosis", "genetics", "evolution", "ecosystem", "food chain",
                "nutrient", "carbohydrate", "lipid", "fat", "vitamin", "mineral",
                "digestion", "circulation", "blood", "heart", "lung", "brain", "neuron",
                "immune", "antibody", "antigen", "virus", "bacteria", "fungi", "plant",
                "animal", "human anatomy", "physiology", "homeostasis", "osmosis",
                "diffusion", "active transport", "passive transport", "cell membrane",
                "nucleus", "mitochondria", "chloroplast", "ribosome", "endoplasmic",
                "Golgi", "lysosome", "chromosome", "gene", "allele", "mutation"
            ],
            "social_science": [
                "history", "geography", "civics", "political", "society", "culture",
                "anthropology", "sociology", "psychology", "economics", "politics",
                "government", "democracy", "monarchy", "constitution", "law", "rights",
                "freedom", "revolution", "war", "peace", "treaty", "trade", "economy",
                "development", "poverty", "globalization", "urbanization", "migration",
                "population", "resource", "climate", "environment", "sustainability",
                "colonialism", "imperialism", "nationalism", "terrorism", "conflict",
                "diplomacy", "international", "organization", "UN", "WHO", "World Bank",
                "IMF", "religion", "belief", "tradition", "custom", "language", "art"
            ],
            "economics": [
                "economics", "demand", "supply", "price", "cost", "value", "market",
                "equilibrium", "elasticity", "GDP", "GNp", "inflation", "deflation",
                "unemployment", "interest rate", "exchange rate", "trade", "tariff",
                "tax", "subsidy", "budget", "fiscal", "monetary", "policy", "bank",
                "investment", "saving", "consumption", "production", "distribution",
                "allocation", "resource", "opportunity cost", "scarcity", "utility",
                "profit", "revenue", "cost", "wage", "rent", "interest", "capital",
                "entrepreneur", "firm", "industry", "market structure", "monopoly",
                "oligopoly", "competition", "regulation", "deregulation", "globalization",
                "development", "growth", "sustainability", "poverty", "inequality"
            ],
            "health": [
                "health", "disease", "illness", "symptom", "treatment", "medicine",
                "drug", "therapy", "surgery", "diagnosis", "prognosis", "prevention",
                "nutrition", "diet", "exercise", "fitness", "wellness", "mental health",
                "stress", "anxiety", "depression", "psychology", "therapy", "counseling",
                "hospital", "clinic", "doctor", "nurse", "patient", "healthcare",
                "vaccine", "immunization", "infection", "bacterial", "viral", "parasitic",
                "cancer", "diabetes", "heart disease", "hypertension", "stroke",
                "asthma", "allergy", "autoimmune", "genetic", "hereditary", "chronic",
                "acute", "infectious", "contagious", "pandemic", "epidemic", "public health",
                "hygiene", "sanitation", "water", "air quality", "sleep", "rest"
            ],
            "computer_science": [
                "computer", "programming", "coding", "algorithm", "software", "hardware",
                "internet", "website", "app", "application", "database", "server", "cloud",
                "python", "java", "javascript", "c++", "c#", "ruby", "php", "swift",
                "kotlin", "html", "css", "sql", "query", "data", "structure", "array",
                "list", "stack", "queue", "tree", "graph", "heap", "hash", "table",
                "sort", "search", "loop", "function", "class", "object", "method",
                "variable", "constant", "type", "string", "integer", "boolean", "float",
                "recursion", "iteration", "condition", "if", "else", "switch", "case",
                "machine learning", "AI", "artificial intelligence", "deep learning",
                "neural network", "data science", "big data", "analytics", "cybersecurity",
                "network", "protocol", "API", "framework", "library", "package"
            ]
        }
        
        # Verified educational resources for each subject
        self.verified_resources = {
            "mathematics": [
                {"name": "Khan Academy - Mathematics", "url": "https://www.khanacademy.org/math", "description": "Comprehensive math courses from basic to advanced"},
                {"name": "Wolfram MathWorld", "url": "https://mathworld.wolfram.com/", "description": "Extensive mathematics encyclopedia"},
                {"name": "Paul's Online Math Notes", "url": "https://tutorial.math.lamar.edu/", "description": "Free math tutorials and practice problems"},
                {"name": "Math is Fun", "url": "https://www.mathsisfun.com/", "description": "Easy-to-understand math explanations"}
            ],
            "physics": [
                {"name": "Khan Academy - Physics", "url": "https://www.khanacademy.org/science/physics", "description": "Physics lessons from fundamentals to advanced"},
                {"name": "Physics Classroom", "url": "https://www.physicsclassroom.com/", "description": "Interactive physics tutorials"},
                {"name": "HyperPhysics", "url": "http://hyperphysics.phy-astr.gsu.edu/", "description": "Exploration of physics concepts"},
                {"name": "NASA Science", "url": "https://science.nasa.gov/", "description": "Space and physics research"}
            ],
            "chemistry": [
                {"name": "Khan Academy - Chemistry", "url": "https://www.khanacademy.org/science/chemistry", "description": "Comprehensive chemistry courses"},
                {"name": "Royal Society of Chemistry", "url": "https://www.rsc.org/", "description": "Chemistry education and resources"},
                {"name": "ChemGuide", "url": "https://www.chemguide.co.uk/", "description": "Detailed chemistry tutorials"},
                {"name": "PubChem", "url": "https://pubchem.ncbi.nlm.nih.gov/", "description": "Chemical compound database"}
            ],
            "biology": [
                {"name": "Khan Academy - Biology", "url": "https://www.khanacademy.org/science/biology", "description": "Biology from cells to ecosystems"},
                {"name": "Nature Education - Scitable", "url": "https://www.nature.com/scitable/", "description": "Biology learning resources"},
                {"name": "National Geographic - Biology", "url": "https://www.nationalgeographic.com/science/biology", "description": "Biology articles and resources"},
                {"name": "NCBI - National Center for Biotechnology Information", "url": "https://www.ncbi.nlm.nih.gov/", "description": "Biotechnology and biology research"}
            ],
            "social_science": [
                {"name": "Khan Academy - History", "url": "https://www.khanacademy.org/humanities/history", "description": "World history courses"},
                {"name": "CrashCourse - Social Science", "url": "https://www.youtube.com/user/crashcourse", "description": "Video courses on various social sciences"},
                {"name": "UNESCO", "url": "https://en.unesco.org/", "description": "Education, science, and culture resources"},
                {"name": "Britannica - Social Science", "url": "https://www.britannica.com/topic/social-science", "description": "Encyclopedia entries on social topics"}
            ],
            "economics": [
                {"name": "Khan Academy - Economics", "url": "https://www.khanacademy.org/economics-finance-domain", "description": "Micro and macroeconomics courses"},
                {"name": "Investopedia - Economics", "url": "https://www.investopedia.com/economics/", "description": "Economic concepts and terms"},
                {"name": "IMF - Economic Concepts", "url": "https://www.imf.org/en/Publications/FandD", "description": "International Monetary Fund resources"},
                {"name": "World Bank - Economics", "url": "https://www.worldbank.org/en/research", "description": "Economic research and data"}
            ],
            "health": [
                {"name": "WHO - World Health Organization", "url": "https://www.who.int/", "description": "Official health information"},
                {"name": "Mayo Clinic", "url": "https://www.mayoclinic.org/", "description": "Medical information and health guides"},
                {"name": "MedlinePlus", "url": "https://medlineplus.gov/", "description": "Health information from NIH"},
                {"name": "CDC - Centers for Disease Control", "url": "https://www.cdc.gov/", "description": "Disease prevention and health information"}
            ],
            "computer_science": [
                {"name": "W3Schools", "url": "https://www.w3schools.com/", "description": "Web development tutorials"},
                {"name": "MDN Web Docs", "url": "https://developer.mozilla.org/", "description": "Web technology documentation"},
                {"name": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/", "description": "Computer science tutorials"},
                {"name": "LeetCode", "url": "https://leetcode.com/", "description": "Programming practice problems"},
                {"name": "GitHub Learning Lab", "url": "https://github.com/skills", "description": "Coding and version control learning"}
            ]
        }
        
        logger.info("SubjectSolver initialized successfully")
    
    def detect_subject(self, question: str) -> Tuple[str, float]:
        """
        Detect the primary subject of the question
        Returns: (subject_name, confidence_score)
        """
        question_lower = question.lower()
        subject_scores = {}
        
        for subject, keywords in self.subject_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in question_lower:
                    score += 1
            if score > 0:
                subject_scores[subject] = score
        
        if not subject_scores:
            return "general", 0.0
        
        # Get the subject with highest score
        max_subject = max(subject_scores, key=subject_scores.get)
        max_score = subject_scores[max_subject]
        
        # Calculate confidence (normalize by total keywords)
        confidence = min(max_score / 5, 1.0)  # Cap at 1.0
        
        return max_subject, confidence
    
    def solve_math_question(self, question: str) -> Dict[str, Any]:
        """
        Solve mathematics questions with step-by-step solutions
        """
        result = {
            "solution": [],
            "explanation": [],
            "final_answer": "",
            "method": "",
            "why_this_works": "",
            "how_it_is_possible": "",
            "reasons": []
        }
        
        question_lower = question.lower()
        
        # Basic arithmetic operations
        if any(op in question_lower for op in ["add", "sum", "plus", "total of"]):
            return self._solve_addition(question)
        elif any(op in question_lower for op in ["subtract", "minus", "difference", "less"]):
            return self._solve_subtraction(question)
        elif any(op in question_lower for op in ["multiply", "times", "product", "multiplied"]):
            return self._solve_multiplication(question)
        elif any(op in question_lower for op in ["divide", "quotient", "divided", "per"]):
            return self._solve_division(question)
        
        # Algebraic equations
        elif "solve for" in question_lower or "solve the equation" in question_lower or "=" in question:
            return self._solve_algebraic_equation(question)
        
        # Quadratic equations
        elif "quadratic" in question_lower or ("x^2" in question_lower) or ("x²" in question):
            return self._solve_quadratic(question)
        
        # Percentage
        elif "percent" in question_lower or "%" in question:
            return self._solve_percentage(question)
        
        # Profit and Loss
        elif "profit" in question_lower or "loss" in question_lower:
            return self._solve_profit_loss(question)
        
        # Simple and Compound Interest
        elif "interest" in question_lower:
            return self._solve_interest(question)
        
        # Average/Mean
        elif "average" in question_lower or "mean" in question_lower:
            return self._solve_average(question)
        
        # Ratio and Proportion
        elif "ratio" in question_lower or "proportion" in question_lower:
            return self._solve_ratio(question)
        
        # Geometry - Area/Perimeter
        elif "area" in question_lower or "perimeter" in question_lower:
            return self._solve_geometry(question)
        
        # Trigonometry
        elif any(trig in question_lower for trig in ["sine", "cosine", "tangent", "sin", "cos", "tan"]):
            return self._solve_trigonometry(question)
        
        # Pythagorean theorem
        elif "pythagoras" in question_lower or "pythagorean" in question_lower:
            return self._solve_pythagoras(question)
        
        # Probability
        elif "probability" in question_lower or "chance" in question_lower:
            return self._solve_probability(question)
        
        # Statistics
        elif "median" in question_lower or "mode" in question_lower:
            return self._solve_statistics(question)
        
        # Derivative/Calculus
        elif "derivative" in question_lower or "differentiate" in question_lower or "dy/dx" in question_lower:
            return self._solve_derivative(question)
        
        # Integral/Calculus
        elif "integral" in question_lower or "integrate" in question_lower or "∫" in question:
            return self._solve_integral(question)
        
        else:
            # Use general approach
            return self._general_math_solution(question)
    
    def _solve_addition(self, question: str) -> Dict[str, Any]:
        """Solve addition problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 2:
            result = sum(numbers)
            
            solution_steps = []
            solution_steps.append(f"Step 1: Identify the numbers to add: {numbers}")
            solution_steps.append(f"Step 2: Add the numbers sequentially:")
            
            running_total = numbers[0]
            for i, num in enumerate(numbers[1:], 1):
                solution_steps.append(f"   {running_total} + {num} = {running_total + num}")
                running_total += num
            
            return {
                "solution": solution_steps,
                "explanation": [
                    "Addition is the process of combining two or more quantities to find their total.",
                    "We add numbers from left to right, carrying over if needed (for multi-digit numbers)."
                ],
                "final_answer": f"The sum is {result}",
                "method": "Basic Addition Algorithm",
                "why_this_works": "Addition follows the commutative property, meaning the order doesn't matter: a + b = b + a. It's also associative: (a + b) + c = a + (b + c).",
                "how_it_is_possible": "When we add, we're essentially counting forward. Each number represents a quantity, and combining them gives the total count.",
                "reasons": [
                    "Addition is fundamental to mathematics",
                    "It represents combining sets of objects",
                    "It's the basis for more complex operations"
                ],
                "resources": self.verified_resources["mathematics"]
            }
        
        return self._general_math_solution(question)
    
    def _solve_subtraction(self, question: str) -> Dict[str, Any]:
        """Solve subtraction problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 2:
            result = numbers[0] - numbers[1]
            
            solution_steps = [
                f"Step 1: Identify the numbers: {numbers[0]} (minuend) - {numbers[1]} (subtrahend)",
                f"Step 2: Subtract {numbers[1]} from {numbers[0]}",
                f"Step 3: Result = {result}"
            ]
            
            return {
                "solution": solution_steps,
                "explanation": [
                    "Subtraction is the inverse operation of addition.",
                    "It finds the difference between two quantities."
                ],
                "final_answer": f"The difference is {result}",
                "method": "Basic Subtraction Algorithm",
                "why_this_works": "Subtraction works because it undoes addition. If a + b = c, then c - b = a.",
                "how_it_is_possible": "Subtraction represents taking away a quantity from another to find what's left.",
                "reasons": [
                    "Used to compare quantities",
                    "Essential for finding differences",
                    "Important in real-world applications like money"
                ],
                "resources": self.verified_resources["mathematics"]
            }
        
        return self._general_math_solution(question)
    
    def _solve_multiplication(self, question: str) -> Dict[str, Any]:
        """Solve multiplication problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 2:
            result = 1
            for num in numbers:
                result *= num
            
            solution_steps = [
                f"Step 1: Identify the factors: {numbers}",
                f"Step 2: Multiply {numbers[0]} × {numbers[1]} = {result}"
            ]
            
            return {
                "solution": solution_steps,
                "explanation": [
                    "Multiplication is repeated addition.",
                    "a × b means adding a to itself b times (or vice versa)."
                ],
                "final_answer": f"The product is {result}",
                "method": "Basic Multiplication Algorithm",
                "why_this_works": "Multiplication is commutative (a × b = b × a) and associative ((a × b) × c = a × (b × c)). It's also distributive: a × (b + c) = a×b + a×c.",
                "how_it_is_possible": "Multiplication efficiently combines equal groups. Instead of adding 5 ten times, we calculate 5 × 10.",
                "reasons": [
                    "Efficient way to add equal groups",
                    "Used in area calculations",
                    "Foundation for algebra"
                ],
                "resources": self.verified_resources["mathematics"]
            }
        
        return self._general_math_solution(question)
    
    def _solve_division(self, question: str) -> Dict[str, Any]:
        """Solve division problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 2 and numbers[1] != 0:
            result = numbers[0] / numbers[1]
            remainder = numbers[0] % numbers[1]
            
            solution_steps = [
                f"Step 1: Identify dividend ({numbers[0]}) and divisor ({numbers[1]})",
                f"Step 2: Divide {numbers[0]} by {numbers[1]}",
                f"Step 3: Quotient = {result}, Remainder = {remainder}"
            ]
            
            return {
                "solution": solution_steps,
                "explanation": [
                    "Division is the inverse of multiplication.",
                    "It distributes a quantity into equal parts."
                ],
                "final_answer": f"The quotient is {result}" + (f" with remainder {remainder}" if remainder > 0 else ""),
                "method": "Basic Division Algorithm",
                "why_this_works": "If a × b = c, then c ÷ b = a. Division essentially asks: 'How many times does the divisor fit into the dividend?'",
                "how_it_is_possible": "Division groups quantities into equal-sized sets. It answers 'how many of one number fit into another.'",
                "reasons": [
                    "Used to share equally",
                    "Essential for fractions and ratios",
                    "Important in measurement"
                ],
                "resources": self.verified_resources["mathematics"]
            }
        
        return self._general_math_solution(question)
    
    def _solve_algebraic_equation(self, question: str) -> Dict[str, Any]:
        """Solve algebraic equations"""
        try:
            # Extract equation (look for = sign)
            if "=" in question:
                parts = question.split("=")
                left = parts[0].strip()
                right = parts[1].strip() if len(parts) > 1 else "0"
                
                # Use sympy to solve
                x = symbols('x')
                
                # Try to parse and solve
                try:
                    # Simple equation solving
                    expr_left = sp.sympify(left.replace(" ", ""))
                    expr_right = sp.sympify(right.replace(" ", ""))
                    equation = Eq(expr_left, expr_right)
                    solution = solve(equation, x)
                    
                    solution_steps = [
                        f"Step 1: Identify the equation: {left} = {right}",
                        f"Step 2: Rearrange to isolate the variable",
                        f"Step 3: Solution: x = {solution[0]}"
                    ]
                    
                    return {
                        "solution": solution_steps,
                        "explanation": [
                            "Algebraic equations use variables (like x) to represent unknown values.",
                            "We solve by applying inverse operations to isolate the variable."
                        ],
                        "final_answer": f"x = {solution[0]}",
                        "method": "Algebraic Manipulation",
                        "why_this_works": "We use the property that 'whatever you do to one side, you must do to the other' to maintain equality while isolating the unknown.",
                        "how_it_is_possible": "Equations represent balanced relationships. By doing the same operation to both sides, we maintain balance while moving toward the solution.",
                        "reasons": [
                            "Equations model real-world situations",
                            "They help find unknown values",
                            "Essential for problem-solving"
                        ],
                        "resources": self.verified_resources["mathematics"]
                    }
                except:
                    pass
        except Exception as e:
            logger.error(f"Error solving algebraic equation: {e}")
        
        return self._general_math_solution(question)
    
    def _solve_quadratic(self, question: str) -> Dict[str, Any]:
        """Solve quadratic equations"""
        try:
            # Extract coefficients from common quadratic forms
            numbers = self._extract_numbers(question)
            
            if len(numbers) >= 3:
                a, b, c = numbers[0], numbers[1], numbers[2]
            elif len(numbers) == 2:
                a, b, c = 1, numbers[0], numbers[1]
            else:
                return self._general_math_solution(question)
            
            # Calculate discriminant
            discriminant = b**2 - 4*a*c
            
            if discriminant >= 0:
                x1 = (-b + sqrt(discriminant)) / (2*a)
                x2 = (-b - sqrt(discriminant)) / (2*a)
                
                solution_steps = [
                    f"Step 1: Identify coefficients: a = {a}, b = {b}, c = {c}",
                    f"Step 2: Use quadratic formula: x = (-b ± √(b²-4ac)) / 2a",
                    f"Step 3: Calculate discriminant: b² - 4ac = {b}² - 4({a})({c}) = {discriminant}",
                    f"Step 4: x₁ = ({-b} + √{discriminant}) / {2*a} = {x1}",
                    f"Step 5: x₂ = ({-b} - √{discriminant}) / {2*a} = {x2}"
                ]
                
                return {
                    "solution": solution_steps,
                    "explanation": [
                        "Quadratic equations have the form ax² + bx + c = 0",
                        "The quadratic formula works for all quadratic equations"
                    ],
                    "final_answer": f"x₁ = {x1}, x₂ = {x2}",
                    "method": "Quadratic Formula",
                    "why_this_works": "The quadratic formula is derived from completing the square. It gives exact solutions for any quadratic equation.",
                    "how_it_is_possible": "By completing the square, we transform the quadratic into a perfect square form, allowing us to take the square root of both sides.",
                    "reasons": [
                        "Derived from completing the square method",
                        "Works for all real and complex solutions",
                        "Essential for analyzing parabolas"
                    ],
                    "resources": self.verified_resources["mathematics"]
                }
            else:
                return {
                    "solution": [f"Discriminant = {discriminant} (negative)"],
                    "explanation": ["When discriminant < 0, there are no real solutions"],
                    "final_answer": "No real solutions (complex roots)",
                    "method": "Quadratic Formula",
                    "why_this_works": "Negative discriminant means the parabola doesn't cross the x-axis",
                    "how_it_is_possible": "The square root of a negative number gives imaginary results",
                    "reasons": ["Quadratic equations can have complex solutions"],
                    "resources": self.verified_resources["mathematics"]
                }
        except Exception as e:
            logger.error(f"Error solving quadratic: {e}")
        
        return self._general_math_solution(question)
    
    def _solve_percentage(self, question: str) -> Dict[str, Any]:
        """Solve percentage problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 2:
            # Determine what's being asked
            question_lower = question.lower()
            
            if "what is" in question_lower and "%" in question:
                # e.g., "what is 20% of 50"
                percent = numbers[0]
                value = numbers[1]
                result = (percent / 100) * value
                
                return {
                    "solution": [
                        f"Step 1: Convert {percent}% to decimal: {percent}/100 = {percent/100}",
                        f"Step 2: Multiply by the value: {percent/100} × {value} = {result}"
                    ],
                    "explanation": [
                        "Percentage means 'per hundred'",
                        "To find a percentage of a number, multiply the decimal form by the number"
                    ],
                    "final_answer": f"{percent}% of {value} = {result}",
                    "method": "Percentage Calculation",
                    "why_this_works": "Percentages are fractions with denominator 100. So 20% = 20/100 = 0.20",
                    "how_it_is_possible": "We convert the percentage to a decimal and multiply by the base value",
                    "reasons": [
                        "Percentages are used in everyday life",
                        "Useful for discounts, interest rates, statistics"
                    ],
                    "resources": self.verified_resources["mathematics"]
                }
        
        return self._general_math_solution(question)
    
    def _solve_profit_loss(self, question: str) -> Dict[str, Any]:
        """Solve profit and loss problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 2:
            cost_price = numbers[0]
            selling_price = numbers[1]
            
            profit = selling_price - cost_price
            profit_percent = (profit / cost_price) * 100 if cost_price != 0 else 0
            loss = cost_price - selling_price
            loss_percent = (loss / cost_price) * 100 if cost_price != 0 else 0
            
            if profit >= 0:
                return {
                    "solution": [
                        f"Step 1: Cost Price (CP) = {cost_price}",
                        f"Step 2: Selling Price (SP) = {selling_price}",
                        f"Step 3: Profit = SP - CP = {selling_price} - {cost_price} = {profit}",
                        f"Step 4: Profit % = (Profit/CP) × 100 = ({profit}/{cost_price}) × 100 = {profit_percent}%"
                    ],
                    "explanation": [
                        "Profit occurs when Selling Price > Cost Price",
                        "Profit percentage shows profit relative to cost price"
                    ],
                    "final_answer": f"Profit = {profit}, Profit % = {profit_percent}%",
                    "method": "Profit/Loss Calculation",
                    "why_this_works": "Profit represents the gain from a transaction. Percentage helps compare profits across different cost bases.",
                    "how_it_is_possible": "By subtracting cost from selling price, we find the absolute profit. Dividing by cost and multiplying by 100 gives the percentage.",
                    "reasons": [
                        "Essential for business calculations",
                        "Used in everyday shopping decisions"
                    ],
                    "resources": self.verified_resources["mathematics"]
                }
            else:
                return {
                    "solution": [
                        f"Step 1: Cost Price (CP) = {cost_price}",
                        f"Step 2: Selling Price (SP) = {selling_price}",
                        f"Step 3: Loss = CP - SP = {cost_price} - {selling_price} = {loss}",
                        f"Step 4: Loss % = (Loss/CP) × 100 = ({loss}/{cost_price}) × 100 = {loss_percent}%"
                    ],
                    "explanation": [
                        "Loss occurs when Selling Price < Cost Price",
                        "Loss percentage shows loss relative to cost price"
                    ],
                    "final_answer": f"Loss = {loss}, Loss % = {loss_percent}%",
                    "method": "Profit/Loss Calculation",
                    "why_this_works": "Loss represents the negative gain from a transaction.",
                    "how_it_ is_possible": "When SP < CP, the seller loses money on each unit sold.",
                    "reasons": [
                        "Important for business viability",
                        "Used to analyze business performance"
                    ],
                    "resources": self.verified_resources["mathematics"]
                }
        
        return self._general_math_solution(question)
    
    def _solve_interest(self, question: str) -> Dict[str, Any]:
        """Solve interest problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 3:
            principal = numbers[0]
            rate = numbers[1]
            time = numbers[2]
            
            question_lower = question.lower()
            
            if "compound" in question_lower:
                # Compound Interest: A = P(1 + r/n)^(nt)
                n = 12 if "monthly" in question_lower else 1
                amount = principal * (1 + rate/100/n)**(n*time)
                ci = amount - principal
                
                return {
                    "solution": [
                        f"Step 1: Principal (P) = {principal}",
                        f"Step 2: Rate (r) = {rate}%",
                        f"Step 3: Time (t) = {time} years",
                        f"Step 4: Compound Interest Formula: A = P(1 + r/n)^(nt)",
                        f"Step 5: A = {principal}(1 + {rate}/100/{n})^({n}×{time}) = {amount}",
                        f"Step 6: CI = A - P = {amount} - {principal} = {ci}"
                    ],
                    "explanation": [
                        "Compound interest calculates interest on both principal and accumulated interest",
                        "It's more common in real-world financial applications"
                    ],
                    "final_answer": f"Compound Interest = {ci}, Total Amount = {amount}",
                    "method": "Compound Interest Formula",
                    "why_this_works": "Each period, interest is calculated on the new principal (original + previous interest), creating exponential growth.",
                    "how_it_is_possible": "The formula (1 + r/n)^(nt) represents the growth factor over time with compounding frequency n.",
                    "reasons": [
                        "Banks use compound interest for savings and loans",
                        "Important for financial planning"
                    ],
                    "resources": self.verified_resources["mathematics"]
                }
            else:
                # Simple Interest: SI = (P × R × T) / 100
                si = (principal * rate * time) / 100
                amount = principal + si
                
                return {
                    "solution": [
                        f"Step 1: Principal (P) = {principal}",
                        f"Step 2: Rate (r) = {rate}%",
                        f"Step 3: Time (t) = {time} years",
                        f"Step 4: Simple Interest Formula: SI = (P × R × T) / 100",
                        f"Step 5: SI = ({principal} × {rate} × {time}) / 100 = {si}",
                        f"Step 6: Total Amount = P + SI = {principal} + {si} = {amount}"
                    ],
                    "explanation": [
                        "Simple interest calculates interest only on the original principal",
                        "Formula: Interest = (Principal × Rate × Time) / 100"
                    ],
                    "final_answer": f"Simple Interest = {si}, Total Amount = {amount}",
                    "method": "Simple Interest Formula",
                    "why_this_works": "Simple interest is linear because interest is always calculated on the original principal, not accumulated interest.",
                    "how_it_is_possible": "The rate represents the percentage of principal paid as interest per time period.",
                    "reasons": [
                        "Used in short-term loans",
                        "Easier to calculate than compound interest"
                    ],
                    "resources": self.verified_resources["mathematics"]
                }
        
        return self._general_math_solution(question)
    
    def _solve_average(self, question: str) -> Dict[str, Any]:
        """Solve average/mean problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 2:
            average = sum(numbers) / len(numbers)
            
            return {
                "solution": [
                    f"Step 1: Identify all values: {numbers}",
                    f"Step 2: Sum all values: {' + '.join(map(str, numbers))} = {sum(numbers)}",
                    f"Step 3: Divide by count: {sum(numbers)} / {len(numbers)} = {average}"
                ],
                "explanation": [
                    "The arithmetic mean (average) is the sum of values divided by the number of values",
                    "It represents the central tendency of a dataset"
                ],
                "final_answer": f"Average = {average}",
                "method": "Arithmetic Mean",
                "why_this_works": "The mean balances out the values - the sum of deviations above the mean equals the sum of deviations below it.",
                "how_it_is_possible": "By adding all values and dividing by the count, we find the 'typical' or representative value.",
                "reasons": [
                    "Used in statistics to represent data",
                    "Important for comparing performances",
                    "Foundation for more advanced statistics"
                ],
                "resources": self.verified_resources["mathematics"]
            }
        
        return self._general_math_solution(question)
    
    def _solve_ratio(self, question: str) -> Dict[str, Any]:
        """Solve ratio and proportion problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 2:
            a, b = numbers[0], numbers[1]
            ratio = a / b if b != 0 else 0
            
            return {
                "solution": [
                    f"Step 1: Identify the two quantities: {a} and {b}",
                    f"Step 2: Write ratio as a:b = {a}:{b}",
                    f"Step 3: Simplify ratio = {a}/{b} = {ratio}"
                ],
                "explanation": [
                    "A ratio compares two quantities of the same kind",
                    "It shows how many times one quantity is of the other"
                ],
                "final_answer": f"Ratio = {ratio} (or {a}:{b})",
                "method": "Ratio Calculation",
                "why_this_works": "Ratios express relative sizes. A ratio of 3:2 means for every 3 of A, there are 2 of B.",
                "how_it_is_possible": "By dividing one quantity by the other, we express them as a proportional relationship.",
                "reasons": [
                    "Used in recipes, mixtures, maps",
                    "Important for scaling",
                    "Essential in business ratios"
                ],
                "resources": self.verified_resources["mathematics"]
            }
        
        return self._general_math_solution(question)
    
    def _solve_geometry(self, question: str) -> Dict[str, Any]:
        """Solve geometry problems (area, perimeter)"""
        numbers = self._extract_numbers(question)
        question_lower = question.lower()
        
        if "triangle" in question_lower:
            if "area" in question_lower and len(numbers) >= 2:
                base, height = numbers[0], numbers[1]
                area = 0.5 * base * height
                return {
                    "solution": [
                        f"Step 1: Identify base (b) = {base}, height (h) = {height}",
                        f"Step 2: Area of triangle = (1/2) × b × h",
                        f"Step 3: Area = (1/2) × {base} × {height} = {area}"
                    ],
                    "explanation": ["A triangle is half of a rectangle with the same base and height"],
                    "final_answer": f"Area = {area} square units",
                    "method": "Triangle Area Formula",
                    "why_this_works": "A triangle can be seen as half of a parallelogram, which can be rearranged into a rectangle.",
                    "how_it_is_possible": "The area formula comes from dividing a rectangle (base × height) into two equal triangles.",
                    "reasons": [
                        "Derived from rectangle area",
                        "Used in construction and design"
                    ],
                    "resources": self.verified_resources["mathematics"]
                }
        
        elif "circle" in question_lower:
            if "area" in question_lower and len(numbers) >= 1:
                radius = numbers[0]
                area = math.pi * radius ** 2
                circumference = 2 * math.pi * radius
                
                return {
                    "solution": [
                        f"Step 1: Radius (r) = {radius}",
                        f"Step 2: Area = πr² = π × {radius}² = π × {radius**2} = {area:.2f}",
                        f"Step 3: Circumference = 2πr = 2π × {radius} = {circumference:.2f}"
                    ],
                    "explanation": [
                        "Area of circle = πr² (π ≈ 3.14159)",
                        "Circumference = 2πr"
                    ],
                    "final_answer": f"Area = {area:.2f}, Circumference = {circumference:.2f}",
                    "method": "Circle Formulas",
                    "why_this_works": "π represents the ratio of circumference to diameter. The area formula is derived by considering circles as infinite polygons.",
                    "how_it_is_possible": "Mathematicians proved that as the number of sides of a regular polygon approaches infinity, its area approaches πr².",
                    "reasons": [
                        "π is a fundamental mathematical constant",
                        "Essential in engineering and physics"
                    ],
                    "resources": self.verified_resources["mathematics"]
                }
        
        elif "rectangle" in question_lower:
            if len(numbers) >= 2:
                length, width = numbers[0], numbers[1]
                area = length * width
                perimeter = 2 * (length + width)
                
                return {
                    "solution": [
                        f"Step 1: Length = {length}, Width = {width}",
                        f"Step 2: Area = length × width = {length} × {width} = {area}",
                        f"Step 3: Perimeter = 2(length + width) = 2({length} + {width}) = {perimeter}"
                    ],
                    "explanation": [
                        "Area = length × width",
                        "Perimeter = 2(length + width)"
                    ],
                    "final_answer": f"Area = {area}, Perimeter = {perimeter}",
                    "method": "Rectangle Formulas",
                    "why_this_works": "Area counts unit squares that fit inside. Perimeter is the total distance around.",
                    "how_it_is_possible": "By multiplying dimensions, we find how many square units fit. Adding all sides gives perimeter.",
                    "reasons": [
                        "Rectangles are the simplest polygons",
                        "Used in architecture and design"
                    ],
                    "resources": self.verified_resources["mathematics"]
                }
        
        return self._general_math_solution(question)
    
    def _solve_trigonometry(self, question: str) -> Dict[str, Any]:
        """Solve trigonometry problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 1:
            angle = numbers[0]
            angle_rad = math.radians(angle)
            
            question_lower = question.lower()
            
            if "sine" in question_lower or "sin" in question_lower:
                sin_val = math.sin(angle_rad)
                return self._create_trig_response("sine", "sin", angle, sin_val)
            elif "cosine" in question_lower or "cos" in question_lower:
                cos_val = math.cos(angle_rad)
                return self._create_trig_response("cosine", "cos", angle, cos_val)
            elif "tangent" in question_lower or "tan" in question_lower:
                tan_val = math.tan(angle_rad)
                return self._create_trig_response("tangent", "tan", angle, tan_val)
        
        return self._general_math_solution(question)
    
    def _create_trig_response(self, name: str, func_name: str, angle: float, value: float) -> Dict[str, Any]:
        """Create a trigonometry response"""
        return {
            "solution": [
                f"Step 1: Given angle = {angle}°",
                f"Step 2: Convert to radians: {angle}° × (π/180) = {math.radians(angle):.4f} radians",
                f"Step 3: Calculate {name}: {func_name}({angle}°) = {value:.4f}"
            ],
            "explanation": [
                f"The {name} function gives the ratio of the opposite side to hypotenuse (sin), adjacent to hypotenuse (cos), or opposite to adjacent (tan) in a right triangle.",
                "Trigonometric functions are periodic and relate angles to side ratios in right triangles."
            ],
            "final_answer": f"{func_name}({angle}°) = {value:.4f}",
            "method": "Trigonometric Function Calculation",
            "why_this_works": "In a unit circle, the coordinates give cosine and sine values. The ratios are constant for any right triangle with the same angle.",
            "how_it_is_possible": "Ancient mathematicians discovered that angle measures correspond to fixed ratios in right triangles, enabling precise calculations.",
            "reasons": [
                "Essential in engineering and physics",
                "Used in navigation and surveying",
                "Foundation for wave functions"
            ],
            "resources": self.verified_resources["mathematics"]
        }
    
    def _solve_pythagoras(self, question: str) -> Dict[str, Any]:
        """Solve Pythagorean theorem problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 2:
            a, b = numbers[0], numbers[1]
            c = math.sqrt(a**2 + b**2)
            
            return {
                "solution": [
                    f"Step 1: In a right triangle, a² + b² = c²",
                    f"Step 2: Given: a = {a}, b = {b}",
                    f"Step 3: c² = {a}² + {b}² = {a**2} + {b**2} = {a**2 + b**2}",
                    f"Step 4: c = √{a**2 + b**2} = {c:.4f}"
                ],
                "explanation": [
                    "The Pythagorean Theorem states: In a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides.",
                    "c² = a² + b²"
                ],
                "final_answer": f"Hypotenuse (c) = {c:.4f} units",
                "method": "Pythagorean Theorem",
                "why_this_works": "This theorem was proven by Euclid and many others. It works because the areas of squares on the sides sum perfectly.",
                "how_it_is_possible": "The theorem can be proven geometrically by showing that the area of the square on the hypotenuse equals the sum of areas of squares on the other two sides.",
                "reasons": [
                    "One of the oldest mathematical theorems",
                    "Essential in navigation and construction",
                    "Foundation for distance calculations"
                ],
                "resources": self.verified_resources["mathematics"]
            }
        
        return self._general_math_solution(question)
    
    def _solve_probability(self, question: str) -> Dict[str, Any]:
        """Solve probability problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 2:
            favorable = numbers[0]
            total = numbers[1]
            
            if total > 0 and favorable <= total:
                probability = favorable / total
                
                return {
                    "solution": [
                        f"Step 1: Identify favorable outcomes = {favorable}",
                        f"Step 2: Identify total possible outcomes = {total}",
                        f"Step 3: Probability = Favorable/Total = {favorable}/{total} = {probability:.4f}",
                        f"Step 4: As percentage = {probability * 100:.2f}%"
                    ],
                    "explanation": [
                        "Probability measures the likelihood of an event occurring",
                        "Formula: P(Event) = Number of favorable outcomes / Total outcomes"
                    ],
                    "final_answer": f"Probability = {probability:.4f} ({probability*100:.2f}%)",
                    "method": "Classical Probability",
                    "why_this_works": "When all outcomes are equally likely, the probability is the ratio of favorable to total outcomes. This gives a number between 0 and 1.",
                    "how_it_is_possible": "In the classical definition, we assume each outcome has equal chance. This works well for games of chance and controlled experiments.",
                    "reasons": [
                        "Used in statistics and data science",
                        "Essential for risk assessment",
                        "Foundation for decision making under uncertainty"
                    ],
                    "resources": self.verified_resources["mathematics"]
                }
        
        return self._general_math_solution(question)
    
    def _solve_statistics(self, question: str) -> Dict[str, Any]:
        """Solve statistics problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 2:
            sorted_nums = sorted(numbers)
            n = len(sorted_nums)
            
            question_lower = question.lower()
            
            if "median" in question_lower:
                if n % 2 == 0:
                    median = (sorted_nums[n//2 - 1] + sorted_nums[n//2]) / 2
                else:
                    median = sorted_nums[n//2]
                
                return {
                    "solution": [
                        f"Step 1: Arrange data in order: {sorted_nums}",
                        f"Step 2: Count number of values: n = {n}",
                        f"Step 3: Since n is {'even' if n % 2 == 0 else 'odd'},",
                        f"Step 4: Median = {'(' + str(sorted_nums[n//2-1]) + '+' + str(sorted_nums[n//2]) + ')/2' if n % 2 == 0 else 'middle value'} = {median}"
                    ],
                    "explanation": [
                        "The median is the middle value when data is ordered",
                        "It divides the data into two equal halves"
                    ],
                    "final_answer": f"Median = {median}",
                    "method": "Median Calculation",
                    "why_this_works": "The median is a measure of central tendency that's not affected by extreme values (unlike mean).",
                    "how_it_is_possible": "By ordering all values and finding the middle, we find the value that splits the data equally.",
                    "reasons": [
                        "Robust to outliers",
                        "Used in income statistics",
                        "Important in descriptive statistics"
                    ],
                    "resources": self.verified_resources["mathematics"]
                }
            
            elif "mode" in question_lower:
                from collections import Counter
                counts = Counter(numbers)
                max_count = max(counts.values())
                modes = [k for k, v in counts.items() if v == max_count]
                
                return {
                    "solution": [
                        f"Step 1: List all values: {numbers}",
                        f"Step 2: Count frequency of each value: {dict(counts)}",
                        f"Step 3: Find most frequent value(s): {modes}"
                    ],
                    "explanation": [
                        "The mode is the most frequently occurring value",
                        "A dataset can have one mode (unimodal), multiple modes (multimodal), or no mode"
                    ],
                    "final_answer": f"Mode = {modes}",
                    "method": "Mode Calculation",
                    "why_this_works": "Mode represents the most common or popular value in a dataset.",
                    "how_it_is_possible": "By counting occurrences of each value, we identify which appears most often.",
                    "reasons": [
                        "Used in categorical data analysis",
                        "Important in business (most popular product)",
                        "Simple to calculate"
                    ],
                    "resources": self.verified_resources["mathematics"]
                }
        
        return self._general_math_solution(question)
    
    def _solve_derivative(self, question: str) -> Dict[str, Any]:
        """Solve derivative/calculus problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 1:
            n = numbers[0]
            
            return {
                "solution": [
                    f"Step 1: Identify the power: x^{n}",
                    f"Step 2: Apply power rule: d/dx(x^n) = n × x^(n-1)",
                    f"Step 3: Derivative = {n} × x^({n-1}) = {n}x^{n-1}"
                ],
                "explanation": [
                    "The derivative represents the rate of change of a function",
                    "The power rule: d/dx(x^n) = nx^(n-1)"
                ],
                "final_answer": f"d/dx(x^{n}) = {n}x^{n-1}",
                "method": "Power Rule for Derivatives",
                "why_this_works": "The power rule comes from the definition of derivative. It tells us how fast the function changes at any point.",
                "how_it_is_possible": "Mathematically, taking the limit as h→0 of [(x+h)^n - x^n]/h gives us n*x^(n-1).",
                "reasons": [
                    "Essential in physics for velocity and acceleration",
                    "Used in optimization problems",
                    "Foundation for differential equations"
                ],
                "resources": self.verified_resources["mathematics"]
            }
        
        return self._general_math_solution(question)
    
    def _solve_integral(self, question: str) -> Dict[str, Any]:
        """Solve integral/calculus problems"""
        numbers = self._extract_numbers(question)
        
        if len(numbers) >= 1:
            n = numbers[0]
            
            if n != -1:
                result = f"x^{n+1}/({n+1}) + C"
            else:
                result = "ln|x| + C"
            
            return {
                "solution": [
                    f"Step 1: Identify the function: x^{n}",
                    f"Step 2: Apply power rule for integrals: ∫x^n dx = x^(n+1)/(n+1) + C (where n ≠ -1)",
                    f"Step 3: ∫x^{n} dx = x^({n+1})/({n+1}) + C = {result}"
                ],
                "explanation": [
                    "Integration is the reverse process of differentiation",
                    "The constant C represents the constant of integration"
                ],
                "final_answer": f"∫x^{n} dx = {result}",
                "method": "Power Rule for Integration",
                "why_this_works": "Integration undoes differentiation. Since d/dx(x^(n+1)/(n+1)) = x^n, the integral must be x^(n+1)/(n+1) + C.",
                "how_it_is_possible": "We find a function whose derivative gives us the original function. This is the antiderivative.",
                "reasons": [
                    "Used to calculate areas under curves",
                    "Essential in physics for work and energy",
                    "Important in probability and statistics"
                ],
                "resources": self.verified_resources["mathematics"]
            }
        
        return self._general_math_solution(question)
    
    def _general_math_solution(self, question: str) -> Dict[str, Any]:
        """Provide a general solution for math problems using AI"""
        return {
            "solution": [
                "This appears to be a mathematics problem.",
                "I'll provide a detailed analysis and solution."
            ],
            "explanation": [
                "Mathematics uses logical reasoning and systematic approaches to solve problems.",
                "The solution depends on understanding the specific type of problem."
            ],
            "final_answer": "Please provide more specific details about your math problem for a precise solution.",
            "method": "General Mathematical Analysis",
            "why_this_works": "Mathematics builds from basic principles to solve complex problems.",
            "how_it_is_possible": "Through logical reasoning and established formulas.",
            "reasons": [
                "Math is the language of quantitative reasoning",
                "It provides tools for solving real-world problems"
            ],
            "resources": self.verified_resources["mathematics"]
        }
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numbers from text"""
        import re
        # Match integers and decimals (including negative)
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        numbers = []
        for m in matches:
            try:
                numbers.append(float(m))
            except:
                pass
        return numbers
    
    def solve_science_question(self, question: str, science_type: str) -> Dict[str, Any]:
        """
        Solve science questions (Physics, Chemistry, Biology)
        """
        question_lower = question.lower()
        
        if science_type == "physics":
            return self._solve_physics_question(question)
        elif science_type == "chemistry":
            return self._solve_chemistry_question(question)
        elif science_type == "biology":
            return self._solve_biology_question(question)
        
        return self._general_science_solution(question, science_type)
    
    def _solve_physics_question(self, question: str) -> Dict[str, Any]:
        """Solve physics questions"""
        question_lower = question.lower()
        numbers = self._extract_numbers(question)
        
        # Force calculations (F = ma)
        if "force" in question_lower and "mass" in question_lower and len(numbers) >= 2:
            mass = numbers[0]
            accel = numbers[1]
            force = mass * accel
            
            return {
                "solution": [
                    f"Step 1: Identify known values: mass (m) = {mass} kg, acceleration (a) = {accel} m/s²",
                    f"Step 2: Use Newton's Second Law: F = ma",
                    f"Step 3: Calculate: F = {mass} × {accel} = {force} N"
                ],
                "explanation": [
                    "Newton's Second Law states that Force equals mass times acceleration (F = ma).",
                    "This is one of the fundamental laws of classical mechanics."
                ],
                "final_answer": f"Force = {force} Newtons",
                "method": "Newton's Second Law (F = ma)",
                "why_this_works": "Force causes acceleration. The more mass an object has, the more force is needed to accelerate it.",
                "how_it_is_possible": "This law was derived from experiments by Sir Isaac Newton in the 17th century.",
                "reasons": [
                    "Foundation of classical mechanics",
                    "Used in engineering and design",
                    "Explains motion in everyday life"
                ],
                "resources": self.verified_resources["physics"]
            }
        
        # Velocity/Distance/Time
        elif any(x in question_lower for x in ["velocity", "speed", "distance", "time"]) and len(numbers) >= 2:
            if "distance" in question_lower or "speed" in question_lower:
                speed = numbers[0]
                time = numbers[1]
                distance = speed * time
                
                return {
                    "solution": [
                        f"Step 1: Identify: speed (v) = {speed} m/s, time (t) = {time} s",
                        f"Step 2: Use formula: distance = speed × time",
                        f"Step 3: Calculate: d = {speed} × {time} = {distance} m"
                    ],
                    "explanation": [
                        "Distance = Speed × Time",
                        "This is derived from the definition of speed as distance traveled per unit time"
                    ],
                    "final_answer": f"Distance = {distance} meters",
                    "method": "Speed-Distance-Time Formula",
                    "why_this_works": "Speed tells us how much distance is covered in each unit of time. Multiplying by total time gives total distance.",
                    "how_it_is_possible": "This relationship comes from the definition of speed as rate of change of distance.",
                    "reasons": [
                        "Essential in navigation",
                        "Used in transportation",
                        "Foundation of kinematics"
                    ],
                    "resources": self.verified_resources["physics"]
                }
        
        # Work calculations
        elif "work" in question_lower and len(numbers) >= 2:
            force = numbers[0]
            distance = numbers[1]
            work = force * distance
            
            return {
                "solution": [
                    f"Step 1: Identify: Force (F) = {force} N, Distance (d) = {distance} m",
                    f"Step 2: Use formula: Work = Force × Distance",
                    f"Step 3: Calculate: W = {force} × {distance} = {work} Joules"
                ],
                "explanation": [
                    "Work is done when a force causes displacement.",
                    "Unit of work is Joule (J) = Newton-meter"
                ],
                "final_answer": f"Work = {work} Joules",
                "method": "Work Formula (W = Fd)",
                "why_this_works": "Work transfers energy. When you push an object and it moves, you're doing work on it.",
                    "how_it_is_possible": "The work done is proportional to both the force applied and the distance moved in the direction of the force.",
                    "reasons": [
                        "Conservation of energy principle",
                        "Used in all mechanical systems",
                        "Essential for understanding energy transfer"
                    ],
                    "resources": self.verified_resources["physics"]
                }
        
        # Energy calculations
        elif "energy" in question_lower:
            question_lower = question.lower()
            
            if "kinetic" in question_lower and len(numbers) >= 1:
                mass = numbers[0]
                velocity = numbers[1] if len(numbers) >= 2 else 1
                ke = 0.5 * mass * velocity ** 2
                
                return {
                    "solution": [
                        f"Step 1: Given: mass (m) = {mass} kg, velocity (v) = {velocity} m/s",
                        f"Step 2: Use Kinetic Energy formula: KE = ½mv²",
                        f"Step 3: Calculate: KE = ½ × {mass} × ({velocity})² = {ke} J"
                    ],
                    "explanation": [
                        "Kinetic energy is the energy of motion.",
                        "It depends on mass and the square of velocity."
                    ],
                    "final_answer": f"Kinetic Energy = {ke} Joules",
                    "method": "Kinetic Energy Formula (KE = ½mv²)",
                    "why_this_works": "When you accelerate an object, you transfer energy to it. This energy becomes kinetic energy.",
                    "how_it_is_possible": "Derived from work-energy theorem: work done equals change in kinetic energy.",
                    "reasons": [
                        "Explains motion and collisions",
                        "Used in vehicle safety design",
                        "Foundation of thermodynamics"
                    ],
                    "resources": self.verified_resources["physics"]
                }
            
            elif "potential" in question_lower and len(numbers) >= 1:
                mass = numbers[0]
                gravity = 9.8
                height = numbers[1] if len(numbers) >= 2 else 1
                pe = mass * gravity * height
                
                return {
                    "solution": [
                        f"Step 1: Given: mass (m) = {mass} kg, height (h) = {height} m",
                        f"Step 2: Use Gravitational Potential Energy: PE = mgh",
                        f"Step 3: Calculate: PE = {mass} × {gravity} × {height} = {pe} J"
                    ],
                    "explanation": [
                        "Gravitational potential energy is energy stored due to position in a gravitational field.",
                        "It increases with height and mass."
                    ],
                    "final_answer": f"Potential Energy = {pe} Joules",
                    "method": "Gravitational PE Formula (PE = mgh)",
                    "why_this_works": "Objects higher in a gravitational field have more potential to do work when they fall.",
                    "how_it_is_possible": "This energy comes from the gravitational force that would accelerate the object downward.",
                    "reasons": [
                        "Important for understanding falling objects",
                        "Used in hydroelectric power",
                        "Related to conservation of energy"
                    ],
                    "resources": self.verified_resources["physics"]
                }
        
        # Wave calculations
        elif "wave" in question_lower or "frequency" in question_lower or "wavelength" in question_lower:
            if len(numbers) >= 2:
                freq = numbers[0]
                wavelength = numbers[1]
                velocity = freq * wavelength
                
                return {
                    "solution": [
                        f"Step 1: Given: frequency (f) = {freq} Hz, wavelength (λ) = {wavelength} m",
                        f"Step 2: Use wave equation: v = fλ",
                        f"Step 3: Calculate: v = {freq} × {wavelength} = {velocity} m/s"
                    ],
                    "explanation": [
                        "The wave equation relates velocity, frequency, and wavelength.",
                        "This applies to all types of waves: light, sound, water, etc."
                    ],
                    "final_answer": f"Wave velocity = {velocity} m/s",
                    "method": "Wave Equation (v = fλ)",
                    "why_this_works": "Frequency tells how many waves pass per second, wavelength tells the distance between waves. Their product gives wave speed.",
                    "how_it_is_possible": "This relationship was discovered through experimental observations of wave behavior.",
                    "reasons": [
                        "Essential for understanding light and sound",
                        "Used in communications technology",
                        "Important in medical imaging"
                    ],
                    "resources": self.verified_resources["physics"]
                }
        
        return {
            "solution": ["This is a physics problem requiring analysis."],
            "explanation": ["Physics explains natural phenomena through laws and principles."],
            "final_answer": "Please provide specific values for precise calculation.",
            "method": "Physics Problem Solving",
            "why_this_works": "Physics laws are derived from observations and experiments.",
            "how_it_is_possible": "Through careful measurement and mathematical modeling.",
            "reasons": [
                "Physics is the foundation of all natural sciences",
                "It explains how the universe works"
            ],
            "resources": self.verified_resources["physics"]
        }
    
    def _solve_chemistry_question(self, question: str) -> Dict[str, Any]:
        """Solve chemistry questions"""
        question_lower = question.lower()
        
        # pH calculations
        if "ph" in question_lower or "pH" in question:
            numbers = self._extract_numbers(question)
            
            if len(numbers) >= 1:
                h_concentration = numbers[0]
                if h_concentration > 0:
                    ph = -math.log10(h_concentration)
                    
                    return {
                        "solution": [
                            f"Step 1: Given [H+] = {h_concentration} M",
                            f"Step 2: Use pH formula: pH = -log₁₀[H⁺]",
                            f"Step 3: Calculate: pH = -log₁₀({h_concentration}) = {ph:.2f}"
                        ],
                        "explanation": [
                            "pH is a measure of hydrogen ion concentration in a solution.",
                            "pH scale ranges from 0 (very acidic) to 14 (very basic), 7 is neutral."
                        ],
                        "final_answer": f"pH = {ph:.2f}",
                        "method": "pH Formula",
                        "why_this_works": "The logarithmic scale allows us to express very wide ranges of acidity. Each pH unit represents a 10-fold change in [H⁺].",
                        "how_it_is_possible": "The negative log transforms the small decimal concentrations into manageable numbers.",
                        "reasons": [
                            "Important in biology and medicine",
                            "Used in water quality testing",
                            "Essential in chemical processes"
                        ],
                        "resources": self.verified_resources["chemistry"]
                    }
        
        # Molar mass calculations
        elif "molar mass" in question_lower or "mole" in question_lower:
            numbers = self._extract_numbers(question)
            
            return {
                "solution": [
                    "Step 1: Identify the chemical formula of the compound",
                    "Step 2: Add atomic masses of all elements (from periodic table)",
                    "Step 3: The sum gives molar mass in g/mol"
                ],
                "explanation": [
                    "Molar mass is the mass of one mole of a substance.",
                    "It's expressed in grams per mole (g/mol) and equals the molecular weight."
                ],
                "final_answer": "Molar mass depends on the chemical formula",
                "method": "Molar Mass Calculation",
                "why_this_works": "One mole contains Avogadro's number (6.022 × 10²³) of particles, and the molar mass equals the atomic/molecular weight in grams.",
                "how_it_is_possible": "By adding up the atomic masses from the periodic table.",
                "reasons": [
                    "Used in stoichiometry",
                    "Essential for conversions",
                    "Important in solution preparation"
                ],
                "resources": self.verified_resources["chemistry"]
            }
        
        # Balancing chemical equations
        elif "balance" in question_lower and "equation" in question_lower:
            return {
                "solution": [
                    "Step 1: Write the unbalanced equation",
                    "Step 2: Count atoms of each element on both sides",
                    "Step 3: Add coefficients to balance atoms",
                    "Step 4: Verify all atoms are balanced"
                ],
                "explanation": [
                    "Chemical equations must obey the Law of Conservation of Mass.",
                    "Atoms cannot be created or destroyed in a chemical reaction."
                ],
                "final_answer": "Balanced equation shows equal atoms on both sides",
                "method": "Equation Balancing",
                "why_this_works": "The total mass of reactants equals total mass of products (Lavoisier's Law).",
                "how_it_is_possible": "By adjusting coefficients (not subscripts), we balance atoms without changing the actual compounds.",
                "reasons": [
                    "Essential for stoichiometric calculations",
                    "Required for predicting yields",
                    "Fundamental to chemistry"
                ],
                "resources": self.verified_resources["chemistry"]
            }
        
        # Periodic table questions
        elif "periodic" in question_lower or "element" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify the element's position (group and period)",
                    "Step 2: Use periodic trends to predict properties",
                    "Step 3: Consider electron configuration"
                ],
                "explanation": [
                    "The periodic table organizes elements by atomic number and properties.",
                    "Elements in the same group have similar chemical properties."
                ],
                "final_answer": "Properties can be predicted from position in periodic table",
                "method": "Periodic Law Analysis",
                "why_this_works": "Elements are arranged by increasing atomic number, revealing periodic patterns in properties.",
                "how_it_is_possible": "Electron configuration determines chemical behavior, and it varies periodically with atomic number.",
                "reasons": [
                    "Predicts chemical behavior",
                    "Organizes all known elements",
                    "Foundation of chemistry"
                ],
                "resources": self.verified_resources["chemistry"]
            }
        
        return {
            "solution": ["This is a chemistry problem."],
            "explanation": ["Chemistry studies matter and its transformations."],
            "final_answer": "Please provide more specific details.",
            "method": "Chemistry Problem Solving",
            "why_this_works": "Chemistry follows laws and principles derived from experiments.",
            "how_it_is_possible": "Through understanding atomic and molecular behavior.",
            "reasons": [
                "Chemistry is central to many industries",
                "Essential for understanding life processes"
            ],
            "resources": self.verified_resources["chemistry"]
        }
    
    def _solve_biology_question(self, question: str) -> Dict[str, Any]:
        """Solve biology questions"""
        question_lower = question.lower()
        
        # Cell structure
        if "cell" in question_lower or "mitochondria" in question_lower or "nucleus" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify the cell structure or process involved",
                    "Step 2: Understand its function in the cell",
                    "Step 3: Connect to cellular processes and energy flow"
                ],
                "explanation": [
                    "The cell is the basic unit of life.",
                    "Different organelles have specific functions: nucleus (DNA), mitochondria (energy), ribosomes (protein synthesis), etc."
                ],
                "final_answer": "Cell structures work together for life processes",
                "method": "Cell Biology Analysis",
                "why_this_works": "Cells are organized systems where each part contributes to survival and function.",
                    "how_it_is_possible": "Through evolution, cells developed specialized structures for different functions.",
                    "reasons": [
                        "All living things are made of cells",
                        "Cell theory is fundamental to biology",
                        "Understanding cells is key to medicine"
                    ],
                    "resources": self.verified_resources["biology"]
                }
        
        # DNA/Genetics
        elif "dna" in question_lower or "genetics" in question_lower or "gene" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify the genetic concept or problem",
                    "Step 2: Apply principles of inheritance",
                    "Step 3: Consider Mendel's laws or molecular genetics"
                ],
                "explanation": [
                    "DNA carries genetic information in genes.",
                    "Genes are passed from parents to offspring following specific patterns."
                ],
                "final_answer": "Genetic information determines traits",
                "method": "Genetic Analysis",
                "why_this_works": "DNA sequence determines protein synthesis, which determines traits. Inheritance follows predictable patterns.",
                "how_it_is_possible": "Through replication, transcription, and translation, genetic information is expressed.",
                "reasons": [
                    "Explains inheritance and variation",
                    "Basis for genetic diseases",
                    "Important for biotechnology"
                ],
                "resources": self.verified_resources["biology"]
            }
        
        # Photosynthesis
        elif "photosynthesis" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify inputs: CO₂ + H₂O + Light → Output",
                    "Step 2: Light reactions: Chlorophyll absorbs light energy",
                    "Step 3: Dark reactions (Calvin cycle): CO₂ is fixed into glucose",
                    "Step 4: Overall: 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂"
                ],
                "explanation": [
                    "Photosynthesis converts light energy into chemical energy (glucose).",
                    "It occurs in chloroplasts using chlorophyll to capture light."
                ],
                "final_answer": "Produces glucose and oxygen from carbon dioxide and water",
                "method": "Photosynthesis Analysis",
                "why_this_works": "Plants convert solar energy into chemical energy through a series of enzyme-catalyzed reactions.",
                "how_it_is_possible": "Chlorophyll absorbs light photons, exciting electrons that drive the synthesis of ATP and NADPH.",
                "reasons": [
                    "Basis of food chains",
                    "Produces oxygen we breathe",
                    "Important for climate regulation"
                ],
                "resources": self.verified_resources["biology"]
            }
        
        # Respiration
        elif "respiration" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify type: Aerobic (with O₂) or Anaerobic (without O₂)",
                    "Step 2: Aerobic: C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + ATP",
                    "Step 3: Occurs in mitochondria",
                    "Step 4: Produces 36-38 ATP per glucose"
                ],
                "explanation": [
                    "Cellular respiration releases energy from glucose.",
                    "Aerobic respiration requires oxygen and produces more ATP."
                ],
                "final_answer": "Breaks down glucose to release energy (ATP)",
                "method": "Cellular Respiration Analysis",
                "why_this_works": "Glucose is oxidized, releasing electrons that power ATP synthesis through the electron transport chain.",
                "how_it_is_possible": "A series of metabolic reactions (glycolysis, Krebs cycle, ETC) extract energy step by step.",
                "reasons": [
                    "Provides energy for cells",
                    "Essential for life",
                    "Opposite of photosynthesis"
                ],
                "resources": self.verified_resources["biology"]
            }
        
        # Ecosystem
        elif "ecosystem" in question_lower or "food chain" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify components: producers, consumers, decomposers",
                    "Step 2: Trace energy flow from sun → producers → consumers",
                    "Step 3: Each level loses energy as heat (10% rule)"
                ],
                "explanation": [
                    "Ecosystems include living (biotic) and non-living (abiotic) components.",
                    "Energy flows through food chains, but matter is recycled."
                ],
                "final_answer": "Energy flows, matter cycles in ecosystems",
                "method": "Ecosystem Analysis",
                "why_this_works": "Producers capture solar energy, consumers transfer it, decomposers recycle nutrients.",
                "how_it_is_possible": "Through photosynthesis, biogeochemical cycles, and food webs.",
                "reasons": [
                    "Maintains balance in nature",
                    "Important for conservation",
                    "Explains environmental relationships"
                ],
                "resources": self.verified_resources["biology"]
            }
        
        return {
            "solution": ["This is a biology question."],
            "explanation": ["Biology studies living organisms and their processes."],
            "final_answer": "Please provide more specific details.",
            "method": "Biology Problem Solving",
            "why_this_works": "Biological systems follow physical and chemical principles.",
            "how_it_is_possible": "Through evolution, life has developed remarkable mechanisms.",
            "reasons": [
                "Biology explains life at all levels",
                "Essential for medicine and environment"
            ],
            "resources": self.verified_resources["biology"]
        }
    
    def _general_science_solution(self, question: str, science_type: str) -> Dict[str, Any]:
        """General science solution"""
        return {
            "solution": ["This is a science problem."],
            "explanation": ["Science follows the scientific method."],
            "final_answer": "Please provide specific details for a precise answer.",
            "method": "Scientific Analysis",
            "why_this_works": "Science is based on observation, hypothesis, experimentation, and theory.",
            "how_it_is_possible": "Through systematic inquiry and evidence-based reasoning.",
            "reasons": [
                "Science advances our understanding",
                "Drives technological progress"
            ],
            "resources": self.verified_resources.get(science_type, self.verified_resources["biology"])
        }
    
    def solve_social_science_question(self, question: str) -> Dict[str, Any]:
        """Solve social science questions"""
        question_lower = question.lower()
        
        # History questions
        if "history" in question_lower or "when" in question_lower or "year" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify the historical event or period mentioned",
                    "Step 2: Research the timeline and context",
                    "Step 3: Connect to causes and consequences"
                ],
                "explanation": [
                    "History studies past events to understand present and future.",
                    "Historical events are connected through cause-effect relationships."
                ],
                "final_answer": "Historical analysis provides context and lessons",
                "method": "Historical Analysis",
                "why_this_works": "History follows documented evidence and scholarly interpretation.",
                "how_it_is_possible": "Through primary sources, archaeology, and historical records.",
                "reasons": [
                    "Helps us learn from past",
                    "Explains current situations",
                    "Preserves cultural memory"
                ],
                "resources": self.verified_resources["social_science"]
            }
        
        # Geography
        elif "geography" in question_lower or "country" in question_lower or "capital" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify the location or geographic feature",
                    "Step 2: Consider physical and human geography",
                    "Step 3: Analyze relationships between environment and society"
                ],
                "explanation": [
                    "Geography studies the Earth surface and human activities.",
                    "It includes physical features, climate, and human settlement patterns."
                ],
                "final_answer": "Geographic factors influence human activities",
                "method": "Geographic Analysis",
                "why_this_works": "Physical geography shapes where and how humans live.",
                "how_it_is_possible": "Through mapping, remote sensing, and spatial analysis.",
                "reasons": [
                    "Important for planning",
                    "Helps understand cultures",
                    "Essential for environmental management"
                ],
                "resources": self.verified_resources["social_science"]
            }
        
        return {
            "solution": ["This is a social science question."],
            "explanation": ["Social sciences study human society and relationships."],
            "final_answer": "Please provide specific details.",
            "method": "Social Science Analysis",
            "why_this_works": "Social sciences apply scientific methods to human behavior.",
            "how_it_is_possible": "Through observation, surveys, experiments, and case studies.",
            "reasons": [
                "Helps understand society",
                "Informs policy decisions"
            ],
            "resources": self.verified_resources["social_science"]
        }
    
    def solve_economics_question(self, question: str) -> Dict[str, Any]:
        """Solve economics questions"""
        question_lower = question.lower()
        numbers = self._extract_numbers(question)
        
        # Demand and Supply
        if "demand" in question_lower or "supply" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify the economic concept (demand/supply)",
                    "Step 2: Analyze factors affecting demand/supply",
                    "Step 3: Consider equilibrium and market forces"
                ],
                "explanation": [
                    "Demand is the willingness and ability to buy at various prices.",
                    "Supply is the willingness to sell at various prices.",
                    "Market equilibrium occurs where demand equals supply."
                ],
                "final_answer": "Price is determined by interaction of demand and supply",
                "method": "Demand-Supply Analysis",
                "why_this_works": "Buyers and sellers interact in markets to determine prices and quantities.",
                "how_it_is_possible": "Law of demand (inverse relationship) and law of supply (direct relationship).",
                "reasons": [
                    "Foundation of microeconomics",
                    "Explains price formation",
                    "Helps predict market behavior"
                ],
                "resources": self.verified_resources["economics"]
            }
        
        # GDP
        elif "gdp" in question_lower or "gdp" in question:
            return {
                "solution": [
                    "Step 1: GDP = C + I + G + (X-M)",
                    "Step 2: C = Consumer spending",
                    "Step 3: I = Investment",
                    "Step 4: G = Government spending",
                    "Step 5: X-M = Exports minus Imports"
                ],
                "explanation": [
                    "GDP (Gross Domestic Product) measures total economic output.",
                    "It represents the market value of all final goods and services produced."
                ],
                "final_answer": "GDP measures economic size and health",
                "method": "GDP Calculation",
                "why_this_works": "GDP captures all economic activity within a country's borders.",
                "how_it_is_possible": "By summing all expenditures or all incomes in an economy.",
                "reasons": [
                    "Standard measure of economic health",
                    "Used for international comparisons",
                    "Guides policy decisions"
                ],
                "resources": self.verified_resources["economics"]
            }
        
        # Inflation
        elif "inflation" in question_lower:
            return {
                "solution": [
                    "Step 1: Inflation = (Current Price Index - Base Price Index) / Base × 100",
                    "Step 2: Common measures: CPI, GDP deflator",
                    "Step 3: Effects: purchasing power decreases"
                ],
                "explanation": [
                    "Inflation is the rate at which prices rise over time.",
                    "It reduces the purchasing power of money."
                ],
                "final_answer": "Inflation measures price level changes",
                "method": "Inflation Calculation",
                "why_this_works": "When money supply grows faster than output, prices rise.",
                "how_it_is_possible": "Through too much money chasing too few goods.",
                "reasons": [
                    "Affects interest rates",
                    "Impacts savings and investments",
                    "Important for monetary policy"
                ],
                "resources": self.verified_resources["economics"]
            }
        
        return {
            "solution": ["This is an economics question."],
            "explanation": ["Economics studies how societies allocate scarce resources."],
            "final_answer": "Please provide specific details.",
            "method": "Economic Analysis",
            "why_this_works": "Economics applies theories to understand resource allocation.",
            "how_it_is_possible": "Through models, data analysis, and policy evaluation.",
            "reasons": [
                "Essential for business decisions",
                "Informs government policy",
                "Helps understand markets"
            ],
            "resources": self.verified_resources["economics"]
        }
    
    def solve_health_question(self, question: str) -> Dict[str, Any]:
        """Solve health and medical questions"""
        question_lower = question.lower()
        
        # Nutrition
        if "nutrition" in question_lower or "diet" in question_lower or "food" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify the nutritional component or diet question",
                    "Step 2: Consider macronutrients (carbs, proteins, fats)",
                    "Step 3: Consider micronutrients (vitamins, minerals)",
                    "Step 4: Apply balanced diet principles"
                ],
                "explanation": [
                    "A balanced diet includes carbohydrates, proteins, fats, vitamins, minerals, and water.",
                    "Each nutrient has specific functions in the body."
                ],
                "final_answer": "Balanced nutrition is essential for health",
                "method": "Nutritional Analysis",
                "why_this_works": "Different nutrients provide energy and building blocks for body functions.",
                "how_it_is_possible": "Through digestion, nutrients are absorbed and used by cells.",
                "reasons": [
                    "Prevents deficiency diseases",
                    "Supports immune system",
                    "Maintains healthy weight"
                ],
                "resources": self.verified_resources["health"]
            }
        
        # Disease
        elif "disease" in question_lower or "diabetes" in question_lower or "cancer" in question_lower or "heart" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify the disease type and symptoms",
                    "Step 2: Understand causes (genetic, environmental, lifestyle)",
                    "Step 3: Consider prevention and treatment options"
                ],
                "explanation": [
                    "Diseases can be infectious (caused by pathogens) or non-communicable (chronic).",
                    "Many diseases are influenced by lifestyle factors."
                ],
                "final_answer": "Disease understanding helps in prevention and treatment",
                "method": "Medical Analysis",
                "why_this_works": "Diseases have specific causes and pathological mechanisms.",
                "how_it_is_possible": "Through medical research and clinical studies.",
                "reasons": [
                    "Important for public health",
                    "Guides treatment decisions",
                    "Helps in prevention"
                ],
                "resources": self.verified_resources["health"]
            }
        
        # Mental health
        elif "mental" in question_lower or "stress" in question_lower or "anxiety" in question_lower or "depression" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify the mental health concern",
                    "Step 2: Consider contributing factors",
                    "Step 3: Suggest coping strategies and professional help"
                ],
                "explanation": [
                    "Mental health affects thinking, feeling, and behavior.",
                    "It involves emotional, psychological, and social well-being."
                ],
                "final_answer": "Mental health is as important as physical health",
                "method": "Mental Health Analysis",
                "why_this_works": "Mental health involves complex interactions of brain chemistry, genetics, and environment.",
                "how_it_is_possible": "Through therapy, medication, lifestyle changes, and support systems.",
                "reasons": [
                    "Affects quality of life",
                    "Connected to physical health",
                    "Important for productivity"
                ],
                "resources": self.verified_resources["health"]
            }
        
        return {
            "solution": ["This is a health-related question."],
            "explanation": ["Health involves physical, mental, and social well-being."],
            "final_answer": "Please provide specific details.",
            "method": "Health Analysis",
            "why_this_works": "Health science applies biology, medicine, and public health principles.",
            "how_it_is_possible": "Through research, prevention, and treatment.",
            "reasons": [
                "Fundamental to well-being",
                "Reduces disease burden",
                "Improves quality of life"
            ],
            "resources": self.verified_resources["health"]
        }
    
    def solve_computer_science_question(self, question: str) -> Dict[str, Any]:
        """Solve computer science questions"""
        question_lower = question.lower()
        
        # Programming
        if any(lang in question_lower for lang in ["python", "java", "javascript", "c++", "coding", "program", "code"]):
            return {
                "solution": [
                    "Step 1: Identify the programming concept or problem",
                    "Step 2: Break down the problem into steps",
                    "Step 3: Write pseudocode or algorithm",
                    "Step 4: Implement in chosen language"
                ],
                "explanation": [
                    "Programming involves writing instructions that computers execute.",
                    "Key concepts: variables, data types, control structures, functions."
                ],
                "final_answer": "Programming translates logic into executable code",
                "method": "Programming Problem Solving",
                "why_this_works": "Computers follow instructions exactly as given.",
                "how_it_is_possible": "Through syntax (grammar) and semantics (meaning) of programming languages.",
                "reasons": [
                    "Essential for software development",
                    "Automates tasks",
                    "Powers modern technology"
                ],
                "resources": self.verified_resources["computer_science"]
            }
        
        # Algorithms
        elif "algorithm" in question_lower or "sort" in question_lower or "search" in question_lower:
            return {
                "solution": [
                    "Step 1: Understand the problem requirements",
                    "Step 2: Choose appropriate algorithm",
                    "Step 3: Analyze time and space complexity",
                    "Step 4: Implement and test"
                ],
                "explanation": [
                    "Algorithms are step-by-step procedures for solving problems.",
                    "Important: Time complexity (Big O) and space complexity."
                ],
                "final_answer": "Algorithm efficiency determines program performance",
                "method": "Algorithm Analysis",
                "why_this_works": "Different algorithms have different efficiencies for the same task.",
                "how_it_is_possible": "Through mathematical analysis of operations and memory usage.",
                "reasons": [
                    "Optimizes performance",
                    "Fundamental to computer science",
                    "Used in all software"
                ],
                "resources": self.verified_resources["computer_science"]
            }
        
        # Database
        elif "database" in question_lower or "sql" in question_lower or "query" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify data requirements",
                    "Step 2: Design database schema (tables, relationships)",
                    "Step 3: Write SQL queries for CRUD operations",
                    "Step 4: Consider indexing for performance"
                ],
                "explanation": [
                    "Databases store and organize data for efficient retrieval.",
                    "SQL (Structured Query Language) is used to manage relational databases."
                ],
                "final_answer": "Databases enable efficient data management",
                "method": "Database Design",
                "why_this_works": "Data is organized in tables with relationships between them.",
                "how_it_is_possible": "Through normalization, indexing, and query optimization.",
                "reasons": [
                    "Essential for data-driven apps",
                    "Enables data integrity",
                    "Used in all enterprises"
                ],
                "resources": self.verified_resources["computer_science"]
            }
        
        # Networks
        elif "network" in question_lower or "internet" in question_lower or "protocol" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify network components and protocols",
                    "Step 2: Understand OSI or TCP/IP model layers",
                    "Step 3: Consider data transmission methods"
                ],
                "explanation": [
                    "Computer networks enable communication between devices.",
                    "Protocols define rules for data transmission (TCP/IP, HTTP, etc.)."
                ],
                "final_answer": "Networks connect devices for communication and data exchange",
                "method": "Network Analysis",
                "why_this_works": "Devices communicate through standardized protocols and physical connections.",
                "how_it_is_possible": "Through layers of abstraction in network models.",
                "reasons": [
                    "Foundation of the internet",
                    "Enables global communication",
                    "Essential for modern apps"
                ],
                "resources": self.verified_resources["computer_science"]
            }
        
        # AI/ML
        elif "machine learning" in question_lower or "ai" in question_lower or "artificial intelligence" in question_lower or "deep learning" in question_lower:
            return {
                "solution": [
                    "Step 1: Identify the AI/ML problem type (classification, regression, etc.)",
                    "Step 2: Prepare and preprocess data",
                    "Step 3: Choose and train model",
                    "Step 4: Evaluate and optimize"
                ],
                "explanation": [
                    "AI enables computers to learn from data and make decisions.",
                    "Machine learning is a subset of AI that learns patterns from data."
                ],
                "final_answer": "AI/ML enables intelligent automation and predictions",
                "method": "AI/ML Problem Solving",
                "why_this_works": "Algorithms learn patterns from data to make predictions or decisions.",
                "how_it_is_possible": "Through statistical models, neural networks, and optimization.",
                "reasons": [
                    "Powers modern applications",
                    "Automates complex tasks",
                    "Driving technological innovation"
                ],
                "resources": self.verified_resources["computer_science"]
            }
        
        return {
            "solution": ["This is a computer science question."],
            "explanation": ["Computer science studies computation, algorithms, and information processing."],
            "final_answer": "Please provide specific details.",
            "method": "CS Problem Solving",
            "why_this_works": "CS applies mathematical and engineering principles to computing.",
            "how_it_is_possible": "Through hardware, software, and theoretical foundations.",
            "reasons": [
                "Drives technological progress",
                "Essential for digital transformation"
            ],
            "resources": self.verified_resources["computer_science"]
        }
    
    def solve_question(self, question: str) -> Dict[str, Any]:
        """
        Main entry point to solve any question
        Returns comprehensive solution with explanation and resources
        """
        # Detect subject
        subject, confidence = self.detect_subject(question)
        
        logger.info(f"Detected subject: {subject} (confidence: {confidence})")
        
        # Route to appropriate solver
        if subject == "mathematics":
            result = self.solve_math_question(question)
        elif subject == "physics":
            result = self.solve_science_question(question, "physics")
        elif subject == "chemistry":
            result = self.solve_science_question(question, "chemistry")
        elif subject == "biology":
            result = self.solve_science_question(question, "biology")
        elif subject == "social_science":
            result = self.solve_social_science_question(question)
        elif subject == "economics":
            result = self.solve_economics_question(question)
        elif subject == "health":
            result = self.solve_health_question(question)
        elif subject == "computer_science":
            result = self.solve_computer_science_question(question)
        else:
            result = self._general_solution(question)
        
        # Add subject information
        result["detected_subject"] = subject
        result["confidence"] = confidence
        
        # Store resources for reference
        self.last_resources = result.get("resources", [])
        
        return result
    
    def _general_solution(self, question: str) -> Dict[str, Any]:
        """General solution for unclassified questions"""
        return {
            "solution": [
                "This appears to be a general knowledge or specialized question.",
                "I'll provide information based on verified sources."
            ],
            "explanation": [
                "Many questions require analysis from multiple perspectives.",
                "The answer depends on the specific context and field."
            ],
            "final_answer": "Please provide more details for a specific answer.",
            "method": "General Analysis",
            "why_this_works": "Different subjects have different methodologies and frameworks.",
            "how_it_is_possible": "Through interdisciplinary approaches and evidence-based reasoning.",
            "reasons": [
                "Knowledge is interconnected",
                "Context matters for answers"
            ],
            "resources": []
        }
    
    def format_response(self, result: Dict[str, Any]) -> str:
        """
        Format the solution into a readable response
        """
        if not result:
            return "I couldn't analyze this question properly. Please provide more details."
        
        # Build response
        response = []
        
        # Subject detected
        if "detected_subject" in result:
            response.append(f"📚 **Subject: {result['detected_subject'].replace('_', ' ').title()}**\n")
        
        # Solution steps
        if "solution" in result and result["solution"]:
            response.append("### 📝 Solution Steps:")
            for step in result["solution"]:
                response.append(f"• {step}")
            response.append("")
        
        # Explanation
        if "explanation" in result and result["explanation"]:
            response.append("### 💡 Explanation:")
            for exp in result["explanation"]:
                response.append(f"• {exp}")
            response.append("")
        
        # Final answer
        if "final_answer" in result and result["final_answer"]:
            response.append(f"### ✅ Final Answer:\n**{result['final_answer']}**\n")
        
        # Method
        if "method" in result and result["method"]:
            response.append(f"### 🔧 Method: {result['method']}")
        
        # Why this works
        if "why_this_works" in result and result["why_this_works"]:
            response.append(f"\n### 🤔 Why This Works:\n{result['why_this_works']}")
        
        # How it's possible
        if "how_it_is_possible" in result and result["how_it_is_possible"]:
            response.append(f"\n### 🔬 How It's Possible:\n{result['how_it_is_possible']}")
        
        # Reasons behind
        if "reasons" in result and result["reasons"]:
            response.append("\n### 📋 Reasons Behind:")
            for reason in result["reasons"]:
                response.append(f"• {reason}")
        
        # Verified resources
        if "resources" in result and result["resources"]:
            response.append("\n### 📚 Verified Resources:")
            for resource in result["resources"][:4]:  # Limit to 4 resources
                response.append(f"• [{resource['name']}]({resource['url']}): {resource['description']}")
        
        return "\n".join(response)
    
    def get_verified_resources(self, subject: str) -> List[Dict[str, str]]:
        """Get verified resources for a specific subject"""
        return self.verified_resources.get(subject, [])


# Create singleton instance
subject_solver = SubjectSolver()


# Export for use in other modules
__all__ = ['subject_solver', 'SubjectSolver']
