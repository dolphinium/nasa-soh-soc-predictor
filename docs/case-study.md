# AI Developer Teknik Mülakat Görevi: Lithium-Ion Batarya SoH/SoC Analiz ve

# Demo Uygulaması

**Amaç:** Bu görev kapsamında, NASA’nın sağladığı lityum iyon batarya veri setlerini kullanarak
bataryaların Durum Tahmini (State of Health - SoH) ve Şarj Durumu (State of Charge - SoC) değerlerini
tahmin etmek üzere makine öğrenmesi modelleri gelişKreceksiniz. Ek olarak, eğiOğiniz modeli bir REST
API aracılığıyla servis haline geKrecek, bu API’yi çağıran basit bir demo uygulaması (örneğin Node.js
tabanlı) hazırlayarak çözümünüzü son kullanıcıya sunabileceğinizi göstereceksiniz.

## Teknoloji Seçenekleri

- **Backend:** Python (Flask veya FastAPI), Node.js, .NET Core
- **Frontend/Demo:** Node.js tabanlı basit uygulama, React.js veya alternaKf olarak Streamlit
- **Veritabanı:** İhKyaca göre PostgreSQL, MSSQL veya MongoDB kullanılabilir
- **Veri Bilimi Kütüphaneleri:** Python için pandas, NumPy, scikit-learn, TensorFlow/Keras veya
    PyTorch
- **Konteynerizasyon:** Projenin Docker ile konteynerleşKrilmesi zorunludur (Docker Compose
    tercih edilir)
- **Üretken AI Araçları:** ChatGPT, Gemini, Claude gibi araçları danışmanlık amacıyla
    kullanabilirsiniz; kullanımınızı raporunuzda belirKniz.

## Görev Adımları

**1. Veri SeDnin İncelenmesi ve Hazırlanması**
    - **Veri SeD:** NASA PrognosKcs Center of Excellence Data Set Repository’den B0005, B0006 ve
       B0018 batarya veri setlerini indirin.
          o Adres: heps://www.nasa.gov/intelligent-systems-division/discovery-and-systems-
             health/pcoe/pcoe-data-set-repository/
          o Doğrudan indirme bağlanf adresi: heps://phm-
             datasets.s3.amazonaws.com/NASA/5.+Baeery+Data+Set.zip
          o Zip dosyasını açın ve /5. Baeery Data Set/1. BaeeryAgingARC-FY08Q4 dosyasına gidin.


o Burada yer alan B0005, B0006 ve B0018 batarya veri setlerini indirin.

- **Ön İşleme:** Veri temizleme, eksik değerlerin tamamlanması, gürültülü verilerin temizlenmesi
    ve gerekirse veri normalizasyonu gibi adımları uygulayarak analiz için uygun hale geKrin.
- **Raporlama:** Yapfğınız ön işlemleri, kullandığınız yöntemleri ve karşılaşfğınız zorlukları kısa bir
    dokümantasyonla açıklayın.
**2. Keşifsel Veri Analizi (EDA)**
- **Analiz:** Veri seKndeki özellikler arasındaki ilişkileri heatmap, korelasyon analizi gibi yöntemlerle
inceleyin. Özellikle SoH, SoC ve batarya sıcaklığı, akım yükü gibi özellikler arasındaki ilişkilere
odaklanın.


- **Özellik Seçimi:** Modelleme sürecinde hangi özelliklerin önemli olduğunu belirleyin ve bunları
    raporunuzda gerekçelendirin.
- **GörselleşDrme:** EDA sürecinde elde eOğiniz sonuçları grafikler ve tablolar ile destekleyin.
**3. SoH ve SoC Tahmin Modelinin GelişDrilmesi**
- **Model GelişDrme:** SeçKğiniz makine öğrenmesi yöntemleri (regresyon, ağaç tabanlı modeller
veya derin öğrenme teknikleri) ile SoH ve SoC tahmin modellerinizi gelişKrin.
- **Veri Bölme:** Veri seKnizi eğiKm ve test setlerine ayırarak modelinizi eğiKn.
- **Performans Değerlendirmesi:** Model performansını MAE, RMSE gibi metriklerle değerlendirin
ve sonuçları raporlayın.
- **Güncel Yaklaşımlar:** İsterseniz, üretken AI araçlarını (ör. ChatGPT, Gemini, Claude) model
gelişKrme veya sonuçların yorumlanması aşamasında danışmanlık aracı olarak kullanabilirsiniz.
Eğer kullandıysanız, raporunuzda bu araçların hangi kısımlarda kullanıldığını ve elde eOğiniz
çıkflara nasıl katkı sağladığını açıklayın.
**4. API Entegrasyonu ve Demo Uygulaması**
- **REST API GelişDrme:** EğiOğiniz modeli kullanarak, batarya verilerini girdi alıp SoH/SoC tahmini
döndüren basit bir REST API oluşturun. Backend teknolojilerinden (Python: Flask/FastAPI,
Node.js, .NET Core vb.) birini tercih edebilirsiniz.
- **Demo Uygulaması:** API’nizi çağıran, basit bir Node.js tabanlı veya tercih eOğiniz başka bir
framework ile gelişKrilmiş demo uygulaması hazırlayın. Uygulama, kullanıcıların API’ye veri
göndermesi ve tahmin sonuçlarını görsel olarak sunması şeklinde olmalıdır.
- **Docker:** Tüm projenizi Docker ile konteynerleşKrip, Docker Compose kullanarak bağımlılıkların
yöneKldiği bir yapı sunun.
**5. Sonuçların Değerlendirilmesi ve Raporlama**
- **Detaylı Rapor:** Projenin tüm aşamalarını kapsayan, kullanılan yöntemlerin, model seçiminin,
elde edilen sonuçların ve karşılaşılan sorunların detaylandırıldığı bir rapor hazırlayın.
Raporunuzda aşağıdaki bölümler yer almalıdır:
o Problemin Tanımı ve Amacı

