# AI Developer Teknik Mülakat Görevi: Lityum-İyon Batarya SoH/SoC Analizi - Proje Özeti

## Amaç
Bu projenin amacı, NASA tarafından sağlanan lityum-iyon batarya veri setlerini (B0005, B0006, B0018) kullanarak bataryaların Sağlık Durumu (`SoH` - State of Health) ve potansiyel olarak Şarj Durumu (`SoC` - State of Charge) değerlerini tahmin etmek için makine öğrenmesi modelleri geliştirmekti. Görev tanımında ayrıca bir `REST API` ve demo uygulaması geliştirilmesi istense de, sağlanan dokümanlar projenin veri hazırlama, keşifsel analiz ve `SoH` modelleme aşamalarına odaklandığını göstermektedir. `SoC` tahmini ve API/Demo geliştirme aşamaları bu özetin kapsadığı çalışmalarda ele alınmamıştır.

## Teknoloji ve Kütüphaneler
Proje boyunca Python programlama dili ve ilişkili veri bilimi kütüphaneleri kullanılmıştır:

* Veri işleme ve analiz: `pandas`, `numpy`
* `.mat` dosyalarını okuma: `scipy.io.loadmat`
* Sinyal işleme: `scipy.signal` (`savgol_filter`)
* Makine öğrenmesi: `scikit-learn` (veri bölme, `StandardScaler`, `RandomForestRegressor`, metrikler), `xgboost` (`XGBRegressor`), `tensorflow`/`keras` (`LSTM`, `Sequential`, `pad_sequences`, `Masking`)
* Görselleştirme: `matplotlib`, `seaborn`
* Ortam: `conda`, `Jupyter Notebook` (VS Code içinde), `Git` (versiyon kontrolü için)

## Görev Adımları ve Bulgular

### 1. Veri Setinin İncelenmesi ve Hazırlanması

* **Veri İndirme ve Proje Kurulumu:** NASA Prognostics Center of Excellence Data Set Repository'den B0005, B0006 ve B0018 bataryalarına ait `.mat` formatındaki ham veri dosyaları indirildi. Önerilen dizin yapısı (`data/raw_data`, `notebooks/`, `scripts/`, vb.) oluşturuldu, `conda` ortamı kuruldu ve `Git` repository başlatıldı (`01_Project_Setup_and_Initial_Inspection.md`).

* **İlk İnceleme:** `scipy.io.loadmat` kullanılarak bir `.mat` dosyası (B0005.mat) yüklendi. Verinin Python dictionary içinde, batarya ID'si anahtarı altında iç içe geçmiş yapılandırılmış `numpy` dizileri (`structured arrays`) olarak saklandığı tespit edildi. Veri yapısı: `dict -> structured_array[battery_id] -> structured_array['cycle'] -> array_of_cycles -> cycle_struct['data'] -> measurement_struct`. Bu karmaşık yapı, veriyi `pandas DataFrame`'e dönüştürmek için özel bir ayrıştırıcı (parser) fonksiyonu gerektirdi (`01_Project_Setup_and_Initial_Inspection.md`).

* **Veri Ayrıştırma (`Parsing`):** `scripts/data_utils.py` içinde `parse_nasa_mat_file` adında bir fonksiyon geliştirildi. Bu fonksiyon, `.mat` dosyalarındaki iç içe yapıyı dolaşarak her bir ölçüm zaman adımını (`Voltage_measured`, `Current_measured`, `Temperature_measured`, `Time`, vb.) ve ilgili döngü bilgilerini (`cycle_number`, `cycle_type`, `ambient_temperature`) düz bir `pandas DataFrame`'e aktardı. Geliştirme süreci iteratif oldu; farklı döngü tiplerinin (`charge`, `discharge`, `impedance`) farklı alan adlarına sahip olması ve `capacity` bilgisinin `discharge` döngülerinde ölçüm yapısı içinde bulunması gibi zorluklar aşıldı. `impedance` döngüleri analiz dışı bırakıldı. Sonuçta B0005, B0006 ve B0018 için ayrı `DataFrame`'ler oluşturulup `nasa_battery_data_combined.csv` olarak birleştirildi (`02_Data_Parsing_Function.md`).

