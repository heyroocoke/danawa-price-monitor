import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 한글 폰트 설정
plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False


def load_latest_csv():
    """data/ 디렉토리에서 가장 최근 CSV 파일을 읽어 키워드별 상품 데이터를 반환한다."""
    csv_files = sorted(
        [f for f in os.listdir("data") if f.startswith("가격비교") and f.endswith(".csv")]
    )
    if not csv_files:
        print("data/ 디렉토리에 가격비교 CSV 파일이 없습니다.")
        sys.exit(1)

    filename = csv_files[-1]
    print(f"{filename} 로딩...")

    data = {}
    with open(f"data/{filename}", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            keyword = row["키워드"]
            if row["가격"].isdigit():
                if keyword not in data:
                    data[keyword] = []
                data[keyword].append(
                    {
                        "name": row["상품명"][:25],
                        "price": int(row["가격"]),
                    }
                )

    if not data:
        print("유효한 가격 데이터가 없습니다.")
        sys.exit(1)

    return data


COLORS = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]


def plot_price_comparison(data):
    """키워드별 가격 비교 가로 막대 그래프를 생성한다."""
    fig, axes = plt.subplots(len(data), 1, figsize=(12, 5 * len(data)))
    if len(data) == 1:
        axes = [axes]

    for idx, (keyword, products) in enumerate(data.items()):
        ax = axes[idx]
        products_sorted = sorted(products, key=lambda x: x["price"])
        names = [p["name"] for p in products_sorted]
        prices = [p["price"] for p in products_sorted]

        bars = ax.barh(names, prices, color=COLORS[idx % len(COLORS)], height=0.6)
        ax.set_title(
            f"{keyword} - 가격 비교", fontsize=16, fontweight="bold", pad=15
        )
        ax.set_xlabel("가격 (원)", fontsize=12)

        for bar, price in zip(bars, prices):
            ax.text(
                bar.get_width() + max(prices) * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{price:,}",
                va="center",
                fontsize=10,
            )

        ax.set_xlim(0, max(prices) * 1.2)
        ax.grid(axis="x", alpha=0.3)

    plt.tight_layout(pad=3.0)
    plt.savefig("screenshots/price-comparison.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("screenshots/price-comparison.png 저장!")


def plot_lowest_price(data):
    """키워드별 최저가 비교 막대 그래프를 생성한다."""
    fig, ax = plt.subplots(figsize=(10, 6))

    keywords = list(data.keys())
    min_prices = [min(p["price"] for p in prods) for prods in data.values()]
    min_names = [
        min(prods, key=lambda x: x["price"])["name"] for prods in data.values()
    ]

    bars = ax.bar(keywords, min_prices, color=COLORS[: len(keywords)], width=0.5)

    for bar, price, name in zip(bars, min_prices, min_names):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(min_prices) * 0.02,
            f"{price:,}원\n({name})",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ax.set_title("키워드별 최저가 비교", fontsize=16, fontweight="bold")
    ax.set_ylabel("가격 (원)", fontsize=12)
    ax.set_ylim(0, max(min_prices) * 1.4)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("screenshots/lowest-price.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("screenshots/lowest-price.png 저장!")


def main():
    os.makedirs("screenshots", exist_ok=True)

    data = load_latest_csv()

    plot_price_comparison(data)
    plot_lowest_price(data)

    print(f"\n그래프 2개 생성 완료!")
    print(f"  - screenshots/price-comparison.png (키워드별 전체 가격)")
    print(f"  - screenshots/lowest-price.png (최저가 비교)")


if __name__ == "__main__":
    main()
