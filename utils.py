from playwright.sync_api import sync_playwright
from newspaper import Article
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
from lxml import etree



# with sync_playwright() as p:
#     browser = p.chromium.launch()
#     page = browser.new_page()
#     page.goto("https://www.bbc.co.uk/news/articles/cjrld3erq4eo", timeout=60000)
#     page.wait_for_selector("main")  # wait for full article to load
#     content = page.locator("main").inner_text()
#     print(content)
#     browser.close()
    
    

def fetch_full_article(url):
    """
    Fetches and returns the full textual content of a news article from a given URL.
    
    Args:
        url (str): The URL of the article to fetch.
        
    Returns:
        str or None: The raw full text of the article or None if unsuccessful.
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
    



def dict_to_xml(data, root_name='root', item_name='item'):
    """
    Converts a dictionary or list of dictionaries to a pretty-printed XML string.
    
    Args:
        data (dict or list): The data to convert.
        root_name (str): The name of the root XML tag.
        item_name (str): The name to use for each item element (if data is a list).
        
    Returns:
        str: A pretty-printed XML string.
    """
    # Convert dict/list to XML bytes
    xml_bytes = dicttoxml(
        data,
        custom_root=root_name,
        item_func=lambda x: item_name,
        attr_type=False
    )
    # Decode to string
    xml_string = xml_bytes.decode('utf-8')
    dom = parseString(xml_string)
    pretty_xml = dom.toprettyxml()
    return pretty_xml




def extract_article_content_from_xml(xml_file_path):
    """
    Extracts full_content, title, and author from the XML file of articles using XPath.
    
    Args:
        xml_file_path (str): Path to the XML file.
        
    Returns:
        List[Dict]: A list of dictionaries, each with keys 'full_content', 'title', 'author'.
    """
    with open(xml_file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()
    
    # Parse XML content
    tree = etree.fromstring(xml_content.encode('utf-8'))
    articles = tree.xpath('//article')
    results = []
    for art in articles:
        # Use XPath to find elements inside each article
        full_content = art.xpath('.//full_content/text()')
        title = art.xpath('.//title/text()')
        author = art.xpath('.//author/text()')
        # Extract text or default to None
        title = title[0] if title else None
        author = author[0] if author else None
        full_content = full_content[0] if full_content else None
        
        results.append({
            'title': title,
            'author': author,
            'full_content': full_content,
        })
    return results




def parse_xml(file_path):
    """
    Parses an XML file containing multiple news articles and extracts relevant metadata and content.

    Args:
        file_path (str): Path to the XML file containing news articles.

    Returns:
        list[dict]: A list of dictionaries where each dictionary contains the article metadata:
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        xml_data = f.read()
    root = etree.fromstring(xml_data.encode('utf-8'))
    articles = []
    for article in root.findall('article'):
        title = article.findtext('title')
        author = article.findtext('author')
        description = article.findtext('description')
        source_name = article.find('source/name').text if article.find('source/name') is not None else None
        published_at = article.findtext('publishedAt')
        url = article.findtext('url')
        full_content = article.findtext('full_content')

        articles.append({
            'title': title,
            'author': author,
            'description': description,
            'source_name': source_name,
            'published_at': published_at,
            'url': url,
            'full_content': full_content
        })
    return articles



def validate_xml(xml_path, xsd_path):
    """Validates an XML file against an XSD schema."""
    try:
        # Load the XSD schema
        xmlschema_doc = etree.parse(xsd_path)
        xmlschema = etree.XMLSchema(xmlschema_doc)

        # Load the XML file to be validated
        xml_doc = etree.parse(xml_path)
        
        # The assertValid method will raise an exception if validation fails
        xmlschema.assertValid(xml_doc)
        
        return True
    except etree.DocumentInvalid as e:
        # This catches validation-specific errors
        print("XML validation error:")
        print(e)
        return False
    except Exception as e:
        # This catches other errors, like file not found
        print(f"An error occurred during validation: {e}")
        return False