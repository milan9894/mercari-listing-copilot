
# 🛍️ Mercari Listing Copilot
### AI-Assisted Resale Listing Platform

Mercari Listing Copilot is an AI-powered prototype designed to reduce the effort required to create second-hand marketplace listings. It transforms product photos into editable listing drafts and helps sellers estimate a price using comparable-item prices they provide.

## 🎯 Problem Statement

Creating a resale listing can be time-consuming. Sellers need to describe their items accurately, identify important missing details, and choose a reasonable asking price. These tasks can create friction, particularly for first-time sellers.

## 💡 Proposed Solution

Mercari Listing Copilot combines image understanding and price estimation in one simple interface.

**Product principle: AI proposes. The seller decides.**

## ✨ Key Features

- **Photo-to-listing generation:** Uses Google's Gemini API to analyze an uploaded product image and draft a listing.
- **Editable listing content:** Lets sellers review and modify the suggested title and description.
- **Seller verification prompts:** Highlights details sellers should confirm rather than treating uncertain visual guesses as facts.
- **Comparable-price estimator:** Calculates the median of seller-provided comparable prices and displays an illustrative range.
- **Downloadable listing:** Allows sellers to save their edited listing as a text file.
- **Currency selection:** Supports the currencies configured in the application.

## ⚙️ How It Works

1. The seller uploads a product photo.
2. The seller selects the item category and reported condition and may provide additional details.
3. Gemini generates a draft based on the photo and seller-provided information.
4. The seller reviews and edits the generated content.
5. The seller enters prices from comparable items.
6. The application calculates the median and an illustrative range.
7. The seller downloads the final draft.

## 🧰 Technology Stack

- Python
- Streamlit
- Google Gemini API (`google-genai`)
- Pillow
- python-dotenv

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/milan9894/mercari-listing-copilot.git
cd mercari-listing-copilot
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
py -m pip install -r requirements.txt
```

### 4. Configure your API key

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_api_key_here
```

Replace the placeholder with your own Gemini API key. Never commit your `.env` file or expose your API key publicly.

### 5. Start the application

```powershell
py -m streamlit run app.py
```

## 💰 Pricing Methodology

The prototype uses prices entered by the seller for comparable items.

- Reference price: median of the entered comparable prices.
- Illustrative lower estimate: median × 0.90.
- Illustrative upper estimate: median × 1.10.

This range is a simple heuristic, not a verified market valuation. The current prototype does not automatically retrieve live marketplace prices.

## 🛡️ Responsible AI

- AI-generated descriptions are drafts, not verified product facts.
- Sellers should confirm brand, model, size, material, authenticity, and other important details.
- The photo may not reveal hidden damage or whether an item works.
- Sellers retain control over the final listing and asking price.

## 🔭 Future Improvements

- Automated research of current prices from permitted marketplace data sources.
- More robust structured AI output and listing validation.
- Optional WhatsApp listing summaries using Twilio.
- Listing quality checks and usability testing.
- Deployment as a publicly accessible web application.

## 📌 Project Status

Working local prototype. AI listing generation, seller editing, listing download, and comparable-price estimation have been tested locally. Live marketplace price research, WhatsApp integration, and public deployment remain future improvements.

---

Built as an AI-assisted product concept exploring multimodal AI, seller experience, and resale marketplace workflows.
