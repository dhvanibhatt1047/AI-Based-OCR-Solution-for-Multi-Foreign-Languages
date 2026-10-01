from paddleocr import PaddleOCR

# Set up the OCR engine for Chinese text
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="ch",
    enable_mkldnn=False
)

# Run OCR on the test image
result = ocr.predict("test.png")

# Print and save the results
for res in result:
    res.print()
    res.save_to_img("output")
    res.save_to_json("output")