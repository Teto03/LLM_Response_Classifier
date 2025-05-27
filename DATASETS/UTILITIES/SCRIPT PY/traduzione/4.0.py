import os
import time
import json
from pathlib import Path
from tqdm import tqdm
import logging
import re
import langdetect
from langdetect import DetectorFactory

# Make language detection deterministic
DetectorFactory.seed = 0

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

def get_translator(translator_type="offline", to_lang="en"):
    """Creates and returns the appropriate translator based on the specified type"""
    # Default to offline translator to handle sensitive content better
    if translator_type == "google":
        try:
            from deep_translator import GoogleTranslator
            # Google Translator has auto-detection which works better with multilingual content
            return GoogleTranslator(source='auto', target=to_lang)
        except ImportError:
            logger.error("To use GoogleTranslator install: pip install deep-translator")
            return None
    elif translator_type == "offline":
        try:
            from argostranslate import package, translate
            
            # Check if packages are already installed
            if not package.get_installed_packages():
                logger.info("Downloading and installing translation packages...")
                package.update_package_index()
                
                # For a multilingual approach, we need to install all available packages
                # that have English as the target language
                available_packages = package.get_available_packages()
                installed_count = 0
                
                for pkg in available_packages:
                    if pkg.to_code == to_lang:
                        try:
                            pkg.install()
                            installed_count += 1
                            logger.info(f"Installed package: {pkg.from_code} -> {pkg.to_code}")
                        except Exception as e:
                            logger.error(f"Error installing {pkg.from_code}: {str(e)}")
                
                logger.info(f"Installed {installed_count} translation packages to {to_lang}")
                
                if installed_count == 0:
                    logger.error(f"No packages found with target {to_lang}")
                    return None
            
            # Get all installed languages
            installed_languages = translate.get_installed_languages()
            target_lang = next((lang for lang in installed_languages if lang.code == to_lang), None)
            
            if not target_lang:
                logger.error(f"Target language {to_lang} not available")
                return None
                
            # Create a wrapper that attempts to translate with different models
            class MultilingualArgosTranslator:
                def __init__(self, installed_languages, target_lang_code):
                    self.target_lang_code = target_lang_code
                    self.installed_languages = installed_languages
                    self.models = {}
                    
                    # Find the target language object
                    target_lang = next((lang for lang in installed_languages if lang.code == target_lang_code), None)
                    if not target_lang:
                        logger.error(f"Target language {target_lang_code} not available")
                        return
                    
                    # Pre-load available translation models
                    for lang in installed_languages:
                        if lang.code != target_lang_code:
                            translation = lang.get_translation(target_lang)  # Pass language object instead of string
                            if translation:
                                self.models[lang.code] = translation
                    
                    if not self.models:
                        logger.error("No translation models available")
                
                def translate(self, text):
                    # If text is already in English, no need to translate
                    if self._is_probably_english(text):
                        return text
                    
                    # Try to detect the language (simple implementation)
                    detected_lang = self._detect_language(text)
                    
                    if detected_lang in self.models:
                        return self.models[detected_lang].translate(text)
                    else:
                        # Fallback: try all languages until we find a translation that looks correct
                        best_translation = text
                        for lang_code, model in self.models.items():
                            try:
                                translation = model.translate(text)
                                # If the translation has a higher percentage of Latin characters
                                # than the original text, it might be better
                                if self._quality_score(translation) > self._quality_score(best_translation):
                                    best_translation = translation
                            except:
                                continue
                        
                        return best_translation
                
                def _is_probably_english(self, text):
                    # Use the improved function
                    return is_probably_english(text)
                
                def _detect_language(self, text):
                    # Use langdetect for better language detection
                    try:
                        return langdetect.detect(text)
                    except:
                        # Fallback based on simple heuristics
                        # Check specific characters for some languages
                        if any(ord(c) > 1000 for c in text):  # Non-Latin characters
                            for candidate in ["ar", "ru", "zh", "ja", "ko", "th"]:
                                if candidate in self.models:
                                    return candidate
                        
                        # Default to a common language
                        return next(iter(self.models.keys())) if self.models else "en"
                
                def _quality_score(self, text):
                    # Calculate a quality score for the translation
                    # Higher score means it's more likely to be a good translation in English
                    
                    # Score based on percentage of Latin characters
                    latin_chars = sum(1 for c in text if 'a' <= c.lower() <= 'z')
                    total_chars = max(1, len(text.strip()))
                    
                    return latin_chars / total_chars
            
            return MultilingualArgosTranslator(installed_languages, to_lang)
            
        except ImportError:
            logger.error("To use the offline translator install: pip install argostranslate langdetect")
            return None
    elif translator_type == "combo":
        # A hybrid solution that uses offline first (for sensitive content), then Google as fallback
        offline_translator = get_translator("offline", to_lang)
        if offline_translator:
            return offline_translator
        
        logger.warning("Offline translator not available, using Google translator (sensitive content might be filtered)")
        return get_translator("google", to_lang)
    else:
        logger.error(f"Unsupported translator type: {translator_type}")
        return None