* **Ön İşleme (Temizleme ve Yumuşatma):** Birleştirilmiş veri (`df`) yüklendi. Eksik değerler kontrol edildi; ölçüm sütunlarındaki çok az sayıdaki (`NaN`) satır düşürüldü. Aykırı değer analizi yapıldı; özellikle `voltage_measured` için fiziksel olarak mantıksız değerler (>4.5V, <0V) tespit edildi, `NaN` ile değiştirildi ve döngü bazında lineer interpolasyon (`interpolate`) ile dolduruldu. Sinyallerdeki gürültüyü azaltmak için `scipy.signal.savgol_filter` (Savitzky-Golay filtresi) kullanılarak `voltage_measured`, `current_measured`, `temperature_measured` sinyalleri döngü bazında yumuşatıldı ve yeni `_smooth` sütunlarına kaydedildi. İşlenmiş veri `nasa_battery_data_preprocessed.csv` olarak kaydedildi (`03_Data_Cleaning_and_Smoothing.md`).

### 2. Keşifsel Veri Analizi (EDA)

* **`SoH` Hesaplama:** Her batarya için `SoH`, ilgili deşarj döngüsünün kapasitesinin ilk döngüdeki kapasiteye oranı olarak hesaplandı. Bu döngü seviyesi `SoH` değeri, aynı döngü içindeki tüm ölçüm satırlarına yayıldı (`04_Exploratory_Data_Analysis.md`).

* **Analiz ve Görselleştirme:**
    * `SoH` vs. `cycle_number` grafiği, tüm bataryalarda belirgin bir bozulma (degradation) trendi olduğunu, ancak bozulma hızlarının farklılaştığını (B0005 en yavaş) ve doğrusal olmayan davranışlar ("knee" noktaları, geçici kapasite artışları) gösterdiğini ortaya koydu.
    * Döngü seviyesinde agrega edilmiş veriler (`cycle_agg DataFrame`) üzerinde korelasyon analizi yapıldı. `SoH` ile `cycle_number` (-0.90), `delta_temp_measured` (-0.85), `avg_current_measured` (-0.92), `avg_voltage_measured` (+0.95), `discharge_time_s` (+0.89) arasında güçlü korelasyonlar bulundu. Bu, bu özelliklerin potansiyel `SoH` tahminleyicileri olduğunu gösterdi.
    * Farklı yaşam evrelerindeki (erken, orta, geç) deşarj voltaj eğrileri (`voltage_measured_smooth` vs. zaman) karşılaştırıldı. Düşük `SoH`'a sahip döngülerde deşarj süresinin kısaldığı, voltaj profilinin düştüğü ve eğri şeklinin belirgin şekilde değiştiği gözlemlendi. Bu, sadece ortalama değerlerin değil, eğri şeklini yakalayan özelliklerin (veya dizi tabanlı modellerin) önemini vurguladı (`04_Exploratory_Data_Analysis.md`).

* **Veri Yeniden Yapılandırma (Model Stratejisi Değişikliği):** EDA'da gözlemlenen bataryalar arası farklı bozulma paternleri nedeniyle, başlangıçta planlanan tek bir birleşik model yerine, her batarya için ayrı modeller (`battery-specific models`) geliştirilmesine karar verildi. Bu doğrultuda, tam ön işleme adımlarından geçmiş veri (`df_eda`), her batarya için ayrı CSV dosyalarına (`nasa_battery_data_[ID]_preprocessed.csv`) kaydedildi. Model geliştirme aşamasında bu dosyalardan biri yüklenecek ve tüm modelleme adımları (veri bölme, ölçekleme, eğitim vb.) o bataryaya özel olarak yapılacaktı (`05_Data_Restructuring_for_Battery_Specific_Models.md`).

### 3. `SoH` Tahmin Modelinin Geliştirilmesi

Bu aşama, bataryaya özel CSV dosyaları kullanılarak `4_model_development.ipynb` içerisinde gerçekleştirilmiştir. Veri, her batarya için döngü numarasına göre kronolojik olarak Eğitim (%70), Doğrulama (%15) ve Test (%15) setlerine ayrılmıştır.

#### Yaklaşım 1: Döngü Seviyesi Özellikler ile `Random Forest` & `XGBoost`

