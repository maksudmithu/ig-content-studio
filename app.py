import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import random
import os

# Page Configuration
st.set_page_config(
    page_title="IG Advisor | Professional Content Studio",
    page_icon="🛡️",
    layout="wide"
)

# Custom Minimalist & Professional Corporate UI Styling
st.markdown("""
    <style>
    .main { background-color: #f8fafc; color: #1e293b; }
    
    .hero-container {
        padding: 2rem 1.5rem;
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .hero-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }
    .hero-subtitle {
        color: #64748b;
        font-size: 0.95rem;
    }

    /* Primary Action Button */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        height: 44px;
        background-color: #0f172a;
        color: white;
        border: none;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #334155;
    }

    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: #475569;
        font-weight: 500;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# Hero Header
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">IG Advisor Content Studio</div>
        <div class="hero-subtitle">Generate professional, human-crafted social media campaigns from official IG Insights.</div>
    </div>
""", unsafe_allow_html=True)

# Secure API Key Loading
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_API_KEY:
    try:
        OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    except Exception:
        pass

# Helper to pick clean image without logo/branding keywords
def find_clean_plain_image(soup, base_url="https://www.ig.ca"):
    blocked_keywords = [
        "logo", "brand", "icon", "sprite", "avatar", "favicon",
        "header", "footer", "badge", "button", "arrow", "ig-logo", "investors-group"
    ]
    candidates = []

    for img in soup.find_all("img"):
        src = (img.get("src") or img.get("data-src") or "").strip()
        alt = (img.get("alt") or "").lower()
        cls = " ".join(img.get("class") or []).lower()

        if not src or src.startswith("data:") or ".svg" in src.lower():
            continue

        full_src = src if src.startswith("http") else f"{base_url}{src if src.startswith('/') else '/' + src}"
        combined_check = f"{full_src.lower()} {alt} {cls}"

        if any(bad in combined_check for bad in blocked_keywords):
            continue

        # Prefer larger/editorial article images
        width_attr = img.get("width")
        height_attr = img.get("height")
        score = 0
        try:
            if width_attr and int(str(width_attr).replace("px", "")) >= 300:
                score += 2
            if height_attr and int(str(height_attr).replace("px", "")) >= 200:
                score += 2
        except Exception:
            pass

        if any(good in full_src.lower() for good in ["insight", "article", "editorial", "hero", "banner", "media", "content"]):
            score += 3

        candidates.append((score, full_src))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    og_img = soup.find("meta", property="og:image")
    if og_img and og_img.get("content"):
        og_url = og_img["content"].strip()
        if not any(bad in og_url.lower() for bad in blocked_keywords):
            return og_url

    return ""

