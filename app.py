import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import concurrent.futures

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

# Fonction pour vérifier et compléter l'URL
def get_complete_url(name):
    try:
        query = f"{name} site official website"
        url = search_bing(query)
        
        # Si l'URL contient le nom de l'organisation, elle est probablement correcte
        if name.lower() in url.lower():
            return url
        else:
            return f"Error: Invalid URL {url}"
    except Exception as e:
        return f"Error: {str(e)}"

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

        progress_bar = st.progress(0)
        progress_text = st.empty()

        def update_progress(current, total):
            progress_percentage = int((current / total) * 100)
            progress_bar.progress(progress_percentage)
            progress_text.text(f"Progress: {current}/{total}")

        if function_choice == 'Import to Affinity':
            total_rows = len(df)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_url = {executor.submit(get_complete_url, row[0]): idx for idx, row in df.iterrows()}
                for i, future in enumerate(concurrent.futures.as_completed(future_to_url)):
                    idx = future_to_url[future]
                    try:
                        url = future.result()
                        df.at[idx, 'URL'] = url
                    except Exception as exc:
                        df.at[idx, 'URL'] = f"Error: {str(exc)}"
                    update_progress(i + 1, total_rows)
            
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
                total_rows = len(df)
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_to_url = {executor.submit(get_complete_url, row['Website']): idx for idx, row in df.iterrows()}
                    for i, future in enumerate(concurrent.futures.as_completed(future_to_url)):
                        idx = future_to_url[future]
                        try:
                            url = future.result()
                            df.at[idx, 'Complete URL'] = url
                        except Exception as exc:
                            df.at[idx, 'Complete URL'] = f"Error: {str(exc)}"
                        update_progress(i + 1, total_rows)

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