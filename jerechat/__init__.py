import os
import re
from typing import List, Tuple

def jaccard_similarity(text1: str, text2: str) -> float:
    """
    Calculate Jaccard similarity between two texts.
    Jaccard similarity = |A ∩ B| / |A ∪ B|
    where A and B are sets of words in the texts.
    """
    # Convert to lowercase and split into words
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    
    # Calculate intersection and union
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    # Return similarity (avoid division by zero)
    if len(union) == 0:
        return 0.0
    return len(intersection) / len(union)

def load_corpus(filename: str) -> List[Tuple[List[str], str]]:
    """
    Load Q&A pairs from corpus file.
    Format: Questions start with single '-', answers with '--'.
    Multiple questions can map to the same answer.
    """
    qa_pairs = []
    current_questions = []
    current_answer = ""
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('--'):
                    # This is an answer line
                    if current_questions:  # If we have questions waiting for an answer
                        current_answer = line[2:].strip()
                        qa_pairs.append((current_questions.copy(), current_answer))
                        current_questions = []
                elif line.startswith('-'):
                    # This is a question line
                    current_questions.append(line[1:].strip())
                
    except FileNotFoundError:
        print(f"Error: Corpus file '{filename}' not found.")
        return []
    except Exception as e:
        print(f"Error reading corpus file: {e}")
        return []
    
    return qa_pairs

def find_best_match(user_input: str, qa_pairs: List[Tuple[List[str], str]]) -> str:
    """
    Find the best matching question using Jaccard similarity.
    Combines similarity scores for all questions that map to the same answer.
    Returns the answer with the highest combined similarity score.
    """
    answer_scores = {}
    
    for questions, answer in qa_pairs:
        # Calculate max similarity for all questions mapping to this answer
        max_similarity = max(
            jaccard_similarity(user_input, q) 
            for q in questions
        )
        
        # Update the score for this answer
        if answer in answer_scores:
            answer_scores[answer] = max(answer_scores[answer], max_similarity)
        else:
            answer_scores[answer] = max_similarity
    
    if not answer_scores:
        return "I'm sorry, I don't understand. Could you rephrase that?"
    
    # Get answer with highest score
    best_answer = max(answer_scores.items(), key=lambda x: x[1])
    
    # Only return the answer if similarity is above a threshold
    if best_answer[1] > 0.1:  # Adjust threshold as needed
        return best_answer[0]
    else:
        return "I'm not sure I understand. Could you rephrase your question?"

def chatbot():
    """
    Main chatbot function.
    """
    print("JereChat: Hello! I'm a simple chatbot. Type 'quit' to exit.")
    
    # Load corpus from the correct path
    corpus_path = os.path.join(os.path.dirname(__file__), 'corpus.txt')
    qa_pairs = load_corpus(corpus_path)
    if not qa_pairs:
        print("JereChat: No knowledge base loaded. Exiting.")
        return
    
    print(f"JereChat: Loaded {len(qa_pairs)} Q&A pairs. How can I help you?")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("JereChat: Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Find and return best match
            response = find_best_match(user_input, qa_pairs)
            print(f"JereChat: {response}")
            
        except KeyboardInterrupt:
            print("\nJereChat: Goodbye!")
            break
        except Exception as e:
            print(f"JereChat: An error occurred: {e}")

def generate_response(user_input: str, model: str = "1.5") -> str:
    """
    Generate response using loaded corpus.
    
    Args:
        user_input: The user's input text
        model: Model version (not currently used, kept for compatibility)
        
    Returns:
        str: The chatbot's response
    """
    # Load corpus from the correct path
    corpus_path = os.path.join(os.path.dirname(__file__), 'corpus.txt')
    qa_pairs = load_corpus(corpus_path)
    if not qa_pairs:
        return "I'm sorry, I don't have any knowledge base loaded to help you."
    
    # Find and return best match
    return find_best_match(user_input, qa_pairs)

if __name__ == "__main__":
    chatbot()