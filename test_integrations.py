"""
Chat&Talk GPT - Integration Test Script
Tests all new tool integrations to ensure they work correctly.
"""
import sys
import os
import asyncio
import json
from pathlib import Path
import inspect

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "total": 0
}

def log_test(test_name: str, passed: bool, message: str = ""):
    """Log test results"""
    test_results["total"] += 1
    if passed:
        test_results["passed"].append(test_name)
        print(f"[PASS] {test_name}")
    else:
        test_results["failed"].append(f"{test_name}: {message}")
        print(f"[FAIL] {test_name} - {message}")

def test_module_imports():
    """Test that all modules can be imported without errors"""
    print("\n" + "="*60)
    print("TESTING MODULE IMPORTS")
    print("="*60)
    
    modules_to_test = [
        ("translator", "TranslatorManager"),
        ("calendar_manager", "CalendarManager"),
        ("code_executor", "CodeExecutor"),
        ("flashcards", "FlashcardManager"),
        ("news_manager", "NewsManager"),
        ("calculator", "CalculatorManager"),
        ("dictionary_manager", "DictionaryManager"),
        ("recipe_manager", "RecipeManager"),
        ("currency_converter", "CurrencyConverter"),
    ]
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            log_test(f"Import {module_name}.{class_name}", True)
        except Exception as e:
            log_test(f"Import {module_name}.{class_name}", False, str(e))

def test_tools_manager_import():
    """Test that tools_manager can be imported"""
    print("\n" + "="*60)
    print("TESTING TOOLS MANAGER IMPORT")
    print("="*60)
    
    try:
        from tools import ToolsManager
        log_test("Import ToolsManager from tools", True)
        
        # Test instantiation
        tools_mgr = ToolsManager()
        log_test("Instantiate ToolsManager", True)
        
        return tools_mgr
    except Exception as e:
        log_test("Import ToolsManager from tools", False, str(e))
        return None

def test_translator_module(tools_mgr):
    """Test translator module functionality"""
    print("\n" + "="*60)
    print("TESTING TRANSLATOR MODULE")
    print("="*60)
    
    try:
        from translator import TranslatorManager, SUPPORTED_LANGUAGES
        
        # Test class instantiation
        translator = TranslatorManager()
        log_test("TranslatorManager instantiation", True)
        
        # Test supported languages constant exists
        assert len(SUPPORTED_LANGUAGES) > 0, "No supported languages"
        log_test("SUPPORTED_LANGUAGES constant loaded", True)
        
        # Test get_supported_languages method
        langs = translator.get_supported_languages()
        assert len(langs) > 0, "get_supported_languages returned empty"
        log_test("get_supported_languages works", True)
        
        # Test detect_language method exists
        assert hasattr(translator, 'detect_language'), "Missing detect_language method"
        log_test("detect_language method exists", True)
        
        # Test translate method is async
        assert asyncio.iscoroutinefunction(translator.translate), "translate should be async"
        log_test("translate is async", True)
        
        # Test ToolsManager integration
        if tools_mgr:
            assert hasattr(tools_mgr, 'translate'), "ToolsManager missing translate method"
            log_test("ToolsManager.translate method exists", True)
            
            assert hasattr(tools_mgr, 'get_supported_languages'), "ToolsManager missing get_supported_languages"
            log_test("ToolsManager.get_supported_languages method exists", True)
            
            assert hasattr(tools_mgr, 'detect_language'), "ToolsManager missing detect_language"
            log_test("ToolsManager.detect_language method exists", True)
        
    except Exception as e:
        log_test("Translator module tests", False, str(e))

