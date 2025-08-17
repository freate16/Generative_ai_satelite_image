import requests
from bs4 import BeautifulSoup
import os
import time
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def concise_description(text):
    """
    Takes raw ESA description and converts it into a concise, visual description.
    """
    # Use model to summarize into fewer words
    summary = summarizer(
        text,
        max_length=40,  # adjust for brevity
        min_length=10,
        do_sample=False
    )[0]["summary_text"]

    # Optional: make it look like a scene prompt
    return summary.lower().strip()

def scrape_all_esa_images():
    base_url = "https://www.esa.int"
    gallery_url_template = (
        "https://www.esa.int/ESA_Multimedia/Sets/Earth_from_Space_image_collection/"
        "(offset)/{offset}/(sortBy)/published/(result_type)/images"
    )

    # Create folder for images
    os.makedirs("esa_images_new", exist_ok=True)

    image_page_links = []
    print("Collecting links from all 20 gallery pages...")

    # Step 1: Collect all individual image page links
    for i in range(20):
        offset = i * 50
        gallery_url = gallery_url_template.format(offset=offset)
        try:
            response = requests.get(gallery_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            for item in soup.find_all("div", class_="grid-item image"):
                link_tag = item.find("a")
                if link_tag and link_tag.get("href"):
                    image_page_links.append(link_tag["href"])

            print(f"Page {i+1}/20 scanned. Total links so far: {len(image_page_links)}")
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"Could not fetch gallery page {i+1}: {e}")
            continue

    print(f"\nFinished collecting links. Found {len(image_page_links)} image pages.")
    print("\nStarting to download high-resolution images...")

    # # Step 2: Visit each image page and download the HI-RES JPG/PNG
    # for i, page_link in enumerate(image_page_links, start=1):
    #     detail_page_url = f"{base_url}{page_link}"
    #     try:
    #         resp = requests.get(detail_page_url, timeout=10)
    #         resp.raise_for_status()
    #         soup = BeautifulSoup(resp.content, "html.parser")

    #         image_url = None

    #         # Look inside the dropdown list
    #         dropdown_div = soup.find("div", class_="dropdown")
    #         if dropdown_div:
    #             for a_tag in dropdown_div.find_all("a", href=True, title=True):
    #                 title = a_tag["title"].lower()
    #                 href = a_tag["href"].strip()

    #                 # Pick the HI-RES JPG/JPEG/PNG link
    #                 if "hi-res" in title and any(href.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
    #                     image_url = href
    #                     break

    #         if not image_url:
    #             print(f"({i}/{len(image_page_links)}) No HI-RES JPG/PNG link found on {detail_page_url}")
    #             continue

    #         # Handle relative URLs like "/var/esa/storage/..."
    #         if not image_url.startswith("http"):
    #             image_url = base_url + image_url

    #         print(f"({i}/{len(image_page_links)}) Downloading: {image_url}")

    #         img_resp = requests.get(image_url, timeout=20)
    #         img_resp.raise_for_status()

    #         # Save with correct extension
    #         ext = os.path.splitext(image_url)[1]
    #         filename = f"esa_images/image_{i:04d}{ext}"
    #         with open(filename, "wb") as f:
    #             f.write(img_resp.content)

    #         print(f"Saved to {filename}")
    #         time.sleep(1)

    #     except requests.exceptions.RequestException as e:
    #         print(f"Could not process page {detail_page_url}: {e}")
    #         continue

    #print("\n✅ Scraping complete!")
    print("Starting concise description extraction...")

    for idx, page_link in enumerate(image_page_links, start=1):
        detail_page_url = f"{base_url}{page_link}"
        try:
            resp = requests.get(detail_page_url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")

            desc_div = soup.find("div", class_="modal__tab-description")
            raw_text = ""
            if desc_div:
                paragraphs = desc_div.find_all("p")
                raw_text = " ".join(p.get_text(strip=True) for p in paragraphs)

            if raw_text:
                concise_text = concise_description(raw_text)
            else:
                concise_text = "no description available"

            desc_filename = f"esa_description/desc_{idx:04d}.txt"
            with open(desc_filename, "w", encoding="utf-8") as f:
                f.write(concise_text)

            print(f"({idx}/{len(image_page_links)}) Saved concise description for {detail_page_url}")
            time.sleep(1)
        except Exception as e:
            print(f"Error on {detail_page_url}: {e}")

    print("\n✅ All concise descriptions saved.")

if __name__ == "__main__":
    scrape_all_esa_images()
