# Document Verification System - KYC Workflow

A comprehensive Python-based document verification system that extracts structured data from multiple document types (Government ID, Bank Statement, Employment Letter) and validates them across documents, similar to a KYC (Know Your Customer) workflow.

## 🚀 Features

- **Multi-document OCR**: Extract text from Government ID, Bank Statement, and Employment Letter images using pytesseract
- **AI-powered Data Extraction**: Use Google's Flan-T5-small model to extract structured fields from unstructured text
- **Cross-document Validation**: Apply 7 validation rules to ensure data consistency across documents
- **Data Normalization**: Clean and standardize extracted data (phone numbers, dates, PAN, Aadhaar)
- **JSON Output**: Generate structured verification results in JSON format

## 📋 System Requirements

- Python 3.12+
- Google Colab compatible (free tier)
- 4GB RAM minimum
- Internet connection for model downloads

## 🛠️ Installation & Setup

### Option 1: Google Colab (Recommended)

1. **Open Google Colab**: Go to [colab.research.google.com](https://colab.research.google.com)

2. **Create a new notebook** and run these setup commands:

```python
# Install system dependencies
!apt update && apt install -y tesseract-ocr

# Clone the repository (or upload files manually)
!git clone https://github.com/yourusername/document-verification-system.git
%cd document-verification-system

# Install Python dependencies
!pip install -r requirements.txt

# Run the verification system
!python main.py
```

### Option 2: Local Setup

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/document-verification-system.git
cd document-verification-system
```

2. **Install Tesseract OCR**:
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the system**:
```bash
python main.py
```

## 📁 Project Structure

```
document-verification-system/
├── main.py                 # Complete pipeline implementation
├── requirements.txt        # Python dependencies
├── README.md              # This documentation
├── outputs/               # Generated results
│   └── results.json       # Final JSON output
└── dataset/               # Document images (auto-created)
    ├── P001/              # Person 1 documents
    │   ├── government_id.jpg
    │   ├── bank_statement.jpg
    │   └── employment_letter.jpg
    └── P002/              # Person 2 documents
        ├── government_id.jpg
        ├── bank_statement.jpg
        └── employment_letter.jpg
```

## 🔧 How It Works

### Pipeline Overview

1. **Dataset Setup**: Downloads and organizes document images
2. **OCR Processing**: Extracts text from all document images using pytesseract
3. **Field Extraction**: Uses Flan-T5-small LLM to extract structured data
4. **Data Normalization**: Cleans and standardizes extracted fields
5. **Cross-validation**: Applies 7 validation rules across documents
6. **Output Generation**: Saves results in structured JSON format

### Extracted Fields

The system extracts these fields from each document:
- Full Name
- Father's Name
- Date of Birth
- Complete Address (house number, street, city, state, pincode)
- Phone Number
- Email Address
- Aadhaar Number (12 digits)
- PAN Number (5 letters + 4 digits + 1 letter)
- Employee ID
- Account Number

### Validation Rules

1. **Name Match**: Fuzzy matching of names across documents (≥80% similarity)
2. **DOB Match**: Exact date matching across documents
3. **Address Match**: Fuzzy matching of addresses (≥70% similarity)
4. **Phone Match**: Exact phone number matching
5. **Father's Name Match**: Fuzzy matching (≥80% similarity)
6. **PAN Format**: Validates proper PAN format (XXXXX9999X)
7. **Aadhaar Format**: Validates 12-digit Aadhaar format

### Overall Status

- **VERIFIED**: ≤2 validation rules failed
- **FAILED**: >2 validation rules failed

## 📊 Output Format

The system generates `outputs/results.json` with this structure:

```json
[
  {
    "person_id": "P001",
    "extracted_data": {
      "document_1": {
        "full_name": "Rahul Kumar Sharma",
        "fathers_name": "Vijay Kumar Sharma",
        "date_of_birth": "15-08-1995",
        "complete_address": "House No 123, Green Park New Delhi, Delhi 110016",
        "phone_number": "+91-9876543210",
        "email_address": "rahul.sharma@email.com",
        "aadhaar_number": "1234 5678 9012",
        "pan_number": "ABCDE1234F",
        "employee_id": "",
        "account_number": ""
      },
      "document_2": { /* Bank Statement fields */ },
      "document_3": { /* Employment Letter fields */ }
    },
    "verification_results": {
      "rule_1_name_match": { "status": "PASS" },
      "rule_2_dob_match": { "status": "PASS" },
      "rule_3_address_match": { "status": "PASS" },
      "rule_4_phone_match": { "status": "PASS" },
      "rule_5_father_name_match": { "status": "PASS" },
      "rule_6_pan_format": { "status": "PASS" },
      "rule_7_aadhaar_format": { "status": "PASS" }
    },
    "overall_status": "VERIFIED"
  }
]
```

## 🔍 Key Technologies

- **OCR**: pytesseract (Google Tesseract OCR Engine)
- **LLM**: google/flan-t5-small via Hugging Face Transformers
- **Text Matching**: rapidfuzz for fuzzy string matching
- **Date Processing**: python-dateutil for robust date parsing
- **Image Processing**: Pillow (PIL) for image handling
- **ML Framework**: PyTorch for model inference

## 🚨 Limitations & Considerations

- **Mock Data**: Currently uses simulated OCR results for demonstration
- **Model Size**: Flan-T5-small provides basic extraction; larger models may improve accuracy
- **OCR Quality**: Performance depends on document image quality
- **Free Tier**: Designed to work within Google Colab's free tier limitations
- **No Paid APIs**: Uses only open-source tools (no OpenAI, Google Cloud, etc.)

## 🔧 Customization

### Adding New Fields
Modify the `extraction_fields` list in `DocumentVerificationSystem.__init__()`:
```python
self.extraction_fields.append("New Field Name")
```

### Adjusting Validation Rules
Modify thresholds in `apply_validation_rules()` method:
```python
# Change fuzzy matching threshold
rules_result["rule_1_name_match"] = {
    "status": "PASS" if self._fuzzy_match_any(names, threshold=85) else "FAIL"
}
```

### Adding Document Types
Extend the OCR mock data methods and update document processing logic.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is created for educational and internship application purposes. Feel free to modify and use as needed.

## 📞 Support

For questions or issues:
1. Check the console output for detailed error messages
2. Ensure all dependencies are properly installed
3. Verify Tesseract OCR is available in system PATH
4. Check that Python 3.12+ is being used

## 🎯 Future Enhancements

- [ ] Real dataset integration with Google Drive download
- [ ] Support for additional document types
- [ ] Enhanced OCR preprocessing (image rotation, noise reduction)
- [ ] Web interface using FastAPI/Flask
- [ ] Database integration for result storage
- [ ] Advanced validation rules and scoring
- [ ] Multi-language document support
- [ ] PDF document processing capability

---

**Author**: Backend Python Developer Intern Application  
**Created**: October 2024  
**Version**: 1.0.0