def test_calendar_module(tools_mgr):
    """Test calendar module functionality"""
    print("\n" + "="*60)
    print("TESTING CALENDAR MODULE")
    print("="*60)
    
    try:
        from calendar_manager import CalendarManager, EVENT_TYPES
        
        # Test class instantiation with test file
        test_file = "memory/test_calendar_events.json"
        calendar = CalendarManager(calendar_file=test_file)
        log_test("CalendarManager instantiation", True)
        
        # Test event types
        assert len(EVENT_TYPES) > 0, "No event types defined"
        log_test("EVENT_TYPES loaded", True)
        
        # Test add_event method - returns event dict directly
        result = calendar.add_event(
            title="Test Event",
            description="Test Description",
            event_type="general",
            date="2026-03-01",
            time="10:00"
        )
        # Result is the event dict directly, not wrapped in success/data
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "title" in result, "Result doesn't contain title"
        event_id = result.get("id")
        assert event_id is not None, "No event id returned"
        log_test("add_event works", True)
        
        # Test get_event_by_id method
        event = calendar.get_event_by_id(event_id)
        assert event is not None, "Failed to get event"
        assert event.get("title") == "Test Event", f"Wrong title: {event.get('title')}"
        log_test("get_event_by_id works", True)
        
        # Test get_events method
        events = calendar.get_events()
        assert len(events) > 0, "No events returned"
        log_test("get_events works", True)
        
        # Test mark_completed method
        result = calendar.mark_completed(event_id)
        assert result is not None, "Failed to mark event complete"
        log_test("mark_completed works", True)
        
        # Test delete_event method
        result = calendar.delete_event(event_id)
        assert result == True, "Failed to delete event"
        log_test("delete_event works", True)
        
        # Test ToolsManager integration
        if tools_mgr:
            assert hasattr(tools_mgr, 'add_calendar_event'), "ToolsManager missing add_calendar_event"
            log_test("ToolsManager.add_calendar_event method exists", True)
            
            assert hasattr(tools_mgr, 'get_calendar_events'), "ToolsManager missing get_calendar_events"
            log_test("ToolsManager.get_calendar_events method exists", True)
            
            assert hasattr(tools_mgr, 'delete_calendar_event'), "ToolsManager missing delete_calendar_event"
            log_test("ToolsManager.delete_calendar_event method exists", True)
        
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
        
    except Exception as e:
        log_test("Calendar module tests", False, str(e))

def test_code_executor_module(tools_mgr):
    """Test code executor module functionality"""
    print("\n" + "="*60)
    print("TESTING CODE EXECUTOR MODULE")
    print("="*60)
    
    try:
        from code_executor import CodeExecutor, LANGUAGE_MAP
        
        # Test class instantiation
        executor = CodeExecutor()
        log_test("CodeExecutor instantiation", True)
        
        # Test language mapping
        assert "python" in LANGUAGE_MAP, "Python not in language map"
        assert "javascript" in LANGUAGE_MAP, "JavaScript not in language map"
        log_test("LANGUAGE_MAP loaded", True)
        
        # Test get_supported_languages method
        langs = executor.get_supported_languages()
        assert len(langs) > 0, "No supported languages"
        log_test("get_supported_languages works", True)
        
        # Test execute method exists
        assert hasattr(executor, 'execute'), "Missing execute method"
        log_test("execute method exists", True)
        
        # Test ToolsManager integration
        if tools_mgr:
            assert hasattr(tools_mgr, 'execute_code'), "ToolsManager missing execute_code"
            log_test("ToolsManager.execute_code method exists", True)
            
            assert hasattr(tools_mgr, 'get_code_supported_languages'), "ToolsManager missing get_code_supported_languages"
            log_test("ToolsManager.get_code_supported_languages method exists", True)
        
    except Exception as e:
        log_test("Code executor module tests", False, str(e))