def is_probably_english(text):
    """More accurate detection of English text"""
    if not text or text.isspace():
        return True
        
    # If text is very short, use character-based heuristics
    if len(text) < 15:
        latin_chars = sum(1 for c in text.lower() if 'a' <= c <= 'z' or c in ',.!? ')
        return latin_chars / max(1, len(text)) > 0.7
    
    # Use langdetect for more accurate language detection
    try:
        lang = langdetect.detect(text)
        return lang == 'en'
    except:
        # Fallback to simple heuristics if langdetect fails
        common_english_words = {"the", "and", "is", "in", "to", "of", "that", "for", "it", "with"}
        words = text.lower().split()
        if not words:
            return True
        
        english_count = sum(1 for word in words if word in common_english_words)
        non_latin_count = sum(1 for c in text if ord(c) > 127)
        
        # If significant non-latin characters, probably not English
        if non_latin_count / max(1, len(text)) > 0.3:
            return False
            
        return english_count / len(words) > 0.15

def segment_text(text, threshold=0.2):
    """Improved text segmentation for mixed-language content"""
    if not text:
        return []
    
    # For very short text, just process as a single segment
    if len(text) < 100:
        return [(text, is_probably_english(text))]
    
    # Try to detect sentence boundaries across multiple languages
    # This regex handles sentence endings in various languages
    sentences = re.split(r'([.!?。！？\n]+\s*)', text)
    
    result = []
    current_segment = ""
    current_lang = None
    
    for i in range(0, len(sentences), 2):
        sentence = sentences[i] if i < len(sentences) else ""
        ending = sentences[i+1] if i+1 < len(sentences) else ""
        full_sentence = sentence + (ending if ending else "")
        
        if not full_sentence:
            continue
            
        # Try to detect language
        try:
            # For short segments, rely on character analysis
            if len(full_sentence) < 20:
                # Check if mostly non-Latin characters (likely Asian language)
                non_latin = sum(1 for c in full_sentence if ord(c) > 127)
                is_english = non_latin / max(1, len(full_sentence)) < 0.3
            else:
                # Use more accurate language detection for longer segments
                detected_lang = langdetect.detect(full_sentence)
                is_english = detected_lang == 'en'
                
        except Exception:
            # Default to analyzing non-Latin character ratio if detection fails
            non_latin = sum(1 for c in full_sentence if ord(c) > 127)
            is_english = non_latin / max(1, len(full_sentence)) < 0.3
        
        # If first segment or the language changed
        if current_lang is None:
            current_segment = full_sentence
            current_lang = is_english
        elif is_english != current_lang or len(current_segment) > 4000:
            # Language changed or segment is getting too large
            result.append((current_segment, current_lang))
            current_segment = full_sentence
            current_lang = is_english
        else:
            # Same language, keep appending
            current_segment += full_sentence
    
    # Add the last segment
    if current_segment:
        result.append((current_segment, current_lang))
    
    return result