o Veri SeK ve Ön İşleme Adımları
o Keşifsel Veri Analizi (EDA) Sonuçları
o Model GelişKrme Süreci ve Performans Metrikleri
o REST API Tasarımı ve Demo Uygulaması Açıklaması
o Üretken AI Araçlarının Kullanımı (varsa): Hangi kısımlarda kullanıldığını ve bu kullanımın
sonuçlara etkisini detaylandırın.
o Gerçek Dünya Entegrasyonu Önerileri: Örneğin, modelin batarya yöneKm sistemine
entegrasyonu, edge deployment senaryoları veya MLOps süreçleri üzerine önerileriniz.

- **Opsiyonel Sunum Videosu:** Çalışmanızı açıklayan 5 dakikalık bir demo sunum videosu ekleyin.


## Teslim Şartları

- **Dosya PakeD:** Tüm dokümanlar (Jupyter Notebook’lar, REST API ve demo uygulaması kodları,
    rapor – Word/PDF formafnda, varsa demo videosu) tek bir zip veya rar dosyasında
    sunulmalıdır.
- **GitHub:** Projenizi GitHub üzerinden paylaşarak README dosyasında projenin nasıl
    çalışfrılacağı, API kullanımı, Docker yapılandırması gibi bilgileri ekleyiniz.
- **Gönderim:** Dosya pakeKni belirKlen e-posta adresine, belirKlen tarih ve saate kadar gönderiniz.

## Değerlendirme Kriterleri

**1. İstenenlerin Tamamlanma Durumu:** Tüm adımlar (veri hazırlama, EDA, model gelişKrme, API
    entegrasyonu, demo uygulaması) eksiksiz gerçekleşKrilmiş mi?
**2. Kodun Kalitesi ve Esnekliği:** Yazılan kodun okunabilirliği, modülerliği ve yeniden
    kullanılabilirliği.
**3. Model Performansı ve Yorumlama:** Modelin başarım metrikleri (MAE, RMSE) ve sonuçların
    yorumlanma kalitesi.
**4. API ve Demo Uygulaması:** API’nin işlevselliği, demo uygulamasının kullanışlılığı ve sunum
    kalitesi.
**5. Raporun İçerik ve Düzen Kalitesi:** Te k n i k d e t ay l a r ı n , y ö n t e m l e r i n v e s o n u ç l a r ı n a n l a ş ı l ı r ş e k i l d e
    raporlanması.
**6. Üretken AI Araçlarının Kullanımı:** Eğer kullanıldıysa, araçların nasıl destekleyici olarak
    kullanıldığının açıkça belirKlmesi ve adayın özgün katkısının ortaya konması.
**7. Proje Sunum Videosu (Opsiyonel):** Çözümün sözlü olarak sunulması, sorulara verilen yanıtlar
    ve projenin genel savunulması.
**8. Docker ile Konteynerizasyon:** Projenin Docker ortamında sorunsuz çalışfrılabilir olması.

## Ek Notlar

- **Üretken AI Araçları:** Görev sırasında üretken yapay zeka destekli araçlardan yararlanabilirsiniz.
    Ancak, kullandıysanız hangi kısımlarda kullandığınızı ve elde eOğiniz çıkfyı nasıl doğruladığınızı
    mutlaka raporunuzda belirKniz.
- **Gerçek Dünya Entegrasyonu:** GelişKrdiğiniz modelin potansiyel gerçek dünya kullanım
    alanlarını (ör. batarya yöneKm sistemleri, edge deployment) tarfşmanız, çözümünüzün sadece
    akademik kalıpların ötesine geçKğini gösterecekKr.
- **Bonus:** Eğer zamanınız kalırsa, modelin MLOps süreçleri (otomaKk eğiKm, versiyon kontrolü,
    yeni veri akışında yeniden eğiKm gibi) hakkında kısa bir değerlendirme veya öneri eklemeniz
    olumlu değerlendirilecekKr.


