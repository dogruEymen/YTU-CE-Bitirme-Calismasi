from sqlalchemy import Column, Integer, String, Text, DateTime
from database.db import Base
# datetime kütüphanesi ileride varsayılan değer atamak isterseniz gerekli olabilir
from datetime import datetime 

class ArxivArticle(Base):
    __tablename__ = "arxiv_articles"

    # 1. Primary Key (Birincil Anahtar)
    # Neden standart bir 'id' ekliyoruz? arxiv_id zaten benzersiz değil mi?
    # Evet, arXiv ID'leri benzersizdir. Ancak veritabanı tasarımı standartlarında, 
    # dış dünyadan gelen (ve yapısı değişebilecek) ID'ler yerine, veritabanının 
    # kendisinin yönettiği, otomatik artan (autoincrement) tam sayı bir 'id' 
    # kullanmak her zaman daha güvenli ve performanslıdır (özellikle join işlemlerinde).
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 2. Arxiv ID
    # arXiv ID'leri sadece sayıdan oluşmaz (örn: "2105.12345" veya eski format "hep-th/9912293").
    # Bu yüzden 'Integer' değil, 'String' olmalıdır. Hızlı arama yapabilmek için 'index=True' 
    # ve aynı makalenin iki kez kaydedilmesini önlemek için 'unique=True' diyoruz.
    arxiv_id = Column(String(50), unique=True, index=True, nullable=False)

    # 3. Başlık
    # Başlıklar genellikle kısadır ancak bazen çok uzun bilimsel başlıklar olabilir.
    # Bu yüzden karakter sınırını geniş tutuyoruz.
    title = Column(String(500), nullable=False)

    # 4. Özet Metni
    # Neden String yerine Text? String(VARCHAR) veritabanlarında belirli bir karakter limitine 
    # sahiptir (genelde 255). Makale özetleri (abstract) sayfalarca sürebilir. Text tipi 
    # çok daha büyük boyutlu karakter dizilerini depolamak için optimize edilmiştir.
    abstract_text = Column(Text, nullable=True)

    # 5. Yayın Tarihi
    # XML'deki <published> etiketi bir tarih ve saat bilgisi taşır (örn: "2023-10-12T15:30:00Z").
    # Bunu veritabanında da DateTime objesi olarak tutmak, ileride "son 1 ayın makalelerini getir" 
    # gibi tarihsel sorgular yapabilmenizi sağlar.
    publish_date = Column(DateTime, nullable=True)

    # 6. Yazarlar (Şüpheli Nokta!)
    # Burada biraz kalıp dışı düşünelim: Birden fazla yazar var. Onları "Ali, Ayşe, Veli" gibi 
    # tek bir String içinde tutmak şu an için kolaydır. Ancak ileride "Ayşe'nin yazdığı tüm makaleler" 
    # demek isterseniz bu tasarım sizi yavaşlatır (veritabanı normalizasyon kurallarına aykırıdır).
    # Şimdilik talebinize uygun olarak tek sütun (Text) yapıyoruz, ancak profesyonel bir sistemde 
    # 'authors' ayrı bir tablo olup 'Çoka-Çok' (Many-to-Many) ilişki ile bağlanmalıdır.
    authors = Column(Text, nullable=True)

    # 7. URL ve Kategori
    # URL'ler standart metinlerdir. Bir makalenin URL'si veya kategorisi bazen eksik olabilir, 
    # bu ihtimale karşı nullable=True (boş bırakılabilir) olarak ayarlıyoruz.
    pdf_url = Column(String(500), nullable=True)
    primary_category = Column(String(100), nullable=True)