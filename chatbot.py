import re
import math
import random
from datetime import datetime
from difflib import SequenceMatcher

# ==========================================
# 1. ADVANCED LOGIC CORE CLASSES
# ==========================================

class ContextManager:
    """Keeps track of conversation history to handle follow-up questions and quiz states."""
    def __init__(self, max_history=3):
        self.history = []
        self.max_history = max_history
        self.current_state = "DEFAULT"
        self.extracted_entities = {}

    def update(self, intent_tag, entities=None):
        self.history.append({"intent": intent_tag, "entities": entities})
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # State Machine for Quiz
        if intent_tag == "QUIZ_ASK":
            self.current_state = "AWAITING_QUIZ_ANSWER"
        elif intent_tag in ["QUIZ_ANSWER", "DEFAULT", "FALLBACK"]:
            self.current_state = "DEFAULT"

    def get_last_intent(self):
        return self.history[-1]["intent"] if self.history else None

class EntityExtractor:
    """Extracts specific data types (math expressions) from text using Regex."""
    @staticmethod
    def extract_math(text):
        # Finds patterns like 10+5, 20 * 3, 100/4 (ignoring calc)
        match = re.search(r'(\d+[\s]*[\+\-\*\/\^][\s]*\d+)', text)
        return match.group(1).replace("^", "**") if match else None

