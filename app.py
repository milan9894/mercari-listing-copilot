
import io
import math
import os
import re
import statistics

import streamlit as st
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError
from google import genai
from google.genai import types

# Load API key from .env
load_dotenv()

st.set_page_config(
    page_title="Mercari Listing Copilot",
    page_icon="🛍️",
    layout="wide",
)

st.title("🛍️ Mercari Listing Copilot")
st.subheader("Turn product photos into resale-ready listings")
st.write(
    "Upload a product photo to draft a listing and estimate "
    "a price using comparable items."
)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

if not api_key:
    st.warning(
        "Gemini API key not found. Add GEMINI_API_KEY to your "
        "local .env file and restart the app."
    )

# -------------------- SIDEBAR SETTINGS --------------------

with st.sidebar:
    st.header("⚙️ Listing settings")

    currency = st.selectbox(
        "Price currency",
        ["INR (₹)", "USD ($)", "JPY (¥)", "MYR (RM)"],
    )

    item_category = st.selectbox(
        "Item category",
        [
            "Auto-detect",
            "Clothing",
            "Electronics",
            "Books",
            "Home & Kitchen",
            "Collectibles",
            "Other",
        ],
    )

    condition = st.selectbox(
        "Seller-reported condition",
        [
            "Not specified",
            "New",
            "Like new",
            "Good",
            "Fair",
            "For parts or repair",
        ],
    )

# -------------------- IMAGE UPLOAD --------------------

uploaded_file = st.file_uploader(
    "📸 Upload a clear photo of your item",
    type=["png", "jpg", "jpeg", "webp"],
)

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file).convert("RGB")

        left, right = st.columns(2)

        with left:
            st.image(
                image,
                caption="Your product photo",
                use_container_width=True,
            )

        with right:
            st.markdown("### About your item")

            extra_details = st.text_area(
                "Anything else we should know?",
                placeholder=(
                    "Brand, model, size, age, defects, "
                    "original price, accessories..."
                ),
                key="original_item_details",
            )

            if st.button(
                "✨ Generate my listing",
                type="primary",
                disabled=client is None,
            ):
                prompt = f"""
You draft accurate second-hand marketplace listings.

Analyze the uploaded product photo and the seller-provided details.

Seller-selected category: {item_category}
Seller-reported condition: {condition}
Seller-provided details: {extra_details or "None provided"}

Return exactly these six sections using the headings shown:

### 1. Suggested Listing Title
Provide one concise title.

### 2. Draft Description
Write a useful resale listing description.

### 3. Visible Characteristics Supported by the Photo
Describe only reasonably visible characteristics.

### 4. Visible Wear or Damage, If Any
Mention only wear supported by visual evidence.

### 5. Details the Seller Should Verify
List missing information the seller should confirm.

### 6. Uncertainties and Information the Photo Cannot Establish
Explain what cannot be established from the photo.

Accuracy rules:
- Never invent a brand, model, size, material, age, or authenticity.
- Label uncertain product identification as requiring seller verification.
- Never claim authenticity, functionality, or defect-free condition
  based on a photo alone.
- Distinguish visible observations from seller-provided information.
- If uncertain, say "Cannot determine from the provided photo."
- Do not estimate a price.
- Keep the title and description concise and practical.
"""

                try:
                    with st.spinner(
                        "Analyzing your photo with Gemini..."
                    ):
                        image_bytes = io.BytesIO()
                        image.save(image_bytes, format="JPEG")

                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=[
                                types.Part.from_bytes(
                                    data=image_bytes.getvalue(),
                                    mime_type="image/jpeg",
                                ),
                                prompt,
                            ],
                        )

                    if not response.text:
                        st.error(
                            "Gemini returned no text. Please try again."
                        )
                    else:
                        # Save the new draft and reset old editor values.
                        st.session_state["listing_draft"] = response.text
                        st.session_state["original_seller_notes"] = (
                            extra_details or ""
                        )

                        for key in (
                            "listing_fields",
                            "seller_title",
                            "seller_description",
                            "seller_details",
                        ):
                            st.session_state.pop(key, None)

                        st.success("Listing draft generated!")

                except Exception as error:
                    error_text = str(error)
                    st.error("We couldn't generate the listing.")

                    if "503" in error_text or "UNAVAILABLE" in error_text:
                        st.warning(
                            "Gemini is temporarily busy. Wait a little "
                            "and try again."
                        )
                    elif (
                        "429" in error_text
                        or "RESOURCE_EXHAUSTED" in error_text
                    ):
                        st.warning(
                            "The API quota or rate limit may have been "
                            "reached. Check your Google AI Studio quota."
                        )
                    elif "401" in error_text or "403" in error_text:
                        st.warning(
                            "Check your API key and model access."
                        )
                    else:
                        st.caption(f"Technical details: {error_text}")

    except (UnidentifiedImageError, OSError):
        st.error("That image could not be opened. Try another JPG or PNG.")