def translate_with_fallbacks(translator, text, chunk_size=4500, delay=2):
    """
    Attempts to translate text with multiple fallback strategies if the initial translation fails,
    particularly for sensitive content that might be filtered by translation services
    """
    # First try normal translation
    try:
        return translator.translate(text)
    except Exception as e:
        logger.warning(f"Initial translation failed: {e}")
        
        # Strategy 1: Try offline translator if available
        if hasattr(translator, 'get_translation'):
            logger.info("Already using offline translator, trying alternative strategies")
        else:
            logger.info("Trying to use offline translator instead")
            try:
                from argostranslate import package, translate
                # Try to get the appropriate language model
                installed_languages = translate.get_installed_languages()
                target_lang = next((lang for lang in installed_languages if lang.code == "en"), None)
                if target_lang:
                    # Try to detect source language
                    try:
                        source_lang_code = langdetect.detect(text)
                        source_lang = next((lang for lang in installed_languages if lang.code == source_lang_code), None)
                        if source_lang and source_lang.get_translation(target_lang.code):
                            translation = source_lang.get_translation(target_lang.code).translate(text)
                            return translation
                    except:
                        pass
            except ImportError:
                logger.warning("Offline translator not available")
        
        # Strategy 2: Break into very small chunks
        try:
            logger.info("Attempting translation with small chunks")
            words = re.findall(r'\S+|\s+', text)
            micro_chunks = []
            current_chunk = ""
            
            for word in words:
                if len(current_chunk) + len(word) > 100:  # Very small chunks
                    micro_chunks.append(current_chunk)
                    current_chunk = word
                else:
                    current_chunk += word
            
            if current_chunk:
                micro_chunks.append(current_chunk)
            
            translated_chunks = []
            for chunk in micro_chunks:
                try:
                    translated_chunk = translator.translate(chunk)
                    translated_chunks.append(translated_chunk)
                    time.sleep(delay / 2)  # Reduced delay for smaller chunks
                except Exception as chunk_error:
                    logger.warning(f"Chunk translation failed: {chunk_error}")
                    # If even small chunk fails, keep original
                    translated_chunks.append(chunk)
            
            return ''.join(translated_chunks)
        except Exception as chunking_error:
            logger.error(f"Chunking strategy failed: {chunking_error}")
            
            # Strategy 3: Try to mask sensitive words
            try:
                logger.info("Attempting translation with content masking")
                # Define common sensitive terms that might trigger filters
                sensitive_terms = [
                    "bomb", "explosive", "weapon", "poison", "kill", "attack", 
                    "terrorist", "suicide", "hack", "virus", "illegal", "drug",
                    "murder", "torture", "violence", "molest", "harm", "theft",
                    "steal", "dangerous", "illegal", "harmful", "death", "deadly"
                ]
                
                # Create a dictionary to store original terms
                masked_text = text
                replacements = {}
                
                # Replace sensitive terms with neutral placeholders
                for i, term in enumerate(sensitive_terms):
                    pattern = re.compile(r'\b' + term + r'\b', re.IGNORECASE)
                    placeholder = f"TERM_{i}"
                    
                    # Store all matches
                    for match in pattern.finditer(masked_text):
                        original = match.group(0)
                        if placeholder not in replacements:
                            replacements[placeholder] = []
                        replacements[placeholder].append(original)
                    
                    # Replace in text
                    masked_text = pattern.sub(placeholder, masked_text)
                
                # Translate the masked text
                translated_masked = translator.translate(masked_text)
                
                # Restore original terms
                restored_text = translated_masked
                for placeholder, originals in replacements.items():
                    for original in originals:
                        restored_text = restored_text.replace(placeholder, original, 1)
                
                return restored_text
            except Exception as masking_error:
                logger.error(f"Masking strategy failed: {masking_error}")
                
                # If all strategies fail, return original text
                logger.warning("All translation strategies failed. Returning original text.")
                return text

