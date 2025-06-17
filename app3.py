import streamlit as st
import pandas as pd
import re

# Model aliases mapping (lowercase keys)
model_aliases = {
    'E46': '3 Series',
    # Add more aliases here as needed
}

@st.cache_data
def load_data():
    file_path = r"Car Database.csv"
    df = pd.read_csv(file_path, encoding='latin1')
    
    def extract_years(text):
        s = str(text)
        start_year = int(s[:4]) if s[:4].isdigit() else None
        end_year = int(s[-4:]) if s[-4:].isdigit() else None
        return pd.Series([start_year, end_year])
    df[['Start Year', 'End Year']] = df['Year'].apply(extract_years)
    
    def get_second_word(text):
        try:
            words = str(text).split()
            return words[1] if len(words) > 1 else None
        except:
            return None
    df['Variant_Second_Word'] = df['Variant'].apply(get_second_word)

    def extract_after_first_space(text):
        s = str(text)
        return s.split(' ', 1)[1] if ' ' in s else ''
    df['Variants'] = df['Variant'].apply(extract_after_first_space)

    return df

def find_phrase_keywords(text, keywords):
    text_lower = text.lower()
    matches = []
    for kw in keywords:
        if kw.lower() in text_lower:
            matches.append(kw)
    return matches

def map_alias_to_model(text, aliases):
    text_lower = text.lower()
    matched_models = []
    for alias, model in aliases.items():
        if alias in text_lower:
            matched_models.append(model)
    return matched_models

def extract_years(text):
    matches = re.findall(r'(\d{2,4})-(\d{2,4})', text)
    if matches:
        start, end = matches[0]
        start_year = int(start) + (2000 if len(start) == 2 else 0)
        end_year = int(end) + (2000 if len(end) == 2 else 0)
        return start_year, end_year
    return None, None

def format_list_for_display(lst):
    return ", ".join(lst) if lst else "None"

def main():
    st.title("Car Compatibility Search")

    df = load_data()

    unique_makes = sorted(df['Make'].dropna().unique())
    unique_models = sorted(df['Model'].dropna().unique())
    unique_variants = sorted(df['Variant_Second_Word'].dropna().unique())

    search_text = st.text_input("Paste your search string here:")

    if search_text:
        start_year, end_year = extract_years(search_text)
        matched_makes = find_phrase_keywords(search_text, unique_makes)
        alias_matched_models = map_alias_to_model(search_text, model_aliases)
        exact_matched_models = find_phrase_keywords(search_text, unique_models)
        matched_models = list(set(alias_matched_models + exact_matched_models))
        matched_variants = find_phrase_keywords(search_text, unique_variants)

        st.write(f"Detected Start Year: {start_year if start_year else 'None'}, End Year: {end_year if end_year else 'None'}")
        st.write(f"Matched Makes: {format_list_for_display(matched_makes)}")
        st.write(f"Matched Models: {format_list_for_display(matched_models)}")
        st.write(f"Matched Variants: {format_list_for_display(matched_variants)}")

        # Year dropdown if range detected
        selected_year = None
        if start_year and end_year:
            year_options = list(range(start_year, end_year + 1))
            selected_year = st.selectbox("Select a specific year (optional):", options=[""] + year_options)

        # Make dropdown if multiple makes found
        if matched_makes:
            selected_make = st.selectbox("Select make:", options=matched_makes)
        else:
            selected_make = None

        # Model dropdown if multiple models found
        if matched_models:
            selected_model = st.selectbox("Select model:", options=matched_models)
        else:
            selected_model = None

        filtered = df.copy()

        if selected_year:
            filtered = filtered[(filtered['Start Year'] <= int(selected_year)) & (filtered['End Year'] >= int(selected_year))]
        elif start_year and end_year:
            filtered = filtered[(filtered['Start Year'] <= end_year) & (filtered['End Year'] >= start_year)]

        if selected_make:
            filtered = filtered[filtered['Make'] == selected_make]

        if selected_model:
            filtered = filtered[filtered['Model'] == selected_model]

        if matched_variants:
            filtered = filtered[filtered['Variant_Second_Word'].isin(matched_variants)]

        st.write(f"Found {len(filtered)} compatible ktypes:")

        if not filtered.empty:
            ktypes_list = filtered['K-Type'].astype(str).tolist()
            st.text_area("Compatible K-Types (copy from here):", value="\n".join(ktypes_list), height=200)
        else:
            st.write("No compatible ktypes found.")

if __name__ == "__main__":
    main()