# -------------------- EDITABLE LISTING --------------------

if "listing_draft" in st.session_state:
    st.divider()
    st.markdown("## 📝 Your AI-generated listing")
    st.info(
        "AI suggestions are editable. Verify product details before "
        "publishing. The seller makes the final decision."
    )

    if "listing_fields" not in st.session_state:
        draft = st.session_state.get("listing_draft", "")

        title_match = re.search(
            r"(?:^|\n)\s*(?:###\s*)?1\.\s*Suggested Listing Title\s*\n"
            r"(.*?)(?=\n\s*(?:###\s*)?2\.\s*Draft Description|\Z)",
            draft,
            re.IGNORECASE | re.DOTALL,
        )

        description_match = re.search(
            r"(?:^|\n)\s*(?:###\s*)?2\.\s*Draft Description\s*\n"
            r"(.*?)(?=\n\s*(?:###\s*)?3\.\s*Visible Characteristics|\Z)",
            draft,
            re.IGNORECASE | re.DOTALL,
        )

        extracted_title = (
            title_match.group(1).strip() if title_match else ""
        )
        extracted_description = (
            description_match.group(1).strip()
            if description_match
            else draft
        )

        st.session_state["listing_fields"] = {
            "title": extracted_title,
            "description": extracted_description,
            "details": st.session_state.get(
                "original_seller_notes", ""
            ),
        }

    fields = st.session_state["listing_fields"]

    st.markdown("### ✏️ Listing title")
    title = st.text_input(
        "Edit your title",
        value=fields["title"],
        key="seller_title",
        placeholder="Enter your preferred listing title",
    )

    st.markdown("### 📝 Product description")
    description = st.text_area(
        "Edit your description",
        value=fields["description"],
        key="seller_description",
        height=220,
    )

    st.markdown("### 🔎 Additional details")
    details = st.text_area(
        "Edit item details or verification notes",
        value=fields["details"],
        key="seller_details",
        height=120,
        placeholder=(
            "Add size, defects, condition, accessories, "
            "or details you have verified."
        ),
    )

    final_listing = (
        f"LISTING TITLE\n{title.strip()}\n\n"
        f"DESCRIPTION\n{description.strip()}\n\n"
        f"ADDITIONAL DETAILS\n{details.strip()}\n\n"
        "Note: Verify all product information before publishing.\n"
    )

    st.download_button(
        "⬇️ Download my final listing",
        data=final_listing,
        file_name="mercari_final_listing.txt",
        mime="text/plain",
        width="stretch",
    )

# -------------------- PRICE ESTIMATOR --------------------

st.divider()
st.markdown("## 💰 Comparable-price estimator")
st.write(
    "Enter prices from similar items in the same currency. "
    "Compare items with similar condition and features."
)

price_text = st.text_input(
    "Comparable prices, separated by commas",
    placeholder="For example: 1200, 1500, 1350, 1600",
)

if st.button("Calculate suggested price range"):
    try:
        prices = [
            float(value.strip())
            for value in price_text.split(",")
            if value.strip()
        ]

        if len(prices) < 2:
            st.warning("Enter at least two comparable prices.")
        elif any(not math.isfinite(p) or p <= 0 for p in prices):
            st.error("All prices must be positive, finite numbers.")
        else:
            median_price = statistics.median(prices)
            lower = median_price * 0.90
            upper = median_price * 1.10

            symbols = {
                "INR (₹)": "₹",
                "USD ($)": "$",
                "JPY (¥)": "¥",
                "MYR (RM)": "RM ",
            }
            symbol = symbols[currency]

            st.metric(
                "Median comparable price",
                f"{symbol}{median_price:,.2f}",
            )

            st.success(
                f"Illustrative suggested range: "
                f"{symbol}{lower:,.2f} – {symbol}{upper:,.2f}"
            )

            st.caption(
                "This estimate uses only the prices you entered. "
                "It is not live marketplace research or a guaranteed "
                "selling price. The ±10% range is a prototype assumption."
            )

    except ValueError:
        st.error(
            "Enter numbers separated by commas, without currency symbols."
        )

st.caption(
    "Mercari Listing Copilot — AI-assisted drafting prototype. "
    "Seller verification is required."
)
