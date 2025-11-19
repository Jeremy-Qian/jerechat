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

def load_corpus(filename: str) -> List[Tuple[str, str]]:
    """
    Load Q&A pairs from corpus file.
    Format: Q on one line, A on next line, repeated.
    """
    qa_pairs = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        i = 0
        while i < len(lines):
            # Skip empty lines
            if not lines[i].strip():
                i += 1
                continue
            
            # Get question (current non-empty line)
            question = lines[i].strip()
            i += 1
            
            # Find next non-empty line for answer
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            if i < len(lines):
                answer = lines[i].strip()
                qa_pairs.append((question, answer))
                i += 1
            else:
                # Question without answer
                break
                
    except FileNotFoundError:
        print(f"Error: Corpus file '{filename}' not found.")
        return []
    except Exception as e:
        print(f"Error reading corpus file: {e}")
        return []
    
    return qa_pairs

def find_best_match(user_input: str, qa_pairs: List[Tuple[str, str]]) -> str:
    """
    Find the best matching question using Jaccard similarity.
    Returns the answer if similarity >= threshold, otherwise a default response.
    """
    best_similarity = 0.0
    best_answer = "I'm sorry, I don't understand. Could you rephrase that?"
    
    for question, answer in qa_pairs:
        similarity = jaccard_similarity(user_input, question)
        if similarity > best_similarity:
            best_similarity = similarity
            best_answer = answer
    
    return best_answer

def chatbot():
    """
    Main chatbot function.
    """
    print("JereChat: Hello! I'm a simple chatbot. Type 'quit' to exit.")
    
    # Load corpus
    qa_pairs = load_corpus('corpus.txt')
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


def generate_response(user_input, model="1.5"):
    """
    Generate response using loaded corpus.
    """
    
    # Load corpus from the correct path
    corpus_path = os.path.join(os.path.dirname(__file__), 'corpus.txt')
    qa_pairs = load_corpus(corpus_path)
    if not qa_pairs:
        print("JereChat: No knowledge base loaded. Exiting.")
        return "I'm sorry, I don't have any knowledge base loaded to help you."
    
    # Find and return best match
    response = find_best_match(user_input, qa_pairs)
    return response


if __name__ == "__main__":
    chatbot()