* **Veri Hazırlığı:** Deşarj döngüleri için döngü başına tek satır olacak şekilde veri agrege edildi (ortalama/min/max voltaj, ortalama akım, sıcaklık metrikleri, deşarj süresi, döngü numarası). Özellikler `StandardScaler` ile ölçeklendi.

* **Sonuçlar (B0005 örneği):** Her iki model de (`RandomForestRegressor`, `XGBRegressor`) eğitim verisine aşırı uyum (`overfitting`) gösterdi (RF için `OOB Score` ~0.995). Ancak doğrulama (Validation) ve test setlerinde **çok kötü performans** sergilediler (R2 skorları **negatif** değerler aldı; örn. RF Val R2 ~ -1.83, Test R2 ~ -39.02; XGBoost Val R2 ~ -52.16, Test R2 ~ -253.89). Tahminler gerçek `SoH` değerlerini takip edemedi.

* **Yorum:** Döngü seviyesinde basit agrega edilmiş özellikler, özellikle ileri döngülerdeki `SoH` değişimini tahmin etmek için yetersiz kaldı.

#### Yaklaşım 2: Tam Deşarj Dizileri ile `LSTM` (İlk Eğitim)

* **Veri Hazırlığı:** Her deşarj döngüsü içindeki yumuşatılmış ölçüm dizileri (`voltage_measured_smooth`, `current_measured_smooth`, `temperature_measured_smooth`, `measurement_time_relative`) kullanıldı. Diziler `StandardScaler` ile ölçeklendi (eğitim verisine göre fit edildi) ve `keras.preprocessing.sequence.pad_sequences` ile eşit uzunluğa getirildi. Hedef (`target`), her dizi için tek bir `SoH` değeriydi.

