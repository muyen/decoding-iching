#!/usr/bin/env python3
"""
Download ancient Zhou Yi texts from shuge.org
Uses Playwright for browser automation to find and download PDFs
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
TARGET_DIR = Path("/Users/arsenelee/github/iching/data/shuge-pdfs")
BOOKS = [
    {
        "url": "https://www.shuge.org/view/zhou_yi_ji_zhu/",
        "filename": "zhouyi_jizhu.pdf",
        "title": "周易集注"
    },
    {
        "url": "https://www.shuge.org/view/zhou_yi_zhuan_yi_da_quan/",
        "filename": "zhouyi_zhuanyi_daquan.pdf",
        "title": "周易传义大全"
    },
    {
        "url": "https://www.shuge.org/view/zhou_yi_wang_zhu/",
        "filename": "zhouyi_wangzhu.pdf",
        "title": "周易王注"
    }
]

async def download_book(context, book_info):
    """Navigate to book page and download PDF"""
    print(f"\nProcessing: {book_info['title']}")
    print(f"URL: {book_info['url']}")

    page = await context.new_page()

    try:
        # Navigate to the book page
        await page.goto(book_info['url'], wait_until="networkidle", timeout=60000)

        # Wait for page to load
        await page.wait_for_timeout(3000)

        # Find the download link
        download_link = None

        # Strategy 1: Look for download button/link with Chinese text
        try:
            selectors = [
                'a:has-text("下载")',
                'a:has-text("PDF")',
                'a:has-text("高清")',
            ]
            for selector in selectors:
                element = await page.query_selector(selector)
                if element:
                    download_link = await element.get_attribute('href')
                    if download_link:
                        print(f"Found download link: {download_link}")
                        break
        except Exception as e:
            print(f"Strategy 1 failed: {e}")

        if not download_link:
            print("Could not find download link")
            return None

        # Handle relative URLs
        if download_link.startswith('/'):
            download_link = f"https://www.shuge.org{download_link}"

        print(f"Following redirect: {download_link}")

        # Navigate to the download link to follow redirects
        await page.goto(download_link, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(2000)

        # Get the final URL after redirects
        final_url = page.url
        print(f"Final URL: {final_url}")

        # Now look for the actual PDF download link on the landing page
        # The page shows cloud storage options, we need to click the direct download link
        pdf_link = None

        # Try to find "此处下载" or "黑白版" (black & white version) links
        try:
            # Look for text-based download links
            # The "黑白版" option is likely a direct PDF download
            download_selectors = [
                'a:has-text("黑白版")',
                'a:has-text("此处下载")',
                'a:has-text("直接下载")',
                'a:has-text("文件直连")',
            ]

            for selector in download_selectors:
                element = await page.query_selector(selector)
                if element:
                    # Get the link
                    href = await element.get_attribute('href')
                    if href:
                        print(f"Found download link via {selector}: {href}")
                        if href.startswith('/'):
                            href = f"https://www.shuge.org{href}"

                        # If it's already a PDF, use it directly
                        if '.pdf' in href.lower():
                            pdf_link = href
                            print(f"Direct PDF link found: {pdf_link}")
                            break

                        # Otherwise navigate to follow the link
                        print(f"Following link to find PDF...")
                        response = await page.goto(href, wait_until="domcontentloaded", timeout=60000)

                        # Check if we got redirected to a PDF
                        if page.url.endswith('.pdf') or 'application/pdf' in (response.headers.get('content-type', '')):
                            pdf_link = page.url
                            print(f"Landed on PDF: {pdf_link}")
                            break

                        await page.wait_for_timeout(3000)

                        # Look for Download button (OpenList sharing page)
                        download_button = await page.query_selector('button:has-text("Download"), a:has-text("Download")')
                        if download_button:
                            print("Found Download button, clicking it...")
                            # Get the actual download URL by inspecting the button
                            # or try clicking and intercepting the download
                            onclick = await download_button.get_attribute('onclick')
                            href_from_button = await download_button.get_attribute('href')

                            if href_from_button:
                                pdf_link = href_from_button
                                print(f"Got PDF link from Download button: {pdf_link}")
                                break

                            # Try to find the download link by looking at the page structure
                            # OpenList pages usually have the download link in the page
                            import re
                            content = await page.content()

                            # Look for PDF file names in the content
                            pdf_match = re.search(r'([^"\'<>]+\.pdf)', content)
                            if pdf_match:
                                pdf_filename = pdf_match.group(1)
                                print(f"Found PDF filename: {pdf_filename}")

                                # Try to construct the download URL
                                # OpenList sharing pages typically have a download endpoint
                                # Try multiple patterns
                                page_id = page.url.split('/')[-1].split('?')[0]
                                possible_urls = [
                                    f"https://bw.shuge.org/api/raw/{page_id}",
                                    f"https://bw.shuge.org/api/fs/get/{page_id}",
                                    f"https://bw.shuge.org/d/{page_id}",
                                ]

                                # Try to find the actual API endpoint from page source
                                api_match = re.search(r'"(/api/[^"]+)"', content)
                                if api_match:
                                    api_path = api_match.group(1)
                                    download_url = f"https://bw.shuge.org{api_path}"
                                    print(f"Found API endpoint: {download_url}")
                                    possible_urls.insert(0, download_url)

                                # Test the first URL
                                if possible_urls:
                                    pdf_link = possible_urls[0]
                                    print(f"Using download URL: {pdf_link}")
                                    break

                        # Now try to find PDF link on this page
                        if not pdf_link:
                            pdf_element = await page.query_selector('a[href*=".pdf"]')
                            if pdf_element:
                                pdf_link = await pdf_element.get_attribute('href')
                                print(f"Found PDF after following link: {pdf_link}")
                                break

                        # Try getting from content
                        if not pdf_link:
                            import re
                            content = await page.content()
                            pdf_urls = re.findall(r'https?://[^\s"\'<>]+\.pdf', content)
                            if pdf_urls:
                                pdf_link = pdf_urls[0]
                                print(f"Found PDF in content: {pdf_link}")
                                break

        except Exception as e:
            print(f"Download link search failed: {e}")

        if not pdf_link:
            print("No PDF link found after redirect")
            screenshot_path = TARGET_DIR / f"{book_info['filename']}_page.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"Screenshot saved: {screenshot_path}")

            # Print page title and URL for debugging
            title = await page.title()
            print(f"Page title: {title}")
            print(f"Page URL: {page.url}")

            return None

        # Download using context.request to bypass download event issues
        print(f"Downloading PDF from: {pdf_link}")
        output_path = TARGET_DIR / book_info['filename']

        # Use curl for download as it's more reliable
        import subprocess
        result = subprocess.run(
            ['curl', '-L', '-o', str(output_path), pdf_link],
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and output_path.exists():
            file_size = os.path.getsize(output_path)
            file_size_mb = file_size / (1024 * 1024)
            print(f"Downloaded: {output_path}")
            print(f"Size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
            return output_path
        else:
            print(f"Download failed: {result.stderr}")
            return None

    finally:
        await page.close()

    return None

async def main():
    """Main function to download all books"""
    # Create target directory
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Target directory: {TARGET_DIR}")

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # Set to True for headless mode
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )

        # Process each book
        results = []
        for book_info in BOOKS:
            try:
                result = await download_book(context, book_info)
                results.append({
                    "book": book_info['title'],
                    "filename": book_info['filename'],
                    "success": result is not None,
                    "path": result
                })
            except Exception as e:
                print(f"Error processing {book_info['title']}: {e}")
                import traceback
                traceback.print_exc()
                results.append({
                    "book": book_info['title'],
                    "filename": book_info['filename'],
                    "success": False,
                    "error": str(e)
                })

        await browser.close()

        # Print summary
        print("\n" + "="*60)
        print("DOWNLOAD SUMMARY")
        print("="*60)
        for result in results:
            status = "SUCCESS" if result['success'] else "FAILED"
            print(f"{status}: {result['book']}")
            if result['success']:
                print(f"  File: {result['path']}")
            elif 'error' in result:
                print(f"  Error: {result['error']}")

        # List downloaded files
        print("\n" + "="*60)
        print("DOWNLOADED FILES")
        print("="*60)
        for pdf_file in sorted(TARGET_DIR.glob("*.pdf")):
            size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
            print(f"{pdf_file.name}: {size_mb:.2f} MB")

if __name__ == "__main__":
    asyncio.run(main())
