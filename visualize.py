import csv
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 서버 환경용 (화면 없이 이미지 저장)

# 한글 폰트 설정
plt.rcParams['font.family'] = 'NanumGothic'
import os

# CSV 파일 읽기
filename = sorted([f for f in os.listdir("data") if f.startswith("가격비교")])[-1]
print(f"📂 {filename} 로딩...")

data = {}
with open(f"data/{filename}", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        keyword = row["키워드"]
        if row["가격"].isdigit():
            if keyword not in data:
                data[keyword] = []
            data[keyword].append({
                "name": row["상품명"][:25],  # 그래프용 축약
                "price": int(row["가격"])
            })

# 그래프 폴더
os.makedirs("screenshots", exist_ok=True)

# ============================
# 그래프 1: 키워드별 가격 비교 (가로 막대)
# ============================
fig, axes = plt.subplots(len(data), 1, figsize=(12, 5 * len(data)))
if len(data) == 1:
    axes = [axes]

colors = ["#FF6B6B", "#4ECDC4", "#45B7D1"]

for idx, (keyword, products) in enumerate(data.items()):
    ax = axes[idx]
    products_sorted = sorted(products, key=lambda x: x["price"])
    names = [p["name"] for p in products_sorted]
    prices = [p["price"] for p in products_sorted]
    
    bars = ax.barh(names, prices, color=colors[idx % len(colors)], height=0.6)
    ax.set_title(f'{keyword} - Price Comparison', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Price (KRW)', fontsize=12)
    
    # 가격 라벨
    for bar, price in zip(bars, prices):
        ax.text(bar.get_width() + 5000, bar.get_y() + bar.get_height()/2,
                f'{price:,}', va='center', fontsize=10)
    
    ax.set_xlim(0, max(prices) * 1.2)
    ax.grid(axis='x', alpha=0.3)

plt.tight_layout(pad=3.0)
plt.savefig("screenshots/price-comparison.png", dpi=150, bbox_inches='tight')
print("✅ screenshots/price-comparison.png 저장!")

# ============================
# 그래프 2: 브랜드별 최저가 비교
# ============================
fig2, ax2 = plt.subplots(figsize=(10, 6))

keywords = list(data.keys())
min_prices = [min(p["price"] for p in products) for products in data.values()]
min_names = [min(products, key=lambda x: x["price"])["name"] for products in data.values()]

bars2 = ax2.bar(keywords, min_prices, color=colors[:len(keywords)], width=0.5)

for bar, price, name in zip(bars2, min_prices, min_names):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5000,
             f'{price:,} KRW\n({name})', ha='center', va='bottom', fontsize=10)

ax2.set_title('Lowest Price by Keyword', fontsize=16, fontweight='bold')
ax2.set_ylabel('Price (KRW)', fontsize=12)
ax2.set_ylim(0, max(min_prices) * 1.4)
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig("screenshots/lowest-price.png", dpi=150, bbox_inches='tight')
print("✅ screenshots/lowest-price.png 저장!")

print(f"\n📊 그래프 2개 생성 완료!")
print(f"   - screenshots/price-comparison.png (키워드별 전체 가격)")
print(f"   - screenshots/lowest-price.png (최저가 비교)")
