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

# Clean Inline Inputs
st.markdown("### Configuration & Topic Selection")
c_col1, c_col2, c_col3 = st.columns(3, gap="medium")

with c_col1:
    category_names = list(ig_master_data.keys())
    selected_category = st.selectbox("Category", category_names)

with c_col2:
    writing_tone = st.selectbox("Writing Tone", ["Professional & Empathetic", "Conversational & Human", "Thought Leadership"])

with c_col3:
    emoji_level = st.selectbox("Emoji Level", ["Balanced", "Minimal", "High"])

p_col1, p_col2 = st.columns(2, gap="medium")

with p_col1:
    platforms = st.multiselect(
        "Target Platforms",
        ["LinkedIn", "Facebook", "Instagram"],
        default=["LinkedIn", "Facebook", "Instagram"]
    )

with p_col2:
    category_articles = ig_master_data[selected_category]["articles"]
    
    # Map title to exact article dictionary to prevent index mixing
    article_dict = {art["title"]: art for art in category_articles}
    article_titles = list(article_dict.keys())

    selected_article_title = st.selectbox("Official Article Topic", article_titles)
    
    # Exact lookup based on selected title
    selected_article_obj = article_dict.get(selected_article_title, {"title": selected_article_title, "url": ig_master_data[selected_category]["url"]})
    exact_source_url = selected_article_obj["url"]

random_seed = random.randint(1, 100)

st.markdown("---")

# Helper function to extract individual platform content cleanly
def extract_platform_content(full_text, platform_name):
    lines = full_text.split('\n')
    extracted = []
    recording = False
    
    for line in lines:
        clean_line = line.strip()
        if f"### {platform_name}" in clean_line or f"**{platform_name}**" in clean_line or f"[{platform_name}]" in clean_line:
            recording = True
            continue
        elif recording and clean_line.startswith("### "):
            break
        elif recording:
            extracted.append(line)
            
    result = "\n".join(extracted).strip()
    return result if result else full_text

# Generation Trigger
if st.button("Generate Campaign", type="primary"):
    if not OPENROUTER_API_KEY:
        st.error("API Key missing! Please configure your OpenRouter API Key in environment variables.")
    elif not platforms:
        st.warning("Please select at least one social media platform.")
    else:
        try:
            with st.spinner(f"Scraping '{selected_article_title}' and crafting professional posts..."):
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
                        
                        og_img = soup.find('meta', property='og:image')
                        if og_img and og_img.get('content'):
                            banner_image_url = og_img['content']
                        else:
                            g_img = soup.find('img')
                            if g_img and g_img.get('src'):
                                src = g_img['src']
                                banner_image_url = src if src.startswith('http') else f"https://www.ig.ca{src}"
                except Exception:
                    pass

                if not article_text.strip():
                    article_text = f"Official IG Insights article titled '{selected_article_title}' under {selected_category} category."

                prompt = f"""
                You are an expert human financial advisor writing directly to clients on social media.
                Write unique, highly engaging, natural-sounding social media posts specifically for these requested platforms: {', '.join(platforms)}.
                
                Official Source Article Title: {selected_article_title}
                Source Context: {article_text[:2500]}
                Tone: {writing_tone}
                Emoji Usage: {emoji_level}
                Variation Seed: {random_seed}
                
                STRICT RULES:
                - Write like a real human expert sharing insights with depth and empathy based strictly on the article title '{selected_article_title}'. Absolutely no robotic AI phrases.
                - DO NOT include ANY links, URLs, or markdown links inside the post text.
                - DO NOT include ANY Call to Action (CTA) like "Click here", "Call me", or "Visit our website".
                - Add clean, relevant financial/lifestyle hashtags at the very bottom of each post.
                - Use clear paragraph spacing and bullet points where helpful.
                - You MUST separate each platform's content clearly using exact headers:
                ### LinkedIn
                [LinkedIn Post Content]
                ### Facebook
                [Facebook Post Content]
                ### Instagram
                [Instagram Post Content]
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

                    st.success("Campaign generated successfully.")
                    
                    # Source Reference Card
                    with st.container(border=True):
                        st.markdown("### Official Source Reference")
                        st.markdown(f"**Source Article:** [{selected_article_title}]({exact_source_url})")
                        if banner_image_url:
                            st.image(banner_image_url, width=300, caption="IG Banner Asset")

                    st.markdown("### Generated Platform Content")
                    
                    # Render Separate Tabs per Platform inside Clean Native Bordered Containers
                    tabs = st.tabs([f"{p}" for p in platforms])
                    
                    for i, plat in enumerate(platforms):
                        with tabs[i]:
                            plat_content = extract_platform_content(generated_output, plat)
                            
                            with st.container(border=True):
                                st.markdown(f"#### {plat} Professional Post")
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
