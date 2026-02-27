"""
Chat&Talk GPT - Sentiment Analysis Module
Analyze sentiment and emotions from text
Supports multiple languages and emotion detection
"""
import os
import json
import logging
import re
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger("SentimentAnalyzer")

# Try to import NLP libraries
TEXTBLOB_AVAILABLE = False
VADER_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
    logger.info("TextBlob is available")
except ImportError:
    logger.warning("TextBlob not available")

try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
    logger.info("NLTK VADER is available")
except ImportError:
    logger.warning("NLTK VADER not available")

# Emotion keywords for rule-based analysis
EMOTION_KEYWORDS = {
    "joy": ["happy", "joy", "excited", "love", "amazing", "wonderful", "great", "fantastic", "delighted", "pleased"],
    "sadness": ["sad", "unhappy", "depressed", "down", "miserable", "upset", "disappointed", "sorrow", "grief"],
    "anger": ["angry", "mad", "furious", "annoyed", "irritated", "frustrated", "outraged", "hate"],
    "fear": ["afraid", "scared", "fear", "terrified", "worried", "anxious", "nervous", "panic"],
    "surprise": ["surprised", "amazed", "astonished", "shocked", "unexpected", "wow", "incredible"],
    "anticipation": ["expect", "hope", "looking forward", "eager", "excited", "waiting", "soon"],
    "trust": ["trust", "believe", "confident", "rely", "sure", "certain", "definitely"],
    "disgust": ["disgusting", "gross", "nasty", "awful", "terrible", "horrible", "repulsive"]
}


