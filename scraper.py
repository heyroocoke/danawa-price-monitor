import csv
import sys
import time
from datetime import datetime
from urllib.parse import quote

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def scrape_danawa(page, keyword):
    """다나와에서 키워드로 상품을 검색하고 가격 정보를 수집한다."""
    encoded = quote(keyword)
    page.goto(f"https://search.danawa.com/dsearch.php?query={encoded}")
    page.wait_for_timeout(3000)

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    products = []
    items = soup.select(".product_list .prod_item")

    for item in items[:10]:
        name_tag = item.select_one(".prod_name a")
        if not name_tag:
            continue
        name = name_tag.get_text(strip=True)

        price_tag = item.select_one(".price_sect a strong")
        price = (
            price_tag.get_text(strip=True).replace(",", "") if price_tag else "가격없음"
        )

        products.append(
            {
                "키워드": keyword,
                "상품명": name,
                "가격": price,
                "수집일": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        )

    return products


def main():
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = input("검색할 키워드를 입력하세요 (쉼표로 구분): ")

    keywords = [k.strip() for k in user_input.split(",") if k.strip()]

    if not keywords:
        print("키워드를 입력해주세요.")
        sys.exit(1)

    print(f"\n검색 키워드: {keywords}\n")

    import os

    os.makedirs("data", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        all_results = []
        for keyword in keywords:
            print(f"'{keyword}' 검색 중...")
            try:
                results = scrape_danawa(page, keyword)
                all_results.extend(results)
                print(f"  -> {len(results)}개 수집 완료")
            except Exception as e:
                print(f"  -> '{keyword}' 수집 실패: {e}")
            time.sleep(2)

        browser.close()

    if not all_results:
        print("\n수집된 결과가 없습니다.")
        sys.exit(1)

    print(f"\n전체 수집 결과 ({len(all_results)}개)\n")
    print(f"{'키워드':<12} {'상품명':<45} {'가격':>12}")
    print("-" * 72)
    for r in all_results:
        price_display = (
            f"{int(r['가격']):,}원" if r["가격"].isdigit() else r["가격"]
        )
        print(f"{r['키워드']:<12} {r['상품명'][:43]:<45} {price_display:>12}")

    filename = f"data/가격비교_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["키워드", "상품명", "가격", "수집일"])
        writer.writeheader()
        writer.writerows(all_results)
        print(f"\n{filename} 저장 완료!")


if __name__ == "__main__":
    main()
