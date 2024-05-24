import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Mapping of Turkish month names to month numbers
turkish_months = {
    "Ocak": "01",
    "Şubat": "02",
    "Mart": "03",
    "Nisan": "04",
    "Mayıs": "05",
    "Haziran": "06",
    "Temmuz": "07",
    "Ağustos": "08",
    "Eylül": "09",
    "Ekim": "10",
    "Kasım": "11",
    "Aralık": "12"
}
# Function to convert date from Turkish to yyyy-mm-dd format
def convert_turkish_date(turkish_date):
    # Split the date string
    day, month, year = turkish_date.split()
    
    # Get the month number from the dictionary
    month_number = turkish_months[month]
    
    # Format the date in yyyy-mm-dd
    formatted_date = f"{year}-{month_number}-{day.zfill(2)}"
    
    return formatted_date

# Function to fetch and parse the web page
def fetch_columns(url):
    print(f"Fetching columns from {url}")
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

# Function to extract article links
def get_article_links(soup, url, simple_name, media):
    links = []
    url_chunks = url.split("/")
    url_chunks = [chunk for chunk in url_chunks if chunk]

    # Updated CSS selector for article links
    if media == "cumhuriyet" or media == "t24":
        for article in soup.find_all('a', href=True):
            href = article.get('href')
            if f'{"/".join(url_chunks[2:])}/' in href:
                full_link = "//".join(url_chunks[:2]) + href
                if full_link not in links:
                    links.append(full_link)
        print(f"Found {len(links)} articles")
        return links[:30]  # Return latest 30 links
    elif media == "ekonomim":
        for article in soup.find_all('a', href=True):
            href = article.get('href')
            if f'/kose-yazisi/' in href:
                full_link = href
                if full_link not in links:
                    links.append(full_link)
        print(f"Found {len(links)} articles")
        return links[:30]  # Return latest 30 links

# Function to extract article content
def get_article_content(url,media):
    print(f"Fetching article content from {url}")
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    # Media: www.cumhuriyet.com.tr
    if media == "cumhuriyet":
        # Extract title
        title_tag = soup.find('h1', class_='baslik')
        if title_tag:
            title = title_tag.text.strip()
        else:
            print(f"Title not found for {url}")
            return None, None, None
        
        # Extract publishing date
        date_tag = soup.find('meta', {'name': 'dateModified'})
        if date_tag and 'content' in date_tag.attrs:
            publishing_date = date_tag['content']
        else:
            print(f"Publishing date not found for {url}")
            return None, None, None
        
        # Extract main article content
        content_div = soup.find('div', class_='haberMetni')
        if content_div:
            # Find all paragraphs and h3 tags
            paragraphs = content_div.find_all(['p', 'h3'])
            content = ""
            for tag in paragraphs:
                # Check if it's a subheader
                if tag.name == 'h3':
                    # Add subheader with appropriate Markdown formatting
                    content += f"\n### {tag.text.strip()}\n\n"
                else:
                    # Add paragraph content
                    content += f"{tag.text.strip()}\n\n"
        else:
            print(f"Content not found for {url}")
            return None, None, None
    # Media: www.t24.com.tr
    elif media == "t24":
        # Extract publishing date
        date_tag = soup.find('div', class_='_392lz')
        if date_tag:
            # Extract the date text
            date_published = date_tag.get_text(strip=True)
            publishing_date = convert_turkish_date(date_published)
        else:
            print(f"Publishing date not found for {url}")
            return None, None, None
        
        # Extract main article content
        content_div = soup.find('div', class_='_2teaB')
        # Exclude unwanted tags
        unwanted_div = content_div.find('div', class_='_1XNyq')
        if unwanted_div:
            unwanted_div.decompose()
        
        unwanted_div2 = content_div.find('div', class_='_3KaMw')
        if unwanted_div2:
            unwanted_div2.decompose()

        unwanted_div3 = content_div.find('table')
        if unwanted_div3:
            unwanted_div3.decompose()
        
        # Extract title
        title_tag = soup.find('h1')
        if title_tag:
            title = title_tag.text.strip()
        else:
            print(f"Title not found for {url}")
            return None, None, None
        
        if content_div:
            # Find all paragraphs and h3 tags
            paragraphs = content_div.find_all(['span','h3', 'h2'])
            content = ""
            for tag in paragraphs:
                # Check if it's a subheader
                if tag.name == 'h3':
                    # Add subheader with appropriate Markdown formatting
                    content += f"\n### {tag.text.strip()}\n\n"
                elif tag.name == 'h2':
                    # Add subheader with appropriate Markdown formatting
                    content += f"\n### {tag.text.strip()}\n\n"
                else:
                    # Add paragraph content
                    content += f"{tag.text.strip()}\n\n"
        else:
            print(f"Content not found for {url}")
            return None, None, None
    elif media == "ekonomim":
        # Extract title
        title_tag = soup.find('h1')
        if title_tag:
            title = title_tag.text.strip()
        else:
            print(f"Title not found for {url}")
            return None, None, None
        
        # Extract publishing date
        date_tag = soup.find('meta', {'name': 'dateModified'})
        if date_tag and 'content' in date_tag.attrs:
            publishing_date = date_tag['content']
        else:
            print(f"Publishing date not found for {url}")
            return None, None, None
        
        # Extract main article content
        content_div = soup.find('div', class_='content-text')
        if content_div:
            # Find all paragraphs and h3 tags
            paragraphs = content_div.find_all(['p', 'h3'])
            content = ""
            for tag in paragraphs:
                # Check if it's a subheader
                if tag.name == 'h3':
                    # Add subheader with appropriate Markdown formatting
                    content += f"\n### {tag.text.strip()}\n\n"
                else:
                    # Add paragraph content
                    content += f"{tag.text.strip()}\n\n"
        else:
            print(f"Content not found for {url}")
            return None, None, None

    return title, content, publishing_date