def test_flashcards_module(tools_mgr):
    """Test flashcards module functionality"""
    print("\n" + "="*60)
    print("TESTING FLASHCARDS MODULE")
    print("="*60)
    
    try:
        from flashcards import FlashcardManager, VALID_CATEGORIES
        
        # Test class instantiation with test file
        test_file = "memory/test_flashcards.json"
        flashcards = FlashcardManager(storage_path=test_file)
        log_test("FlashcardManager instantiation", True)
        
        # Test valid categories
        assert len(VALID_CATEGORIES) > 0, "No valid categories"
        log_test("VALID_CATEGORIES loaded", True)
        
        # Test create_deck method
        result = flashcards.create_deck(
            name="Test Deck",
            description="Test description",
            category="language"
        )
        # Result is a dict with 'success' and 'deck' keys
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "deck" in result or "id" in result, f"Result doesn't contain deck info: {result}"
        # Extract deck id from result
        if "deck" in result:
            deck_id = result.get("deck", {}).get("id")
        else:
            deck_id = result.get("id")
        assert deck_id is not None, f"No deck id returned: {result}"
        log_test("create_deck works", True)
        
        # Test add_card method
        result = flashcards.add_card(
            deck_id=deck_id,
            front="Hello",
            back="Namaste"
        )
        assert result.get("success") == True, f"Failed to add card: {result}"
        card_id = result.get("card", {}).get("id")
        log_test("add_card works", True)
        
        # Test get_deck method - returns dict with 'deck' key
        deck = flashcards.get_deck(deck_id)
        assert deck is not None, "Failed to get deck"
        # Deck may be nested under 'deck' key or at top level
        deck_name = deck.get("name") or deck.get("deck", {}).get("name")
        assert deck_name is not None, f"Deck name is None, full deck: {deck}"
        log_test("get_deck works", True)
        
        # Test get_all_decks method
        decks = flashcards.get_all_decks()
        assert len(decks) > 0, "No decks returned"
        log_test("get_all_decks works", True)
        
        # Test delete_card method
        result = flashcards.delete_card(deck_id, card_id)
        assert result == True, "Failed to delete card"
        log_test("delete_card works", True)
        
        # Test delete_deck method
        result = flashcards.delete_deck(deck_id)
        assert result == True, "Failed to delete deck"
        log_test("delete_deck works", True)
        
        # Test ToolsManager integration
        if tools_mgr:
            assert hasattr(tools_mgr, 'create_flashcard_deck'), "ToolsManager missing create_flashcard_deck"
            log_test("ToolsManager.create_flashcard_deck method exists", True)
            
            assert hasattr(tools_mgr, 'add_flashcard'), "ToolsManager missing add_flashcard"
            log_test("ToolsManager.add_flashcard method exists", True)
            
            assert hasattr(tools_mgr, 'get_flashcard_decks'), "ToolsManager missing get_flashcard_decks"
            log_test("ToolsManager.get_flashcard_decks method exists", True)
            
            assert hasattr(tools_mgr, 'study_flashcards'), "ToolsManager missing study_flashcards"
            log_test("ToolsManager.study_flashcards method exists", True)
        
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
        
    except Exception as e:
        log_test("Flashcards module tests", False, str(e))

def test_news_module(tools_mgr):
    """Test news module functionality"""
    print("\n" + "="*60)
    print("TESTING NEWS MODULE")
    print("="*60)
    
    try:
        from news_manager import NewsManager, VALID_CATEGORIES
        
        # Test class instantiation
        news_mgr = NewsManager()
        log_test("NewsManager instantiation", True)
        
        # Test valid categories
        assert len(VALID_CATEGORIES) > 0, "No valid categories"
        log_test("VALID_CATEGORIES loaded", True)
        
        # Test get_latest_news method exists
        assert hasattr(news_mgr, 'get_latest_news'), "NewsManager missing get_latest_news"
        log_test("NewsManager.get_latest_news method exists", True)
        
        # Test search_news method exists
        assert hasattr(news_mgr, 'search_news'), "NewsManager missing search_news"
        log_test("NewsManager.search_news method exists", True)
        
        # Test get_trending_topics method exists
        assert hasattr(news_mgr, 'get_trending_topics'), "NewsManager missing get_trending_topics"
        log_test("NewsManager.get_trending_topics method exists", True)
        
        # Test ToolsManager integration
        if tools_mgr:
            assert hasattr(tools_mgr, 'get_latest_news'), "ToolsManager missing get_latest_news"
            log_test("ToolsManager.get_latest_news method exists", True)
            
            assert hasattr(tools_mgr, 'search_news'), "ToolsManager missing search_news"
            log_test("ToolsManager.search_news method exists", True)
            
            assert hasattr(tools_mgr, 'get_trending_topics'), "ToolsManager missing get_trending_topics"
            log_test("ToolsManager.get_trending_topics method exists", True)
        
    except Exception as e:
        log_test("News module tests", False, str(e))

