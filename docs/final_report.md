# Case Study Raporu

## KULLANILAN YAPAY ZEKA MODELLERİ

*   GEMINI 2.5 PRO EXP
*   MANUS
*   PERPLEXITY
*   GROK
*   CHATGPT

*(MANUS, PERPLEXITY VE GROK ADIM 0'DA KULLANILDI)*

## ADIM 0: LİTERATÜR TARAMASI VE MEVCUT PROJELERİN İNCELENMESİ

*   SOH (State of Health) ve SOC (State of Charge) için verinin nasıl işlendiği ve hangi modellerin kullanıldığı analiz edildi.
*   Mevcut kodlar incelendi:
    *   Manus'un interaktif websitesi: [https://jzbzrilu.manus.space/](https://jzbzrilu.manus.space/) (bu siteden çokça faydalanıldı)
    *   Manus Replay Linki: [https://manus.im/share/bbELiqCMAgfS4AXhtWQc1Y?replay=1](https://manus.im/share/bbELiqCMAgfS4AXhtWQc1Y?replay=1)
    *   Literatür Taraması ve Roadmap Oluşturma (Manus): [https://manus.im/share/Yd5U9FmYfGNd0woq8lIyIA?replay=1](https://manus.im/share/Yd5U9FmYfGNd0woq8lIyIA?replay=1)

Manus, kısıtlı zamanımız olduğu için research anlamında büyük ölçüde yardımcı oldu.

## ADIM 1: VERİSETİNİ İNDİRME

Veriseti manuel olarak indirildi. `B0005.mat`, `B0006.mat`, `B0018.mat` dosyaları kullanıldı.

## ADIM 2: VERİSETİNİ İNCELEME VE .MAT FORMATINDAN CSV FORMATINA GEÇİŞ

*   İlgili Notebook: `notebooks/1_initial_data_inspection.ipynb`
*   Referans Repo: [https://github.com/MoHoss007/Li-Ion-Battery-RUL-SOH-Prediction](https://github.com/MoHoss007/Li-Ion-Battery-RUL-SOH-Prediction)
    *   Dataseti `.mat` formatından `.csv` formatına geçirmede bu repodan yardım alındı.

## ADIM 3: DATA PREPARATION (VERİ HAZIRLAMA)

*   İlgili Notebook: `notebooks/2_data_preparation.ipynb`

### 3.1 Eksik Değerler Tespiti
Eksik değerler tespit edildi.

### 3.2 Veri Tipleri Kontrolü
Veri tipleri kontrol edildi.

### 3.3 Tekrarlanan Değerler Kontrolü
Tekrarlanan (duplicate) değerler kontrol edildi.

### 3.4 Outlier (Aykırı Değer) Analizi
*   Histogramlar ve Boxplotlar incelendi.
*   Voltaj değerlerindeki outlier'lar temizlendi: 0.0V - 4.5V aralığının dışındaki 7 değer tespit edilip veri setinden çıkarıldı (`drop` edildi).
*   Daha sonra eksik veriler (çıkarılan outlier'ların yerine) Linear Interpolation tekniğiyle dolduruldu.

### 3.5 SOH (State of Health) Değerlerinin Hesaplanması
*   SOH değerleri hesaplandı.
*   Batarya konusuna biraz yabancı olunduğu için SOH ve SOC arasındaki farkı anlamak zaman aldı. Bu noktada Gemini'dan bolca yardım alındı.
*   Ayrıca, verisetini model için hazırlarken SOH değerlerinin nasıl kullanılacağı konusunda başlangıçta kafa karışıklığı yaşandı. Daha sonra detaylı literatür taraması ve mevcut projelerin incelenmesiyle mevcut yapıya karar verildi.

### 3.6 Smoothing İçin Savitzky-Golay (Sav-Gol) Filtresi
*   Grafiklerde voltajda bazı ani sıçramalar (spike'lar) gözlemlendi.
*   Bu ani değişimlerin modelin performansını olumsuz etkilememesi için Savitzky-Golay filtresi kullanıldı.
*   Bu yaklaşım, *"Data-driven SOH Estimation of Lithium-ion Batteries Based on Savitzky-Golay Filtering and SSA-SVR Model"* makalesinde kullanıldığı ve model performansında artış gözlemlendiği belirtildiği için tercih edildi.

### 3.7 Verinin CSV Olarak Kaydedilmesi
Son olarak işlenen veri tekrar `.csv` formatında kaydedildi.

## 4. EDA (EXPLORATORY DATA ANALYSIS - KEŞİFÇİ VERİ ANALİZİ)

*   İlgili Notebook: `notebooks/3_exploratory_data_analysis.ipynb`

### 4.1 Bataryadaki SoH Değerinin Cycle'lara Göre İncelenmesi
Bataryanın sağlık durumunun (SoH) şarj/deşarj döngü sayısı (cycle) arttıkça nasıl bozulduğu incelendi.

### 4.2 Korelasyon Analizi

*   **soh ile cycle_number (-0.90):** Beklendiği gibi çok güçlü negatif korelasyon. Döngü sayısı arttıkça bataryanın sağlığı azalmaktadır.
*   **soh ile avg_voltage_measured (+0.95):** Son derece güçlü pozitif korelasyon. Bu, batarya bozuldukça (SoH düştükçe), deşarj sırasındaki ortalama voltajın önemli ölçüde azaldığını göstermektedir. Bu durum, `avg_voltage_measured`'ın SoH tahmini için çok umut verici bir öznitelik (feature) olduğunu işaret ediyor.
*   **soh ile discharge_time_s (+0.89):** Çok güçlü pozitif korelasyon. Sağlıklı bataryaların aynı akım altında tamamen deşarj olması daha uzun sürer. SoH düştükçe, bataryanın belirlenen kesme voltajına ulaşma süresi kısalır. Bu da modelleme için mükemmel bir potansiyel özniteliktir.
*   **soh ile avg_current_measured (-0.92):** Çok güçlü negatif korelasyon.
*   **soh ile delta_temp_measured (-0.85):** Güçlü negatif korelasyon. Sağlıklı bataryalar, bozulmuş bataryalara kıyasla deşarj sırasında daha küçük bir sıcaklık artışı yaşarlar. Bozulmuş bataryaların iç direnci genellikle daha yüksek olduğundan, deşarj sırasında daha fazla ısı üretirler. Bu nedenle `delta_temp_measured` (deşarj sırasındaki sıcaklık değişimi) SoH tahmini için çok kullanışlı bir özniteliktir.
*   **soh ile max_temp_measured (-0.70):** Orta derecede güçlü negatif korelasyon. Bozulmuş bataryalar deşarj sırasında daha yüksek maksimum sıcaklıklara ulaşma eğilimindedir.
*   **soh ile avg_temp_measured (-0.59):** Orta derecede negatif korelasyon. Benzer şekilde, bozulmuş bataryalar deşarj sırasında genellikle daha yüksek bir ortalama sıcaklığa sahip olurlar.

### 4.3 Deşarj Voltajının Farklı SoH Seviyelerine Göre Grafiklendirilmesi
Deşarj sırasındaki voltaj eğrilerinin farklı SoH seviyeleri için nasıl değiştiği görselleştirildi.

### 4.4 EDA Bulgularına Göre Feature Engineering ve Verinin Kaydedilmesi
EDA bulguları ışığında yeni öznitelikler türetildi (feature engineering) ve son veri seti bataryalara göre ayrı ayrı kaydedildi.

## 5. Model Geliştirme

*   İlgili Notebook: `Notebooks/4_model_development.ipynb`

### 5.1 Verinin Train/Validation/Test Olarak Ayrılması
Bu bir zaman serisi (time-series) tahmin görevi olduğu için veri kronolojik olarak train ve test setlerine ayrıldı. Veri %70 train, %15 validation ve %15 test olacak şekilde bölündü.

### 5.2 Özniteliklerin Hazırlanması
Öznitelikler (features) SoH tahmini için hazırlandı.

### 5.3 Random Forest Modeli Testi 1
*   Model, training ve validation setlerinde güzel sonuçlar verirken test setinde çok kötü sonuçlar verdi. Bu durum **Overfitting** (aşırı öğrenme) göstergesidir.
*   Muhtemel Sebepler:
    1.  Veri anlamsızlığı ya da fazlalığı.
    2.  Data leakage (veri sızması).
    3.  Hyperparametrelerin optimal olmaması.

### 5.4 Random Forest Modeli Testi 2
*   Veri seti deşarj döngülerine göre tekrar ayarlandı.
*   Hyperparametreler düzenlendi.
*   Yine overfitting sorunuyla karşılaşıldı.

### 5.5 XGBoost Regressor Testi
Bu model denemelerinde de overfitting ile karşılaşıldı.

### 5.6 LSTM Testleri
*   Veri, LSTM modelinin girdisine uygun olması için sekanslar (sequences) halinde yeniden düzenlendi.
*   LSTM, overfitting sorununu çözdü ve gayet iyi sonuçlar verdi.
*   **Not:** Grafik incelendiğinde validation seti için ayrılan boşluk fark edildi. Modelin RF ve XGBoost'da test setinde düşük sonuçlar vermesinin sebebinin bu olabileceği düşünüldü, ancak tekrar test edildiğinde bununla alakalı olmadığı anlaşıldı.

### 5.7 LSTM'in Diğer Bataryalar İçin Test Edilmesi
LSTM modeli diğer batarya (B0006, B0018) verileri için de test edildi ve başarılı sonuçlar alındı.

**- SONUÇLAR -**
Her batarya için ayrı ayrı oluşturulan ve eğitilen modeller kaydedildi. Bu modeller daha sonra REST API'da kullanılmak üzere saklandı.

### 5.8 EXTRA WORK: CNN-BiLSTM-AM Modeli

*   İlgili Notebook: `4.1_CNN_BiLSTM_AM.ipynb`
*   Referans Makale: *"State-of-Health Prediction of Lithium-Ion Batteries Based on CNN-BiLSTM-AM"* (Tian et al., Batteries 2022)
*   Bu makaledeki model (CNN-BiLSTM-Attention Mechanism) ve sonuçları incelendiğinde başarılı bulundu.
*   Makalede kullanılan Sağlık Göstergesi (Health Indicator - HI): **TIEDVD (Time Interval of Equal Discharging Voltage Difference)** - Deşarj sırasında 3.8V ile 3.4V arasındaki Eşit Deşarj Gerilimi Farkı Zaman Aralığı. Kabaca bu değer öznitelik olarak kullanıldı.
*   Model, makalede belirtildiği gibi kodlandı (build edildi).
*   Ekstra hyperparameter tuning (hiperparametre optimizasyonu) yapıldı ve farklı başlangıç noktaları (SP - starting point) denendi.
*   En iyi hyperparametreler ve konfigürasyonlar bulundu. Sonuçlar notebook'un sonunda tablo olarak listelendi.
*   Bu model, geliştirilen modeller arasında en iyi sonucu veren model oldu.
*   Ancak, bu modelin API'ye adaptasyonu sırasında bazı sıkıntılarla karşılaşıldı ve zaman kısıtlaması nedeniyle bu kısma daha fazla odaklanılmadı. (Bu kısımda biraz daha vakit olsaydı çözülebileceğine inanılıyor).
*   Dökümantasyon yazma işi son kısma bırakıldı. *(Kişisel Not: Şu an tarih 11.04.2024 ve saat 03:38, sanırım doğru kararı vermişim.)*
*   Makaledeki modelin koda dönüştürülmesi noktasında **Gemini 2.5 Pro** inanılmaz derecede yardımcı oldu.

## 6. API & DEMO & DOCKERIZATION

### 6.1 API (Backend)
*   **Framework:** FastAPI (container içinde çalışıyor)
*   **Port:** Host üzerinde 5001 portunda yayınlanır (container içi port 5000'e eşlenmiştir).
*   **Volumes:**
    *   `/models`: Batarya tahminleri için ML modellerini içerir.
    *   `/data`: Batarya veri setlerini içerir.
*   **Endpoint:** Batarya SOH (State of Health) tahmini için bir endpoint sağlar.

### 6.2 DEMO APP (Frontend)
*   **Framework:** Streamlit kullanılarak oluşturulmuştur.
*   **Port:** 8501 portu üzerinde çalışır.
*   **Özellikler:**
    *   Batarya tahminleri için interaktif web arayüzü.
    *   Veri görselleştirme (data visualization) bileşenleri.

### 6.3 DOCKERIZATION
*   **Araç:** Docker Compose kullanılarak multi-container kurulumu yapıldı.
*   **Bileşenler (Containers):**
    *   `backend`: Python/FastAPI servisi.
    *   `frontend`: Streamlit web uygulaması.
*   **Ağ Yapılandırması:**
    *   Servisler arası iletişim için özel bir bridge network (`battery_net`) oluşturuldu.
    *   Bu sayede izole edilmiş container iletişimi sağlandı.
*   **Volume Bağlantıları (Volume Mounts):**
    *   `models` ve `data` dizinlerine container'lar arası paylaşımlı erişim sağlandı.
*   **Bağımlılıklar:**
    *   Frontend container'ı, backend servisine bağımlıdır (çalışmak için backend'e ihtiyaç duyar).
*   **Kurulum:** Tek komutla kolay kurulum: `docker-compose up`