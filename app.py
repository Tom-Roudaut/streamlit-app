import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from googlesearch import search

# Fonction pour nettoyer l'URL
def clean_url(url):
    if isinstance(url, str):
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        return url.rstrip('/')
    return url

# Fonction pour interroger Bing
def search_bing(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(f"https://www.bing.com/search?q={query}", headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all('li', {'class': 'b_algo'})
        if results:
            return results[0].find('a')['href']
    except Exception as e:
        return f"Error: {str(e)}"

# Fonction pour compléter l'URL
def get_complete_url(simplified_url):
    full_url = clean_url(simplified_url)
    query = f"{simplified_url}"

    # Essayez Bing
    url = search_bing(query)
    if url and "Error" not in url:
        return url

    # Si Bing échoue, retournez l'URL simplifiée
    return full_url

# Fonction principale pour Streamlit
def main():
    st.title('URL Finder for Investment Funds and Start-ups')
    st.write("Upload an Excel file with company names in the first column to retrieve their official websites.")

    # Choix de la fonction
    function_choice = st.radio(
        "Choose the function you want to use:",
        ('Import to Affinity', 'Import Pitchbook')
    )

    # Téléchargement du fichier
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write("File uploaded successfully. Here are the first few rows:")
        st.write(df.head())

        total_urls = len(df)
        progress_bar = st.progress(0)
        progress_value = 0

        # Mise à jour de la barre de progression
        def update_progress_bar(current_value, total_value):
            progress = current_value / total_value
            progress_bar.progress(progress)

        if function_choice == 'Import to Affinity':
            urls = []
            for i, row in df.iterrows():
                url = get_complete_url(row[0])
                urls.append(url)
                progress_value += 1
                update_progress_bar(progress_value, total_urls)

            df['URL'] = urls
            df['URL'] = df['URL'].apply(clean_url)
            df.columns = ['Organization Name', 'Organization Website']
            st.write("URLs have been fetched. Here are the first few results:")
            st.write(df.head())
            output_file = 'output_with_urls.csv'
            df.to_csv(output_file, index=False, sep=',')
            with open(output_file, "rb") as file:
                btn = st.download_button(
                    label="Download updated CSV file",
                    data=file,
                    file_name=output_file,
                    mime="text/csv"
                )

        elif function_choice == 'Import Pitchbook':
            if 'Website' in df.columns:
                urls = []
                for i, row in df.iterrows():
                    url = get_complete_url(row['Website'])
                    urls.append(url)
                    progress_value += 1
                    update_progress_bar(progress_value, total_urls)

                df['Complete URL'] = urls
                st.write("Completing URLs for each simplified URL...")
                st.write(df.head())
                output_file = 'completed_urls.csv'
                df.to_csv(output_file, index=False, sep=',')
                with open(output_file, "rb") as file:
                    btn = st.download_button(
                        label="Download completed URLs CSV file",
                        data=file,
                        file_name=output_file,
                        mime="text/csv"
                    )
            else:
                st.error("The uploaded file does not contain a second column with URLs.")

if __name__ == '__main__':
    main()