def test_calculator_module(tools_mgr):
    """Test calculator module functionality"""
    print("\n" + "="*60)
    print("TESTING CALENDAR MODULE")
    print("="*60)
    
    try:
        from calculator import CalculatorManager
        
        # Test class instantiation
        calc = CalculatorManager()
        log_test("CalculatorManager instantiation", True)
        
        # Test calculate method is async
        assert asyncio.iscoroutinefunction(calc.calculate), "calculate should be async"
        log_test("CalculatorManager.calculate is async", True)
        
        # Test calculate returns dict with success key
        async def test_calc():
            result = await calc.calculate("2 + 2")
            assert isinstance(result, dict), f"Expected dict, got {type(result)}"
            assert result.get("success") == True, f"Calculation failed: {result}"
            return result
        
        result = asyncio.run(test_calc())
        log_test("calculate works with basic expression", True)
        
        # Test convert_units is async
        assert asyncio.iscoroutinefunction(calc.convert_units), "convert_units should be async"
        log_test("CalculatorManager.convert_units is async", True)
        
        # Test solve_equation is async
        assert asyncio.iscoroutinefunction(calc.solve_equation), "solve_equation should be async"
        log_test("CalculatorManager.solve_equation is async", True)
        
        # Test ToolsManager integration
        if tools_mgr:
            assert hasattr(tools_mgr, 'calculate'), "ToolsManager missing calculate"
            log_test("ToolsManager.calculate method exists", True)
            
            assert hasattr(tools_mgr, 'solve_equation'), "ToolsManager missing solve_equation"
            log_test("ToolsManager.solve_equation method exists", True)
            
            assert hasattr(tools_mgr, 'convert_units'), "ToolsManager missing convert_units"
            log_test("ToolsManager.convert_units method exists", True)
            
            assert hasattr(tools_mgr, 'calculate_tip'), "ToolsManager missing calculate_tip"
            log_test("ToolsManager.calculate_tip method exists", True)
        
    except Exception as e:
        log_test("Calculator module tests", False, str(e))

def test_dictionary_module(tools_mgr):
    """Test dictionary module functionality"""
    print("\n" + "="*60)
    print("TESTING DICTIONARY MODULE")
    print("="*60)
    
    try:
        from dictionary_manager import DictionaryManager
        
        # Test class instantiation
        dict_mgr = DictionaryManager()
        log_test("DictionaryManager instantiation", True)
        
        # Test define method is async
        assert asyncio.iscoroutinefunction(dict_mgr.define), "define should be async"
        log_test("DictionaryManager.define is async", True)
        
        # Test ToolsManager integration
        if tools_mgr:
            assert hasattr(tools_mgr, 'define_word'), "ToolsManager missing define_word"
            log_test("ToolsManager.define_word method exists", True)
            
            assert hasattr(tools_mgr, 'get_synonyms'), "ToolsManager missing get_synonyms"
            log_test("ToolsManager.get_synonyms method exists", True)
            
            assert hasattr(tools_mgr, 'get_antonyms'), "ToolsManager missing get_antonyms"
            log_test("ToolsManager.get_antonyms method exists", True)
            
            assert hasattr(tools_mgr, 'get_word_info'), "ToolsManager missing get_word_info"
            log_test("ToolsManager.get_word_info method exists", True)
            
            assert hasattr(tools_mgr, 'search_words'), "ToolsManager missing search_words"
            log_test("ToolsManager.search_words method exists", True)
        
    except Exception as e:
        log_test("Dictionary module tests", False, str(e))