class AdvancedChatbotEngine:
    def __init__(self):
        self.context = ContextManager()
        self.extractor = EntityExtractor()
        
        # Legacy Knowledge Base (Used for high-accuracy fuzzy matching)
        self.knowledge_base = {
            "hello": "Hello! Nice to meet you. 👋",
            "hi": "Hi! How can I help you?",
            "hey": "Hey there! 😊",
            "how are you": "I'm doing great! Thanks for asking.",
            "what is ai": "Artificial Intelligence enables machines to mimic human intelligence.",
            "what is machine learning": "Machine Learning is a branch of AI where computers learn from data.",
            "what is python": "Python is one of the most popular programming languages for AI and ML.",
            "what is data science": "Data Science is the process of extracting knowledge from data.",
            "who created you": "I was created using Python and Flask.",
            "thank you": "You're welcome! 😊",
            "about": "I am a Rule-Based AI Chatbot built for an AI/ML Internship Project.",
            "what can you do?": "Type HELP to know",
            "help me write code": "Sure! What would you like to build? Share your programming language, framework, and what you're trying to achieve (or any error you're getting), and I'll help you write, debug, or improve the code.",
            "give me a fun fact": "Type Fun",
            "show all commands": "Type help"
        }

        # Intent Scoring Matrix (Keywords have weights)
        self.intents = {
            "HELP": {"keywords": {"help": 1.0, "commands": 0.9, "menu": 0.8}, "response": "help_menu"},
            "TIME": {"keywords": {"time": 1.0, "hours": 0.8, "clock": 0.7}, "response": "time"},
            "DATE": {"keywords": {"date": 1.0, "day": 0.6, "today": 0.8}, "response": "date"},
            "JOKE": {"keywords": {"joke": 1.0, "funny": 0.8, "laugh": 0.9}, "response": "joke"},
            "MOTIVATE": {"keywords": {"motivate": 1.0, "motivation": 1.0, "quote": 0.9, "inspire": 0.8}, "response": "motivate"},
            "FACT": {"keywords": {"fact": 1.0, "facts": 1.0, "fun": 0.7}, "response": "fact"},
            "TIP": {"keywords": {"tip": 1.0, "tips": 1.0, "advice": 0.8, "programming": 0.5}, "response": "tip"},
            "WEATHER": {"keywords": {"weather": 1.0, "temperature": 0.9, "rain": 0.8, "sunny": 0.7}, "response": "weather"},
            "NEWS": {"keywords": {"news": 1.0, "latest": 0.7, "update": 0.6}, "response": "news"},
            "QUIZ_ASK": {"keywords": {"quiz": 1.0, "question": 0.8, "test": 0.9}, "response": "quiz"},
            "QUIZ_ANSWER": {"keywords": {"a": 0.5, "b": 0.5, "c": 0.5, "d": 0.5}, "response": "quiz_check"},
            "CALCULATOR": {"keywords": {"calc": 1.0, "calculate": 1.0, "math": 0.8, "solve": 0.9}, "response": "calculator"},
            "SENTIMENT_GOOD": {"keywords": {"happy": 1.0, "great": 1.0, "good": 0.8, "awesome": 1.0}, "response": "sentiment_good"},
            "SENTIMENT_BAD": {"keywords": {"sad": 1.0, "bad": 1.0, "angry": 1.0, "upset": 1.0}, "response": "sentiment_bad"},
            "FAREWELL": {"keywords": {"bye": 1.0, "exit": 0.9, "quit": 0.9, "goodbye": 1.0}, "response": "farewell"},
            "FOLLOW_UP": {"keywords": {"another": 0.9, "more": 0.9, "again": 1.0, "next": 0.8}, "response": "follow_up"}
        }

        # Data arrays
        self.jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did Python go to school? To improve its classes!",
            "AI never sleeps... it just keeps learning!",
            "Why don't robots panic? Because they have nerves of steel!"
        ]
        self.quotes = ["Success comes from consistency.", "Believe in yourself.", "Practice makes progress.", "Dream big and work hard.", "Every expert was once a beginner."]
        self.facts = ["Python is the most popular language for AI.", "Machine Learning is a subset of AI.", "Deep Learning uses Neural Networks.", "John McCarthy coined the term Artificial Intelligence.", "AI is used in healthcare, finance, and self-driving cars."]
        self.tips = ["Practice coding every day.", "Build real-world projects.", "Read Python documentation.", "Debug patiently.", "Never stop learning."]

    def _calculate_similarity(self, text1, text2):
        return SequenceMatcher(None, text1, text2).ratio()

    def _check_knowledge_base(self, user_input):
        """First pass: Check for exact or highly similar matches in legacy knowledge base."""
        best_match = None
        highest_score = 0.85 # Strict threshold for KB matches

        for key in self.knowledge_base:
            score = self._calculate_similarity(user_input, key)
            if score > highest_score:
                highest_score = score
                best_match = key
                
        return self.knowledge_base[best_match] if best_match else None

    def _calculate_intent_scores(self, user_input):
        """Second pass: Algorithmic scoring for dynamic intents."""
        scores = {}
        tokens = user_input.split()
        
        for intent_name, intent_data in self.intents.items():
            score = 0.0
            for token in tokens:
                for keyword, weight in intent_data["keywords"].items():
                    if token == keyword:
                        score += weight
                    elif self._calculate_similarity(token, keyword) > 0.8: # Fuzzy token match
                        score += (weight * self._calculate_similarity(token, keyword))
            
            scores[intent_name] = score / math.sqrt(len(tokens)) if len(tokens) > 0 else 0
            
        return scores

    def process_input(self, user_input):
        user_input = user_input.strip().lower()

        # 1. Context State Machine Check (Priority 1: If waiting for a quiz answer)
        if self.context.current_state == "AWAITING_QUIZ_ANSWER":
            if user_input in ['a', 'b', 'c', 'd']:
                self.context.update("QUIZ_ANSWER")
                if user_input == 'b':
                    return "✅ Correct! John McCarthy is known as the Father of AI."
                else:
                    return "❌ Wrong! Correct answer is B. John McCarthy."
            # If they ask something else during a quiz, break state and process normally
            self.context.update("DEFAULT")

        # 2. Knowledge Base Check (Priority 2: High accuracy fuzzy matching)
        kb_response = self._check_knowledge_base(user_input)
        if kb_response:
            self.context.update("KB_MATCH")
            return kb_response

        # 3. Intent Scoring Engine (Priority 3: Weighted algorithms)
        scores = self._calculate_intent_scores(user_input)
        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]

        if confidence < 0.4:
            self.context.update("FALLBACK")
            return "Sorry! I don't understand that. Type 'help' to see available commands."

        # 4. Process Follow-ups before executing normal intent
        if best_intent == "FOLLOW_UP":
            last_intent = self.context.get_last_intent()
            if last_intent in ["JOKE", "FACT", "TIP", "MOTIVATE", "QUIZ_ASK"]:
                best_intent = last_intent # Re-execute the last intent
            else:
                return "I'm not sure what you want another one of."

        # 5. Execute Intent & Generate Response
        response_action = self.intents[best_intent]["response"]
        final_response = ""

        if response_action == "help_menu":
            final_response = """Available Commands\n\n• hello\n• how are you\n• time\n• date\n• joke\n• motivate\n• fact\n• tip\n• weather\n• news\n• quiz\n• about\n• bye\n• calc 10+20"""
        elif response_action == "time":
            final_response = "Current Time: " + datetime.now().strftime("%I:%M:%S %p")
        elif response_action == "date":
            final_response = "Today's Date: " + datetime.now().strftime("%d-%m-%Y")
        elif response_action == "joke":
            final_response = random.choice(self.jokes)
        elif response_action == "motivate":
            final_response = random.choice(self.quotes)
        elif response_action == "fact":
            final_response = random.choice(self.facts)
        elif response_action == "tip":
            final_response = random.choice(self.tips)
        elif response_action == "weather":
            final_response = "☀️ Today's Weather\nTemperature: 30°C\nCondition: Sunny"
        elif response_action == "news":
            final_response = """Latest AI News\n\n• OpenAI released a new AI model.\n• AI is transforming healthcare.\n• Robotics continues to grow rapidly."""
        elif response_action == "quiz":
            final_response = "Who is known as the Father of AI?\nA. Elon Musk\nB. John McCarthy\nC. Bill Gates\nD. Sundar Pichai"
        elif response_action == "calculator":
            math_expr = self.extractor.extract_math(user_input)
            if math_expr:
                try:
                    final_response = f"Answer = {eval(math_expr)}"
                except:
                    final_response = "Math error! Usage: calc 10+20"
            else:
                final_response = "Usage: calc 10+20 or calc 15*6"
        elif response_action == "sentiment_good":
            final_response = "😊 I'm glad you're feeling good!"
        elif response_action == "sentiment_bad":
            final_response = "❤️ I hope everything gets better soon."
        elif response_action == "farewell":
            final_response = "Goodbye! Have a wonderful day. 👋"

        # 6. Update Context Memory
        self.context.update(best_intent)

        return final_response


# ==========================================
# FLASK INTEGRATION POINT
# ==========================================
# We instantiate the class GLOBALLY so it remembers context across HTTP requests.
# If we put this inside get_response(), it would forget your quiz answers!
chat_engine = AdvancedChatbotEngine()

def get_response(user):
    """Flask calls this function. It delegates to the advanced engine."""
    return chat_engine.process_input(user)