# Function to save content to markdown file
def save_article_to_md(output_dir, simple_name, author_name, title, content, publishing_date):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Format filename with publishing date
    filename = os.path.join(output_dir, f"{simple_name}-{publishing_date.split('T')[0]}.md")
    pub_date = f"{publishing_date.split('T')[0]}"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {author_name}\n\n")
        f.write(f"### Yayımlanma tarihi: {pub_date}\n\n")
        f.write(f"# {title}\n\n{content}")
    print(f"Saved article to {filename}")
    return filename, title

# Function to create index file
def create_index_file(output_dir, simple_name, writer, article_files_and_titles):
    index_filename = os.path.join(output_dir, f"index.md")
    with open(index_filename, "w", encoding="utf-8") as index_file:
        index_file.write(f"# {writer}\n\n")
        for article_file, title in article_files_and_titles:
            article_relative_path = os.path.basename(article_file)
            index_file.write(f"- [{title}]({article_relative_path})\n")
    print(f"Index file created at {index_filename}")

# Function to process each columnist
def process_columnist(writer, url, simple_name,media):
    output_dir = os.path.join('articles', simple_name)
    soup = fetch_columns(url)
    article_links = get_article_links(soup, url, simple_name, media)
    article_files_and_titles = []

    for index, link in enumerate(article_links):
        title, content, publishing_date = get_article_content(link,media)
        if title and content and publishing_date:
            filename, article_title = save_article_to_md(output_dir, simple_name, writer, title, content, publishing_date)
            article_files_and_titles.append((filename, article_title))
            print(f"Processed {index + 1}/{len(article_links)}: {title}")
        else:
            print(f"Skipped article {index + 1}/{len(article_links)}: {link}")
    
    create_index_file(output_dir, simple_name, writer, article_files_and_titles)
    print(f"Index file created for {writer}.")

# Main function
def main():
    # Load columnists from JSON file
    with open('columnists.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    columnists = data.get('columnists', [])
    
    for columnist in columnists:
        writer = columnist.get('writer')
        url = columnist.get('url')
        simple_name = columnist.get('simple_name')
        media = columnist.get('media')
        print(f"\nProcessing columnist: {writer}")
        process_columnist(writer, url, simple_name,media)

if __name__ == "__main__":
    main()