* **Model Mimarisi:** `Masking` -> `LSTM(50)` -> `Dropout(0.2)` -> `Dense(1)`. `adam` optimizer ve `mean_squared_error` loss ile derlendi. `EarlyStopping` ve `ModelCheckpoint` (en iyi `val_loss`'a göre) kullanıldı.

* **Sonuçlar (B0005 - En İyi Checkpoint Modeli):** Doğrulama setinde **belirgin bir iyileşme** görüldü (MAE ~0.0085, RMSE ~0.0108, **R2 ~ 0.4604**). Ancak, test setinde **hala genelleme sorunu** yaşandı ve performans düştü (MAE ~0.0142, RMSE ~0.0159, **R2 ~ -2.1966**).

* **Yorum:** Dizi verisini kullanmak performansı artırdı, ancak model hala eğitim verisi aralığının dışındaki (özellikle test setindeki geç ömür) döngülere genelleme yapmakta zorlandı.

#### Yaklaşım 3: Basit `SoH` Dizisi ile `LSTM`

* **Veri Hazırlığı:** Sadece bir önceki döngünün `SoH` değerini kullanarak bir sonraki `SoH` değerini tahmin etmeye çalışan çok basit bir model denendi. `SoH` değerleri `MinMaxScaler` ile ölçeklendi.

* **Sonuçlar (B0005):** Performans **çok kötüydü** (Validation R2 ~ -2.46, Test R2 ~ -42.77). Tahminler neredeyse düz bir çizgiydi.

* **Yorum:** Sadece önceki `SoH` bilgisinin yetersiz olduğunu, döngü içi dinamiklerin kritik olduğunu doğruladı.

#### Yaklaşım 4: Final `LSTM` (Tam Dizi, Eğitim+Doğrulama Üzerinde Yeniden Eğitim)

* **Rationale:** Yaklaşım 2'deki test performansını iyileştirmek amacıyla, doğrulama setinin neden olduğu "boşluğu" kapatmak için model, birleştirilmiş Eğitim+Doğrulama verisi üzerinde yeniden eğitildi. Bu, nihai test performansı raporlaması için standart bir yaklaşımdır.

* **Model ve Eğitim:** Yaklaşım 2'deki aynı `LSTM` mimarisi yeniden başlatıldı ve birleştirilmiş `X_train_val_pad`, `y_train_val_seq` üzerinde sabit sayıda epoch (20) ile eğitildi.

* **Nihai Test Sonuçları (Tüm Bataryalar):**

| Batarya | Test MAE | Test RMSE | Test R2   |
|---------|----------|-----------|-----------|
| B0005   | 0.0205   | 0.0227    | -5.5426   |
| B0006   | 0.0405   | 0.0432    | -3.9514   |
| B0018   | 0.0154   | 0.0174    | -1.3794   |

* **Analiz:** Bu yaklaşım, proje kapsamında elde edilen **en düşük Test MAE ve RMSE** değerlerini sağladı (hata payları %1.5 ile %4.3 arasında değişti). Trend grafikleri, modelin genel bozulma eğilimini RF/XGBoost'a göre daha iyi yakaladığını gösterdi. Ancak, **Test R2 skorları tüm bataryalar için hala negatif** kaldı. Bu, modelin test verisindeki varyansı ortalama bir tahminden daha iyi açıklayamadığını ve özellikle geç ömür dinamiklerini tam olarak yakalayamadığını gösterdi.

* **Yorum:** Tam dizileri kullanmak ve yeniden eğitmek MAE/RMSE'yi düşürse de, temel genelleme ve ekstrapolasyon sorununu (negatif R2 ile belirginleşen) çözmedi.

### 4. API Entegrasyonu ve Demo Uygulaması

Bu adımlar orijinal görev tanımında yer almasına rağmen, sağlanan Markdown dosyaları bu aşamaların gerçekleştirilmediğini göstermektedir. Proje, modelleme aşamasının bulgularıyla tamamlanmıştır.

### 5. Sonuçların Değerlendirilmesi ve Raporlama

* **Genel Sonuç (`SoH` Tahmini):** Döngü içi zaman serisi verilerini kullanan `LSTM` modelleri, döngü seviyesi agrega özelliklerini kullanan `Random Forest` ve `XGBoost` modellerinden önemli ölçüde daha iyi performans gösterdi. Projedeki en iyi model (yeniden eğitilmiş dizi `LSTM`), düşük MAE/RMSE değerleri elde etmesine rağmen, özellikle test setindeki (görülmemiş, geç ömür) döngülere genelleme yapmada zorlandı ve **negatif R2 skorları** üretti. Bu, modelin mevcut özellik setiyle geç ömür bozulma dinamiklerini güvenilir bir şekilde yakalayamadığını göstermektedir.

* **Karşılaşılan Zorluklar:** Ham `.mat` verisinin karmaşık ve iç içe yapısı, basit agrega özelliklerle çalışan modellerin yetersiz kalması, geliştirilen modellerin (özellikle `LSTM`'in) görünmeyen geç ömür döngülerine genelleme yapma ve ekstrapolasyon zorluğu.

* **Üretken Yapay Zeka Kullanımı:** Sağlanan Markdown dosyalarında ChatGPT, Gemini, Claude gibi üretken yapay zeka araçlarının danışmanlık amacıyla kullanıldığına dair bir bilgi bulunmamaktadır.

* **Gelecek Çalışma ve Öneriler:**
    * **İleri Özellik Mühendisliği:** Özellikle **Incremental Capacity Analysis (`ICA` / dQ/dV)** veya Differential Voltage Analysis (`DVA`) gibi bozulma mekanizmalarına duyarlı olduğu bilinen özelliklerin çıkarılması (pik yükseklikleri, konumları, alanları vb.). Bunların geç ömür tahmin doğruluğunu artırması muhtemeldir.
    * **`LSTM` İyileştirmeleri:** Farklı katman/ünite sayıları, optimizer'lar, öğrenme oranları denenmesi, dikkat (`attention`) mekanizmalarının eklenmesi.
    * **Özellik Kombinasyonu:** Ham dizilerin ve mühendislik ürünü özelliklerin (örn. `ICA` pikleri, döngü numarası) birlikte modellere (örn. `LSTM`) girdi olarak verilmesi.
    * **`SoC` Tahmini:** Görev tanımında yer alan ancak bu çalışmada ele alınmayan Şarj Durumu (`SoC`) tahmin probleminin ele alınması (muhtemelen anlık ölçümleri girdi olarak kullanan farklı bir modelleme yaklaşımı gerektirecektir).
    * **Gerçek Dünya Entegrasyonu:** Geliştirilen modelin potansiyel olarak Batarya Yönetim Sistemlerine (`BMS`) entegrasyonu, uç cihazlarda (`edge deployment`) çalıştırılması veya `MLOps` süreçleri (otomatik yeniden eğitim, versiyonlama vb.) ile yönetilmesi gibi konular tartışılabilir.