def translate_json_file(input_file, output_file, translator_type="offline", to_lang="en", 
                         chunk_size=4500, delay=2, fields_to_translate=None):
    """
    Translates a JSON file containing multilingual text fields to English
    
    Parameters:
    - input_file: path to the input JSON file
    - output_file: path to the output JSON file
    - translator_type: "google", "offline" or "combo" (default "offline" to handle sensitive content)
    - to_lang: target language (default "en" for English)
    - chunk_size: maximum size in characters for each translation request
    - delay: delay in seconds between translations
    - fields_to_translate: list of field names to translate (default: ["response"])
    """
    # Default field to translate
    if fields_to_translate is None:
        fields_to_translate = ["response"]
    
    # Backup file names for progress
    backup_file = f"{output_file}.progress"
    temp_output = f"{output_file}.temp"
    
    # Initialize the translator - use offline by default for sensitive content
    translator = get_translator(translator_type, to_lang)
    if not translator:
        logger.error("Failed to initialize translator")
        return
    
    # Check if a progress file exists
    last_translated_idx = -1
    translated_data = []
    
    if os.path.exists(backup_file):
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                last_translated_idx = int(f.read().strip())
            
            # Load already translated data if temp file exists
            if os.path.exists(temp_output):
                with open(temp_output, 'r', encoding='utf-8') as f:
                    translated_data = json.load(f)
            
            logger.info(f"Resuming translation: found {len(translated_data)} already translated items")
        except Exception as e:
            logger.error(f"Error loading progress: {e}")
            last_translated_idx = -1
            translated_data = []
    
    # Load the JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            # Check if file starts as an array or if items are comma-separated objects
            content = f.read().strip()
            if content.startswith('['):
                data = json.loads(content)
            else:
                # Handle case where each line might be a JSON object
                data = []
                try:
                    # Try to parse the file as JSON Lines
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.isspace():
                            if line.endswith(','):
                                line = line[:-1]
                            try:
                                obj = json.loads(line)
                                data.append(obj)
                            except json.JSONDecodeError:
                                # Skip invalid lines
                                logger.warning(f"Skipping invalid JSON line: {line[:50]}...")
                except Exception as e:
                    logger.error(f"Error parsing JSON Lines: {e}")
                    # Try wrapping with brackets and parsing as array
                    try:
                        data = json.loads(f"[{content}]")
                    except:
                        logger.error("Failed to parse JSON file in any format")
                        return
        
        logger.info(f"Loaded {len(data)} JSON items")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return
    except UnicodeDecodeError:
        # Try with different encodings if UTF-8 fails
        encodings = ['latin-1', 'iso-8859-1', 'cp1252']
        for enc in encodings:
            try:
                with open(input_file, 'r', encoding=enc) as f:
                    data = json.loads(f.read())
                logger.info(f"File opened with encoding: {enc}")
                break
            except:
                continue
        else:
            logger.error("Unable to open file with supported encodings")
            return
    
    # If we're starting fresh, initialize translated_data
    if last_translated_idx == -1:
        translated_data = []
    
    # Start translating items
    for i, item in enumerate(tqdm(data[last_translated_idx+1:], 
                                desc="Translating JSON items")):
        idx = i + last_translated_idx + 1
        
        try:
            # Create a copy of the item
            translated_item = item.copy()
            
            # Translate each specified field
            for field in fields_to_translate:
                if field in item and item[field]:
                    text = item[field]
                    
                    # Check if the text contains any non-Latin characters
                    # This helps identify if there are Asian languages mixed in
                    contains_non_latin = any(ord(c) > 127 for c in text)
                    
                    # Skip if text is already entirely in English
                    if not contains_non_latin and is_probably_english(text):
                        logger.info(f"  Item {idx+1}/{len(data)}: Field '{field}' already in English, skipping")
                        translated_item[field] = text
                        continue
                    
                    # Check if the text might contain sensitive content
                    potentially_sensitive = False
                    sensitive_patterns = [
                        r'\b(bomb|explosive|weapon|gun|poison|kill|suicide|hack|torture)\b',
                        r'\b(terrorist|attack|harmful|illegal|deadly|murder|violence)\b'
                    ]
                    
                    for pattern in sensitive_patterns:
                        if re.search(pattern, text, re.IGNORECASE):
                            potentially_sensitive = True
                            break
                    
                    # For potentially sensitive content or mixed languages, use our special handling
                    if potentially_sensitive or contains_non_latin:
                        try:
                            translated_text = translate_with_fallbacks(translator, text, chunk_size, delay)
                            translated_item[field] = translated_text
                            if potentially_sensitive:
                                logger.info(f"  Item {idx+1}/{len(data)}: Potentially sensitive content translated with special handling")
                            else:
                                logger.info(f"  Item {idx+1}/{len(data)}: Mixed language content translated")
                            time.sleep(delay)
                            continue
                        except Exception as e:
                            logger.error(f"Error in special translation handling: {e}")
                            # Fall back to segmented translation
                    
                    # For standard content, use segment-based approach
                    segments = segment_text(text)
                    translated_segments = []
                    
                    for segment_text, is_english in segments:
                        if is_english:
                            # Keep English segments as is
                            translated_segments.append(segment_text)
                        else:
                            # Translate non-English segments
                            if len(segment_text) > chunk_size:
                                # Break into smaller chunks if needed
                                chunks = []
                                start = 0
                                while start < len(segment_text):
                                    # Try to break at sentence boundaries
                                    end = min(start + chunk_size, len(segment_text))
                                    if end < len(segment_text):
                                        # Look for sentence ending
                                        sentence_end = max(segment_text.rfind('. ', start, end),
                                                        segment_text.rfind('! ', start, end),
                                                        segment_text.rfind('? ', start, end))
                                        if sentence_end > start:
                                            end = sentence_end + 2  # Include the punctuation and space
                                    
                                    chunks.append(segment_text[start:end])
                                    start = end
                                
                                # Translate each chunk
                                translated_chunks = []
                                for j, chunk in enumerate(chunks):
                                    try:
                                        # Use fallback translation for each chunk
                                        translated_chunk = translate_with_fallbacks(translator, chunk, chunk_size, delay/2)
                                        translated_chunks.append(translated_chunk)
                                        logger.info(f"  Item {idx+1}/{len(data)}: Chunk {j+1}/{len(chunks)} translated")
                                        time.sleep(delay/2)
                                    except Exception as e:
                                        logger.error(f"Error translating chunk {j+1}: {e}")
                                        translated_chunks.append(chunk)  # Keep original on error
                                
                                translated_segments.append(''.join(translated_chunks))
                            else:
                                # Translate the segment
                                try:
                                    translated_segment = translate_with_fallbacks(translator, segment_text, chunk_size, delay)
                                    translated_segments.append(translated_segment)
                                    time.sleep(delay)
                                except Exception as e:
                                    logger.error(f"Error translating segment: {e}")
                                    translated_segments.append(segment_text)  # Keep original on error
                    
                    # Join all segments back together
                    translated_item[field] = ''.join(translated_segments)
            
            # Add to translated data
            translated_data.append(translated_item)
            
            # Save progress
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(str(idx))
            
            # Save temporary output
            with open(temp_output, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Error processing item {idx+1}: {e}")
            translated_data.append(item)  # Keep original item on error
            
            # Save progress anyway
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(str(idx))
            
            with open(temp_output, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=2)
    
    # Save the final file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)
    
    # Remove temporary files if translation completed successfully
    if len(translated_data) == len(data):
        try:
            if os.path.exists(backup_file):
                os.remove(backup_file)
            if os.path.exists(temp_output):
                os.remove(temp_output)
        except Exception as e:
            logger.warning(f"Warning: unable to remove temporary files: {e}")
    
    logger.info(f"{len(translated_data)} items translated and saved to '{output_file}'")

# Example usage
if __name__ == "__main__":
    translate_json_file(
        'BREAK.json', # Input file
        'BREAK_TRANSLATED.json',  # Output file
        translator_type="offline",  # Changed default to "offline" to handle sensitive content better
        to_lang="en",  # Target language
        chunk_size=4500,  # Maximum chunk size in characters
        delay=2,  # Delay between translations in seconds
        fields_to_translate=["response"]  # Fields to translate in each JSON object
    )