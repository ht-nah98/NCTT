#!/usr/bin/env python3
"""Dựng corpus tham chiếu: câu mở đầu (<=10 từ) của các hymn/spiritual
đã public domain (sáng tác hoặc xuất bản trước 1930, một số trước 1900).
Chỉ dùng để ĐO TRÙNG LẶP kỹ thuật (match_ratio) với lyrics_raw.parquet —
không phải để phát hành lại. Mỗi entry có year + note nguồn gốc.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "framework/04_reference/pd_corpus/hymns_pd.json"

# incipit = vài từ mở đầu đủ để nhận diện, không phải toàn bộ lời bài hát.
# year = năm sáng tác/xuất bản đầu tiên được ghi nhận (đều thuộc PD tại Mỹ).
HYMNS = [
    {"title": "Amazing Grace", "year": 1779, "incipit": "amazing grace how sweet the sound that saved a wretch like me"},
    {"title": "How Great Thou Art", "year": 1885, "incipit": "o lord my god when i in awesome wonder"},
    {"title": "It Is Well with My Soul", "year": 1876, "incipit": "when peace like a river attendeth my way"},
    {"title": "Blessed Assurance", "year": 1873, "incipit": "blessed assurance jesus is mine o what a foretaste of glory divine"},
    {"title": "The Old Rugged Cross", "year": 1913, "incipit": "on a hill far away stood an old rugged cross"},
    {"title": "Swing Low, Sweet Chariot", "year": 1862, "incipit": "swing low sweet chariot coming for to carry me home"},
    {"title": "Wade in the Water", "year": 1901, "incipit": "wade in the water wade in the water children"},
    {"title": "Nobody Knows the Trouble I've Seen", "year": 1867, "incipit": "nobody knows the trouble i've seen nobody knows my sorrow"},
    {"title": "Go Down Moses", "year": 1861, "incipit": "when israel was in egypt's land let my people go"},
    {"title": "Were You There", "year": 1899, "incipit": "were you there when they crucified my lord"},
    {"title": "This Little Light of Mine", "year": 1920, "incipit": "this little light of mine i'm gonna let it shine"},
    {"title": "Down by the Riverside", "year": 1918, "incipit": "gonna lay down my burden down by the riverside"},
    {"title": "When the Saints Go Marching In", "year": 1896, "incipit": "oh when the saints go marching in"},
    {"title": "Precious Lord, Take My Hand", "year": 1932, "incipit": "precious lord take my hand lead me on let me stand", "status": "check"},
    {"title": "I'll Fly Away", "year": 1929, "incipit": "some glad morning when this life is over i'll fly away"},
    {"title": "Will the Circle Be Unbroken", "year": 1907, "incipit": "will the circle be unbroken by and by lord by and by"},
    {"title": "Rock of Ages", "year": 1763, "incipit": "rock of ages cleft for me let me hide myself in thee"},
    {"title": "Holy, Holy, Holy", "year": 1826, "incipit": "holy holy holy lord god almighty"},
    {"title": "Come Thou Fount", "year": 1758, "incipit": "come thou fount of every blessing tune my heart to sing thy grace"},
    {"title": "What a Friend We Have in Jesus", "year": 1855, "incipit": "what a friend we have in jesus all our sins and griefs to bear"},
    {"title": "Leaning on the Everlasting Arms", "year": 1887, "incipit": "what a fellowship what a joy divine leaning on the everlasting arms"},
    {"title": "In the Sweet By and By", "year": 1868, "incipit": "there's a land that is fairer than day"},
    {"title": "Nearer, My God, to Thee", "year": 1841, "incipit": "nearer my god to thee nearer to thee"},
    {"title": "Abide with Me", "year": 1847, "incipit": "abide with me fast falls the eventide"},
    {"title": "O Come, All Ye Faithful", "year": 1751, "incipit": "o come all ye faithful joyful and triumphant"},
    {"title": "Steal Away", "year": 1862, "incipit": "steal away steal away steal away to jesus"},
    {"title": "Sometimes I Feel Like a Motherless Child", "year": 1867, "incipit": "sometimes i feel like a motherless child a long way from home"},
    {"title": "Deep River", "year": 1917, "incipit": "deep river my home is over jordan"},
    {"title": "Every Time I Feel the Spirit", "year": 1867, "incipit": "every time i feel the spirit moving in my heart"},
    {"title": "Peace in the Valley", "year": 1937, "incipit": "well i'm tired and so weary but i must go along", "status": "check"},
    {"title": "Farther Along", "year": 1911, "incipit": "farther along we'll know all about it farther along we'll understand why"},
    {"title": "Softly and Tenderly", "year": 1880, "incipit": "softly and tenderly jesus is calling calling for you and for me"},
    {"title": "At the Cross", "year": 1707, "incipit": "alas and did my savior bleed and did my sovereign die"},
    {"title": "I Must Tell Jesus", "year": 1893, "incipit": "i must tell jesus all of my trials"},
    {"title": "Standing in the Need of Prayer", "year": 1905, "incipit": "not my brother nor my sister but it's me o lord"},
    {"title": "Give Me Jesus", "year": 1900, "incipit": "in the morning when i rise give me jesus"},
    {"title": "Balm in Gilead", "year": 1854, "incipit": "there is a balm in gilead to make the wounded whole"},
    {"title": "Just a Closer Walk with Thee", "year": 1940, "incipit": "i am weak but thou art strong jesus keep me from all wrong", "status": "check"},
    {"title": "Great Is Thy Faithfulness", "year": 1923, "incipit": "great is thy faithfulness o god my father"},
]

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    for h in HYMNS:
        h.setdefault("status", "pd")  # pd = chắc chắn PD; check = năm >=1930, cần xác minh riêng
    n_check = sum(1 for h in HYMNS if h["status"] == "check")
    payload = {
        "note": (
            "Câu mở đầu (incipit) của hymn/spiritual tại Mỹ. Dùng để đo "
            "match_ratio kỹ thuật với lyrics_raw.parquet — không phải bản phát hành lại. "
            "status='pd': sáng tác/xuất bản trước 1930, chắc chắn public domain. "
            "status='check': năm sáng tác >=1930 (ranh giới luật PD Mỹ), KHÔNG được báo là "
            "PD chắc chắn — cần kiểm tra hồ sơ bản quyền cụ thể trước khi kết luận."
        ),
        "n_hymns": len(HYMNS),
        "n_confirmed_pd": len(HYMNS) - n_check,
        "n_needs_check": n_check,
        "hymns": HYMNS,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đã ghi {len(HYMNS)} hymn/spiritual ({len(HYMNS)-n_check} PD chắc chắn, {n_check} cần kiểm tra) -> {OUT}")

if __name__ == "__main__":
    main()
