import streamlit as st
import streamlit.components.v1 as components
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

# Exact verbatim clipboard copy button component
def render_exact_copy_button(text_to_copy, button_key):
    safe_json_text = json.dumps(text_to_copy)
    html_code = f"""
    <div style="display: flex; align-items: center; gap: 10px; margin: 6px 0;">
        <button id="btn_{button_key}" onclick="copyExact_{button_key}()" style="
            background-color: #0f172a;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            height: 44px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            transition: background-color 0.2s ease;
        ">Copy Exact Content</button>
    </div>
    <script>
        function copyExact_{button_key}() {{
            const exactText = {safe_json_text};
            const btn = document.getElementById("btn_{button_key}");
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(exactText).then(() => {{
                    const prev = btn.innerText;
                    btn.innerText = "Copied Exact Content";
                    btn.style.backgroundColor = "#15803d";
                    setTimeout(() => {{
                        btn.innerText = prev;
                        btn.style.backgroundColor = "#0f172a";
                    }}, 1800);
                }}).catch(() => {{
                    fallbackCopy_{button_key}(exactText, btn);
                }});
            }} else {{
                fallbackCopy_{button_key}(exactText, btn);
            }}
        }}
        function fallbackCopy_{button_key}(text, btn) {{
            const ta = document.createElement("textarea");
            ta.value = text;
            ta.setAttribute("readonly", "");
            ta.style.position = "fixed";
            ta.style.opacity = "0";
            document.body.appendChild(ta);
            ta.select();
            try {{
                document.execCommand("copy");
                const prev = btn.innerText;
                btn.innerText = "Copied Exact Content";
                btn.style.backgroundColor = "#15803d";
                setTimeout(() => {{
                    btn.innerText = prev;
                    btn.style.backgroundColor = "#0f172a";
                }}, 1800);
            }} catch (e) {{
                btn.innerText = "Copy Failed";
            }}
            document.body.removeChild(ta);
        }}
    </script>
    """
    components.html(html_code, height=58)

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

# Clean Inline Inputs
st.markdown("### Configuration & Topic Selection")
c_col1, c_col2 = st.columns(2, gap="medium")

with c_col1:
    category_names = list(ig_master_data.keys())
    selected_category = st.selectbox("Category", category_names)

