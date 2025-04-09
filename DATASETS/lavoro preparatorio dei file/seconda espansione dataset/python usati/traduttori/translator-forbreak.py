import os
import json
import time
from tqdm import tqdm
import logging
from deep_translator import GoogleTranslator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("json_translation_log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def translate_json_file(input_file, output_file, source_lang='auto', target_lang='en'):
    """
    Translates the 'response' field of each JSON object in the input file
    
    Parameters:
    - input_file: path to the input JSON file
    - output_file: path to the output JSON file
    - source_lang: source language (default 'auto' for auto-detection)
    - target_lang: target language (default 'en' for English)
    """
    # Initialize the translator
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
    except ImportError:
        logger.error("Please install deep-translator: pip install deep-translator")
        return
    
    # Load the JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Check if file contains a JSON array or a single JSON object
            if content.startswith('['):
                data = json.loads(content)
            else:
                # Handle single object
                try:
                    data = [json.loads(content)]
                except:
                    # Try parsing as JSON Lines (one object per line)
                    data = []
                    for line in content.strip().split('\n'):
                        if line.strip():
                            data.append(json.loads(line))
        
        logger.info(f"Loaded {len(data)} JSON items")
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        return

    # Process each item
    translated_data = []
    for i, item in enumerate(tqdm(data, desc="Translating")):
        try:
            # Create a copy of the item
            translated_item = item.copy()
            
            # Only translate the 'response' field
            if "response" in item and item["response"]:
                try:
                    translated_text = translator.translate(item["response"])
                    translated_item["response"] = translated_text
                    logger.info(f"Item {i+1}/{len(data)}: Translated response field")
                except Exception as e:
                    logger.error(f"Error translating item {i+1}: {e}")
                    # Keep original on error
            
            translated_data.append(translated_item)
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error processing item {i+1}: {e}")
            translated_data.append(item)  # Keep original item on error
    
    # Save the translated data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Translation completed. Saved {len(translated_data)} items to {output_file}")

if __name__ == "__main__":
    # Change these parameters as needed
    INPUT_FILE = "POTENTIAL_JAILBREAKS.json"
    OUTPUT_FILE = "POTENTIAL_JAILBREA_TRANSLATE.json"
    SOURCE_LANGUAGE = "auto"  # "auto" for automatic detection
    TARGET_LANGUAGE = "en"    # "en" for English, "it" for Italian, etc.
    
    translate_json_file(
        input_file=INPUT_FILE,
        output_file=OUTPUT_FILE,
        source_lang=SOURCE_LANGUAGE,
        target_lang=TARGET_LANGUAGE
    )