def test_recipe_module(tools_mgr):
    """Test recipe module functionality"""
    print("\n" + "="*60)
    print("TESTING RECIPE MODULE")
    print("="*60)
    
    try:
        from recipe_manager import RecipeManager
        
        # Test class instantiation
        recipe_mgr = RecipeManager()
        log_test("RecipeManager instantiation", True)
        
        # Test search_by_name is async
        assert asyncio.iscoroutinefunction(recipe_mgr.search_by_name), "search_by_name should be async"
        log_test("RecipeManager.search_by_name is async", True)
        
        # Test search_by_ingredient is async
        assert asyncio.iscoroutinefunction(recipe_mgr.search_by_ingredient), "search_by_ingredient should be async"
        log_test("RecipeManager.search_by_ingredient is async", True)
        
        # Test get_random_recipe is async
        assert asyncio.iscoroutinefunction(recipe_mgr.get_random_recipe), "get_random_recipe should be async"
        log_test("RecipeManager.get_random_recipe is async", True)
        
        # Test ToolsManager integration
        if tools_mgr:
            assert hasattr(tools_mgr, 'search_recipes'), "ToolsManager missing search_recipes"
            log_test("ToolsManager.search_recipes method exists", True)
            
            assert hasattr(tools_mgr, 'search_recipes_by_name'), "ToolsManager missing search_recipes_by_name"
            log_test("ToolsManager.search_recipes_by_name method exists", True)
            
            assert hasattr(tools_mgr, 'search_recipes_by_ingredient'), "ToolsManager missing search_recipes_by_ingredient"
            log_test("ToolsManager.search_recipes_by_ingredient method exists", True)
            
            assert hasattr(tools_mgr, 'get_random_recipe'), "ToolsManager missing get_random_recipe"
            log_test("ToolsManager.get_random_recipe method exists", True)
            
            assert hasattr(tools_mgr, 'get_recipe_details'), "ToolsManager missing get_recipe_details"
            log_test("ToolsManager.get_recipe_details method exists", True)
        
    except Exception as e:
        log_test("Recipe module tests", False, str(e))

def test_currency_converter_module(tools_mgr):
    """Test currency converter module functionality"""
    print("\n" + "="*60)
    print("TESTING CURRENCY CONVERTER MODULE")
    print("="*60)
    
    try:
        from currency_converter import CurrencyConverter, SUPPORTED_CURRENCIES
        
        # Test class instantiation
        converter = CurrencyConverter()
        log_test("CurrencyConverter instantiation", True)
        
        # Test SUPPORTED_CURRENCIES constant
        assert len(SUPPORTED_CURRENCIES) > 0, "No supported currencies"
        log_test("SUPPORTED_CURRENCIES constant loaded", True)
        
        # Test get_supported_currencies method
        currencies = converter.get_supported_currencies()
        assert len(currencies) > 0, "get_supported_currencies returned empty"
        log_test("get_supported_currencies works", True)
        
        # Test convert method returns dict
        result = converter.convert(100, "USD", "EUR")
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert result.get("success") == True, f"Conversion failed: {result}"
        log_test("convert works", True)
        
        # Test get_exchange_rate method
        rate = converter.get_exchange_rate("USD", "EUR")
        assert rate is not None, "get_exchange_rate returned None"
        log_test("get_exchange_rate works", True)
        
        # Test ToolsManager integration
        if tools_mgr:
            assert hasattr(tools_mgr, 'convert_currency'), "ToolsManager missing convert_currency"
            log_test("ToolsManager.convert_currency method exists", True)
            
            assert hasattr(tools_mgr, 'get_exchange_rates'), "ToolsManager missing get_exchange_rates"
            log_test("ToolsManager.get_exchange_rates method exists", True)
            
            assert hasattr(tools_mgr, 'get_supported_currencies'), "ToolsManager missing get_supported_currencies"
            log_test("ToolsManager.get_supported_currencies method exists", True)
        
    except Exception as e:
        log_test("Currency converter module tests", False, str(e))

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {len(test_results['passed'])}")
    print(f"Failed: {len(test_results['failed'])}")
    
    if test_results['failed']:
        print("\n" + "="*60)
        print("FAILED TESTS")
        print("="*60)
        for failure in test_results['failed']:
            print(f"  - {failure}")
        return False
    else:
        print("\n[SUCCESS] All tests passed!")
        return True

def main():
    """Main test function"""
    print("="*60)
    print("Chat&Talk GPT - Tool Integration Tests")
    print("="*60)
    
    # Test module imports
    test_module_imports()
    
    # Test tools manager import
    tools_mgr = test_tools_manager_import()
    
    # Test each module
    test_translator_module(tools_mgr)
    test_calendar_module(tools_mgr)
    test_code_executor_module(tools_mgr)
    test_flashcards_module(tools_mgr)
    test_news_module(tools_mgr)
    test_calculator_module(tools_mgr)
    test_dictionary_module(tools_mgr)
    test_recipe_module(tools_mgr)
    test_currency_converter_module(tools_mgr)
    
    # Print summary
    success = print_summary()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