with c_col2:
    writing_tone = st.selectbox(
        "Writing Tone",
        [
            "Advisor Speaking",
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

# Ensure first line is standalone hook/question, followed by newline before body
def format_hook_first_line(text):
    cleaned = text.strip()
    if not cleaned:
        return cleaned

    lines = [ln.strip() for ln in cleaned.split("\n") if ln.strip()]
    if len(lines) >= 2:
        first_line = lines[0]
        rest_body = "\n\n".join(lines[1:])
        return f"{first_line}\n\n{rest_body}"

    for sep in ["?", "!", "."]:
        if sep in cleaned:
            idx = cleaned.find(sep) + 1
            hook = cleaned[:idx].strip()
            body = cleaned[idx:].strip()
            if hook and body:
                return f"{hook}\n\n{body}"

    return cleaned

# Enforce strict <= 100 char limit for TikTok and Twitter while keeping complete thoughts
def enforce_short_platform_limit(text, max_chars=100):
    cleaned = " ".join(text.split()).strip()
    if len(cleaned) <= max_chars:
        return cleaned

    truncated = cleaned[:max_chars]
    if " " in truncated:
        candidate = truncated.rsplit(" ", 1)[0].strip()
        if candidate:
            return candidate
    return truncated.strip()

# Generation Trigger with button label "Create Content"
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
                        article_text = "\n\n".join([p.get_text(" ", strip=True) for p in paragraphs if p.get_text(strip=True)])
                        banner_image_url = find_clean_plain_image(soup)
                except Exception:
                    pass

                if not article_text.strip():
                    article_text = f"Official IG Insights article titled '{selected_article_title}' under {selected_category} category."

                tone_map = {
                    "Advisor Speaking": (
                        "Speak directly like a real financial advisor giving a live talk or sitting across the table with a client. "
                        "Use natural spoken cadence, clear guidance, real-world perspective, and warm authority while staying grounded in the source article."
                    ),
                    "Hook & Question Driven": (
                        "Open with a compelling question or hook on line 1 to pull the reader into the full piece, "
                        "followed on a new line by a natural, human-sounding breakdown of the article's core points."
                    ),
                    "Professional & Empathetic": (
                        "Write with calm expertise and genuine empathy for everyday financial decisions, using clear human prose."
                    ),
                    "Conversational & Human": (
                        "Write as a thoughtful, relatable human sharing practical insights naturally without stiff jargon."
                    ),
                    "Thought Leadership": (
                        "Write with clear strategic perspective and nuanced insights drawn directly from the source article."
                    )
                }

                tone_guidance = tone_map.get(writing_tone, tone_map["Advisor Speaking"])

                prompt = f"""
                You are an experienced human financial advisor creating social media content based strictly on the original source article below.
                Requested platforms: {', '.join(platforms)}.

                Official Source Article Title: {selected_article_title}
                Original Article Content:
                {article_text[:4500]}

                Selected Writing Tone: {writing_tone}
                Tone Instructions: {tone_guidance}
                Variation Seed: {random_seed}

                MANDATORY RULES FOR EVERY RESPONSE:
                1. ZERO EMOJIS anywhere in any platform's post. Never use emojis or pictographs.
                2. Line 1 MUST be a standalone hook or thought-provoking question based on the source article—challenging a common assumption or touching a real personal/financial decision without giving away the full answer on line 1.
                3. Avoid generic yes/no questions like "Do you know..." or robotic openers like "In today's fast-paced world...". Make line 1 specific, sharp, and human.
                4. Keep line 1 strictly by itself with NO body text on line 1, followed by a blank newline before the body starts on the next line.
                5. Sound 100% like a real human writer—natural phrasing, smooth transitions, zero robotic AI filler.
                6. For LinkedIn, Facebook, and Instagram:
                   - Keep the length substantial and rich like the original article—do NOT shrink it into a brief summary.
                   - Base the main body directly on the facts, ideas, and takeaways in the original article content above.
                   - Include important sub-topics, clear paragraphs, and clean bullet points covering key details from the article so the reader gets full value.
                   - End with relevant hashtags. Do NOT include URLs, links, or pushy sales CTAs.
                7. For TikTok and Twitter:
                   - Complete the entire post—including hook, core takeaway from the original article, and relevant hashtags—strictly within 100 characters or fewer (less than or equal to 100 characters).
                   - Keep it crisp, complete, and directly tied to the original article.
                8. Separate each requested platform clearly using exact markdown headings:
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
                    "max_tokens": 4000
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
                    timeout=45
                )

                if api_response.status_code == 200:
                    res_data = api_response.json()
                    generated_output = res_data['choices'][0]['message']['content']

                    st.success("Content created successfully.")
                    
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
                            else:
                                plat_content = format_hook_first_line(plat_content)
                            
                            with st.container(border=True):
                                st.markdown(f"#### {plat} Post")
                                if plat in ["TikTok", "Twitter"]:
                                    st.caption(f"Character count: {len(plat_content)} / 100")
                                st.divider()
                                st.markdown(plat_content)
                            
                            # Exact verbatim copy button + download + quick raw view
                            render_exact_copy_button(plat_content, f"{plat}_{i}_{random_seed}")

                            col_dl, col_cp = st.columns([1, 2])
                            with col_dl:
                                st.download_button(
                                    label=f"Download {plat} (.txt)",
                                    data=plat_content,
                                    file_name=f"IG_{plat}_{selected_category.replace(' ', '_')}.txt",
                                    mime="text/plain",
                                    key=f"dl_{plat}_{i}_{random_seed}"
                                )
                            with col_cp:
                                with st.expander("Exact Raw Text View"):
                                    st.text(plat_content)
                else:
                    st.error(f"API Error ({api_response.status_code}): {api_response.text}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