# Dynamic Scraper for Categories and Articles
@st.cache_data(ttl=600)
def fetch_fully_dynamic_ig_data():
    base_category_links = [
        "https://www.ig.ca/en/insights/your-financial-life/tax",
        "https://www.ig.ca/en/insights/your-financial-life/business-owner",
        "https://www.ig.ca/en/insights/your-financial-life/mortgages-and-loans",
        "https://www.ig.ca/en/insights/your-financial-life/estate-planning",
        "https://www.ig.ca/en/insights/your-financial-life/investing",
        "https://www.ig.ca/en/insights/your-financial-life/value-of-advice",
        "https://www.ig.ca/en/insights/your-financial-life/retirement"
    ]
    
    dynamic_data = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    
    for cat_url in base_category_links:
        try:
            parts = cat_url.split('/')
            cat_name = parts[-1].replace('-', ' ').title()
            dynamic_data[cat_name] = {"url": cat_url, "articles": []}
            
            resp = requests.get(cat_url, headers=headers, timeout=6)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                seen_titles = set()
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    title = a_tag.get_text().strip()
                    if '/insights/' in href and len(title) > 15:
                        full_url = href if href.startswith('http') else f"https://www.ig.ca{href}"
                        if title not in seen_titles:
                            seen_titles.add(title)
                            dynamic_data[cat_name]["articles"].append({"title": title, "url": full_url})
        except Exception:
            continue
            
    fallback_data = {
        "Tax": {
            "url": "https://www.ig.ca/en/insights/your-financial-life/tax",
            "articles": [
                {"title": "Why it's better not to get a tax refund", "url": "https://www.ig.ca/en/insights/tax/why-its-better-not-to-get-a-tax-refund"},
                {"title": "Tax on rental income", "url": "https://www.ig.ca/en/insights/tax/tax-on-rental-income"},
                {"title": "Tax-Loss Selling: Opportunities when you have unrealized capital losses", "url": "https://www.ig.ca/en/insights/tax/tax-loss-selling"},
                {"title": "What is income splitting in Canada? And how can it reduce your tax?", "url": "https://www.ig.ca/en/insights/tax/what-is-income-splitting-in-canada"}
            ]
        },
        "Business Owner": {
            "url": "https://www.ig.ca/en/insights/your-financial-life/business-owner",
            "articles": [
                {"title": "Succession planning for Canadian business owners", "url": "https://www.ig.ca/en/insights/business-owner/succession-planning"},
                {"title": "Tax-efficient ways to withdraw money from your corporation", "url": "https://www.ig.ca/en/insights/business-owner/withdraw-money-corporation"}
            ]
        },
        "Mortgages And Loans": {
            "url": "https://www.ig.ca/en/insights/your-financial-life/mortgages-and-loans",
            "articles": [
                {"title": "Fixed vs. variable rate mortgages in Canada", "url": "https://www.ig.ca/en/insights/mortgages-and-loans/fixed-vs-variable"},
                {"title": "Strategies to pay off your mortgage faster", "url": "https://www.ig.ca/en/insights/mortgages-and-loans/pay-off-mortgage-faster"}
            ]
        },
        "Value Of Advice": {
            "url": "https://www.ig.ca/en/insights/your-financial-life/value-of-advice",
            "articles": [
                {"title": "How holistic financial planning builds long-term confidence", "url": "https://www.ig.ca/en/insights/value-of-advice/holistic-financial-planning"},
                {"title": "Why working with a financial advisor improves wealth outcomes", "url": "https://www.ig.ca/en/insights/value-of-advice/improves-wealth-outcomes"}
            ]
        },
        "Investing": {
            "url": "https://www.ig.ca/en/insights/your-financial-life/investing",
            "articles": [
                {"title": "What are private investments and how do they work?", "url": "https://www.ig.ca/en/insights/investing/what-are-private-investments-and-how-do-they-work"},
                {"title": "RDSP mistakes to avoid", "url": "https://www.ig.ca/en/insights/investing/rdsp-mistakes-to-avoid"},
                {"title": "Is saving for your child's education still worth it? The research says yes", "url": "https://www.ig.ca/en/insights/investing/is-saving-for-your-childs-education-still-worth-it"},
                {"title": "How long does it take stock markets to recover from a downturn?", "url": "https://www.ig.ca/en/insights/investing/how-long-does-it-take-stock-markets-to-recover-from-a-downturn"}
            ]
        },
        "Estate Planning": {
            "url": "https://www.ig.ca/en/insights/your-financial-life/estate-planning",
            "articles": [
                {"title": "What is estate planning?", "url": "https://www.ig.ca/en/insights/estate-planning/what-is-estate-planning"},
                {"title": "How to prevent your will from being contested", "url": "https://www.ig.ca/en/insights/estate-planning/how-to-prevent-your-will-from-being-contested"},
                {"title": "What happens if you die without a will in Canada?", "url": "https://www.ig.ca/en/insights/estate-planning/what-happens-if-you-die-without-a-will-in-canada"}
            ]
        },
        "Retirement": {
            "url": "https://www.ig.ca/en/insights/your-financial-life/retirement",
            "articles": [
                {"title": "Retirees: what do you do when you have enough?", "url": "https://www.ig.ca/en/insights/retirement/retirees-what-do-you-do-when-you-have-enough"},
                {"title": "Navigating retirement income milestones in Canada", "url": "https://www.ig.ca/en/insights/retirement/milestones"},
                {"title": "How to bridge the financial gap before pension starts", "url": "https://www.ig.ca/en/insights/retirement/bridge-gap"}
            ]
        }
    }
    
    for k, v in fallback_data.items():
        if k not in dynamic_data or len(dynamic_data[k]["articles"]) < 2:
            dynamic_data[k] = v
            
    return dynamic_data

ig_master_data = fetch_fully_dynamic_ig_data()

# Clean Inline Inputs (Emoji Level removed)
st.markdown("### Configuration & Topic Selection")
c_col1, c_col2 = st.columns(2, gap="medium")

with c_col1:
    category_names = list(ig_master_data.keys())
    selected_category = st.selectbox("Category", category_names)

with c_col2:
    writing_tone = st.selectbox(
        "Writing Tone",
        [
            "Hook & Question Driven",
            "Professional & Empathetic",
            "Conversational & Human",
            "Thought Leadership"
        ]
    )

p_col1, p_col2 = st.columns(2, gap="medium")

with p_col1:
    platforms = st.multiselect(
        "Target Platforms",
        ["LinkedIn", "Facebook", "Instagram", "TikTok", "Twitter"],
        default=["LinkedIn", "Facebook", "Instagram", "TikTok", "Twitter"]
    )

with p_col2:
    category_articles = ig_master_data[selected_category]["articles"]
    article_dict = {art["title"]: art for art in category_articles}
    article_titles = list(article_dict.keys())

    selected_article_title = st.selectbox("Official Article Topic", article_titles)
    selected_article_obj = article_dict.get(
        selected_article_title,
        {"title": selected_article_title, "url": ig_master_data[selected_category]["url"]}
    )
    exact_source_url = selected_article_obj["url"]

random_seed = random.randint(1, 100)

st.markdown("---")