class SentimentAnalyzer:
    """
    Sentiment Analyzer for text emotion detection
    
    Features:
    - Multi-language sentiment analysis
    - Emotion detection
    - Sentiment scoring (positive, negative, neutral)
    - Text preprocessing
    - Batch analysis
    - Sentiment trends
    """
    
    def __init__(self):
        """Initialize Sentiment Analyzer"""
        self.analysis_history = []
        
        # Initialize VADER if available
        if VADER_AVAILABLE:
            try:
                nltk.download('vader_lexicon', quiet=True)
                self.vader = SentimentIntensityAnalyzer()
            except Exception as e:
                logger.warning(f"Failed to initialize VADER: {e}")
        
        logger.info("Sentiment Analyzer initialized")
    
    def analyze(
        self,
        text: str,
        language: str = "en",
        return_details: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            language: Language code
            return_details: Return detailed emotions
            
        Returns:
            Sentiment analysis results
        """
        try:
            if not text or len(text.strip()) == 0:
                return {
                    "success": False,
                    "error": "Empty text provided"
                }
            
            # Determine which method to use
            result = {}
            
            # Try VADER first (best for social media)
            if VADER_AVAILABLE:
                result = self._analyze_vader(text)
            
            # Fallback to TextBlob
            if not result and TEXTBLOB_AVAILABLE:
                result = self._analyze_textblob(text)
            
            # Fallback to rule-based
            if not result:
                result = self._analyze_rule_based(text)
            
            # Add emotions if requested
            if return_details:
                result["emotions"] = self._detect_emotions(text)
            
            # Add to history
            self.analysis_history.append({
                "text": text[:100],  # Store first 100 chars
                "sentiment": result.get("sentiment"),
                "score": result.get("score"),
                "timestamp": datetime.now().isoformat()
            })
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_vader(self, text: str) -> Dict[str, Any]:
        """Analyze using VADER"""
        try:
            scores = self.vader.polarity_scores(text)
            
            compound = scores["compound"]
            
            if compound >= 0.05:
                sentiment = "positive"
            elif compound <= -0.05:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "method": "vader",
                "sentiment": sentiment,
                "score": compound,
                "details": {
                    "positive": scores["pos"],
                    "negative": scores["neg"],
                    "neutral": scores["neu"]
                }
            }
            
        except Exception as e:
            logger.error(f"VADER error: {e}")
            return {}
    
    def _analyze_textblob(self, text: str) -> Dict[str, Any]:
        """Analyze using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "method": "textblob",
                "sentiment": sentiment,
                "score": polarity,
                "details": {
                    "polarity": polarity,
                    "subjectivity": subjectivity
                }
            }
            
        except Exception as e:
            logger.error(f"TextBlob error: {e}")
            return {}
    
    def _analyze_rule_based(self, text: str) -> Dict[str, Any]:
        """Rule-based sentiment analysis"""
        try:
            text_lower = text.lower()
            words = text_lower.split()
            
            positive_count = 0
            negative_count = 0
            
            # Simple word matching
            positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "best", "happy", "joy", "beautiful", "awesome", "nice", "perfect"]
            negative_words = ["bad", "terrible", "awful", "horrible", "worst", "hate", "sad", "angry", "disappointed", "poor", "fail", "wrong", "ugly", "boring"]
            
            for word in words:
                if word in positive_words:
                    positive_count += 1
                if word in negative_words:
                    negative_count += 1
            
            total = positive_count + negative_count
            if total == 0:
                score = 0
            else:
                score = (positive_count - negative_count) / total
            
            if score > 0.1:
                sentiment = "positive"
            elif score < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "method": "rule_based",
                "sentiment": sentiment,
                "score": score,
                "details": {
                    "positive_words": positive_count,
                    "negative_words": negative_count
                }
            }
            
        except Exception as e:
            logger.error(f"Rule-based error: {e}")
            return {}
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions in text"""
        text_lower = text.lower()
        emotions = {}
        
        for emotion, keywords in EMOTION_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            if score > 0:
                # Normalize score
                emotions[emotion] = min(score / len(keywords), 1.0)
        
        return emotions
    
    def analyze_batch(
        self,
        texts: List[str],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Analyze multiple texts
        
        Args:
            texts: List of texts to analyze
            language: Language code
            
        Returns:
            Batch analysis results
        """
        results = {
            "success": True,
            "total": len(texts),
            "sentiments": {
                "positive": 0,
                "negative": 0,
                "neutral": 0
            },
            "average_score": 0,
            "results": []
        }
        
        total_score = 0
        
        for text in texts:
            analysis = self.analyze(text, language)
            
            if analysis.get("success"):
                sentiment = analysis.get("sentiment", "neutral")
                results["sentiments"][sentiment] += 1
                total_score += analysis.get("score", 0)
                results["results"].append(analysis)
        
        if len(texts) > 0:
            results["average_score"] = total_score / len(texts)
        
        return results
    
    def get_sentiment_trend(self, days: int = 7) -> Dict[str, Any]:
        """
        Get sentiment trend over time
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Trend data
        """
        # Get recent analyses
        recent = self.analysis_history[-100:]  # Last 100 analyses
        
        if not recent:
            return {
                "success": False,
                "error": "No analysis history available"
            }
        
        positive = sum(1 for r in recent if r.get("sentiment") == "positive")
        negative = sum(1 for r in recent if r.get("sentiment") == "negative")
        neutral = sum(1 for r in recent if r.get("sentiment") == "neutral")
        total = len(recent)
        
        return {
            "success": True,
            "total_analyses": total,
            "distribution": {
                "positive": positive / total if total > 0 else 0,
                "negative": negative / total if total > 0 else 0,
                "neutral": neutral / total if total > 0 else 0
            },
            "counts": {
                "positive": positive,
                "negative": negative,
                "neutral": neutral
            }
        }
    
    def get_text_summary(self, text: str) -> Dict[str, Any]:
        """
        Get a quick summary of text sentiment
        
        Args:
            text: Text to summarize
            
        Returns:
            Summary dictionary
        """
        analysis = self.analyze(text)
        
        return {
            "sentiment": analysis.get("sentiment", "unknown"),
            "intensity": abs(analysis.get("score", 0)),
            "emotions": analysis.get("emotions", {}),
            "is_positive": analysis.get("sentiment") == "positive",
            "is_negative": analysis.get("sentiment") == "negative",
            "is_neutral": analysis.get("sentiment") == "neutral"
        }


# Singleton instance
sentiment_analyzer = SentimentAnalyzer()


# Standalone functions
def analyze_sentiment(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to analyze sentiment"""
    return sentiment_analyzer.analyze(*args, **kwargs)


def analyze_batch(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function for batch analysis"""
    return sentiment_analyzer.analyze_batch(*args, **kwargs)
