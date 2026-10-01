from paddleocr import PaddleOCR
import ollama

import re

def detect_language(text):
    """Returns 'zh-en' if text contains Chinese characters, else 'en-zh'."""
    if re.search(r'[\u4e00-\u9fff]', text):
        return "zh-en"
    return "en-zh"

# Set up OCR engine once (reused across calls)
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="ch",
    enable_mkldnn=False
)

def extract_chinese_text(image_path):
    """Run OCR on an image and return detected text lines + their confidence scores."""
    result = ocr.predict(image_path)
    texts = []
    scores = []
    for res in result:
        texts.extend(res["rec_texts"])
        scores.extend(res["rec_scores"])
    return texts, scores

def translate_text(text, direction="zh-en"):
    if direction == "en-zh":
        prompt = f"Translate the following English text to Chinese. Only output the translation, nothing else:\n\n{text}"
    else:
        prompt = f"Translate the following Chinese text to English. Only output the translation, nothing else:\n\n{text}"

    response = ollama.chat(
        model="qwen2.5",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

def process_image(image_path):
    """Full pipeline: image -> Chinese text -> English translation, with real scores."""
    chinese_lines, scores = extract_chinese_text(image_path)
    full_chinese = "\n".join(chinese_lines)
    english_translation = translate_text(full_chinese)

    avg_score = (sum(scores) / len(scores)) if scores else 0
    min_score = min(scores) if scores else 0

    return {
        "chinese_text": full_chinese,
        "english_text": english_translation,
        "accuracy": round(avg_score * 100, 1),
        "confidence": round(min_score * 100, 1)
    }

# Quick test when running this file directly
if __name__ == "__main__":
    result = process_image("test.png")
    print("=== CHINESE ===")
    print(result["chinese_text"])
    print("\n=== ENGLISH ===")
    print(result["english_text"])