# Helper function to extract individual platform content cleanly
def extract_platform_content(full_text, platform_name):
    lines = full_text.split('\n')
    extracted = []
    recording = False
    known_headers = ["### LinkedIn", "### Facebook", "### Instagram", "### TikTok", "### Twitter"]

    for line in lines:
        clean_line = line.strip()
        if clean_line.lower() == f"### {platform_name}".lower() or clean_line.lower() == f"**{platform_name}**".lower() or clean_line.lower() == f"[{platform_name}]".lower():
            recording = True
            continue
        elif recording and any(clean_line.lower().startswith(h.lower()) for h in known_headers):
            break
        elif recording:
            extracted.append(line)

    result = "\n".join(extracted).strip()
    return result if result else full_text

# Enforce strict <= 100 char limit for TikTok and Twitter
def enforce_short_platform_limit(text, max_chars=100):
    cleaned = " ".join(text.split()).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars].rstrip()

# Generation Trigger with updated button label "Create Content"
if st.button("Create Content", type="primary"):
    if not OPENROUTER_API_KEY:
        st.error("API Key missing! Please configure your OpenRouter API Key in environment variables.")
    elif not platforms:
        st.warning("Please select at least one social media platform.")
    else:
        try:
            with st.spinner(f"Processing '{selected_article_title}' and crafting human posts..."):
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                }
                article_text = ""
                banner_image_url = ""
                
                try:
                    resp = requests.get(exact_source_url, headers=headers, timeout=8)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        paragraphs = soup.find_all('p')
                        article_text = " ".join([p.text for p in paragraphs])
                        banner_image_url = find_clean_plain_image(soup)
                except Exception:
                    pass

                if not article_text.strip():
                    article_text = f"Official IG Insights article titled '{selected_article_title}' under {selected_category} category."

                tone_instruction = (
                    "Start every post with a compelling hook and a thought-provoking question that pulls the reader into the rest of the post. Sound 100% like a real human advisor."
                    if writing_tone == "Hook & Question Driven"
                    else f"Write in a {writing_tone} tone that sounds genuinely human, natural, and relatable."
                )

                prompt = f"""
                You are an experienced human financial advisor writing directly to everyday readers on social media.
                Create posts strictly for these platforms: {', '.join(platforms)}.

                Official Source Article Title: {selected_article_title}
                Source Context: {article_text[:2500]}
                Tone Style: {writing_tone}
                Tone Guidance: {tone_instruction}
                Variation Seed: {random_seed}

                STRICT RULES:
                1. ZERO EMOJIS anywhere in any post. Do not use any emoji characters or pictographs.
                2. Write like a real human expert with natural rhythm, empathy, and clarity. Avoid robotic AI cliches.
                3. For LinkedIn, Facebook, and Instagram: write engaging, well-spaced posts with clean relevant hashtags at the bottom. Do NOT include URLs, links, or pushy sales CTAs.
                4. For TikTok and Twitter: the ENTIRE post including hashtags MUST be strictly 100 characters or fewer (<= 100 characters). Include a sharp hook/question and relevant hashtags while staying strictly under 100 characters total.
                5. Separate each requested platform clearly using exact markdown headings:
                ### LinkedIn
                [content]
                ### Facebook
                [content]
                ### Instagram
                [content]
                ### TikTok
                [content]
                ### Twitter
                [content]
                """

                payload = {
                    "model": "google/gemini-2.5-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2500
                }

                api_response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://ig-content-studio.onrender.com",
                        "X-Title": "IG Advisor Content Studio"
                    },
                    data=json.dumps(payload),
                    timeout=30
                )

                if api_response.status_code == 200:
                    res_data = api_response.json()
                    generated_output = res_data['choices'][0]['message']['content']

                    st.success("Content created successfully.")
                    
                    # Source Reference Card
                    with st.container(border=True):
                        st.markdown("### Official Source Reference")
                        st.markdown(f"**Source Article:** [{selected_article_title}]({exact_source_url})")
                        if banner_image_url:
                            st.image(banner_image_url, width=300, caption="Clean Article Visual")

                    st.markdown("### Generated Platform Content")
                    
                    tabs = st.tabs([f"{p}" for p in platforms])
                    
                    for i, plat in enumerate(platforms):
                        with tabs[i]:
                            plat_content = extract_platform_content(generated_output, plat)
                            if plat in ["TikTok", "Twitter"]:
                                plat_content = enforce_short_platform_limit(plat_content, max_chars=100)
                            
                            with st.container(border=True):
                                st.markdown(f"#### {plat} Post")
                                if plat in ["TikTok", "Twitter"]:
                                    st.caption(f"Character count: {len(plat_content)} / 100")
                                st.divider()
                                st.markdown(plat_content)
                            
                            col_dl, col_cp = st.columns([1, 2])
                            with col_dl:
                                st.download_button(
                                    label=f"Download {plat} (.txt)",
                                    data=plat_content,
                                    file_name=f"IG_{plat}_{selected_category.replace(' ', '_')}.txt",
                                    mime="text/plain",
                                    key=f"dl_{plat}"
                                )
                            with col_cp:
                                with st.expander("Quick Copy View"):
                                    st.code(plat_content, language="text")
                else:
                    st.error(f"API Error ({api_response.status_code}): {api_response.text}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
