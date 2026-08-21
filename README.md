# Hand Tracking - Minimal

Webcam üzerinden işaret parmağı ucunu takip eden, çok düşük sistem kaynağı
kullanan, tamamen offline çalışan minimal bir uygulama. Parmak ekrandaki 3
basit daireden birine yaklaşınca daire renk değiştirir.

## Proje dosya yapısı

```
hand_tracking_app/
├── main.py              # Tkinter arayüzü + kamera döngüsü + daire etkileşimi
├── hand_tracker.py       # MediaPipe HandLandmarker sarmalayıcısı
├── requirements.txt      # opencv-python, mediapipe
├── hand_landmarker.task   # (indirilecek) el algılama modeli, ~8MB
└── README.md
```

## Kurulum

```bash
cd hand_tracking_app
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Model dosyasını indirme (tek seferlik)

Uygulama, Google'ın küçük (float16, ~8MB) el algılama modelini kullanır.
Bu dosya **sadece bir kere** indirilmeli; sonrasında uygulama tamamen
offline çalışır (webcam görüntüsü veya tracking verisi hiçbir zaman
internete gönderilmez).

```bash
# hand_tracking_app klasörünün içindeyken:
curl -L -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

(Windows'ta `curl` yoksa dosyayı tarayıcıdan indirip `hand_tracking_app`
klasörüne `hand_landmarker.task` adıyla koyabilirsiniz.)

## Çalıştırma

```bash
python main.py
```

Açılan pencerede **"Start Camera"** butonuna basın. Webcam görüntüsü
üzerinde 3 daire ve parmak ucunuzu gösteren kırmızı bir nokta göreceksiniz.
İşaret parmağınızı bir dairenin üzerine getirdiğinizde daire yeşile dönüp
dolacaktır. **"Stop Camera"** ile kamerayı tamamen kapatabilirsiniz.

## Gereksinimler

- Python 3.9 – 3.12 (MediaPipe'ın güncel sürümleri bu aralığı destekler)
- Bir webcam
- Model indirme için tek seferlik internet bağlantısı (sonrasında gerekmez)

## Neden bu teknolojiler?

- **OpenCV**: kamera erişimi + basit çizim için en hafif, standart seçenek.
- **MediaPipe HandLandmarker (Tasks API)**: CPU üzerinde çalışan, küçük
  (~8MB) bir TFLite modeli kullanır. Eski `mp.solutions.hands` API'si 2023'ten
  beri "legacy" durumda ve güncel MediaPipe sürümlerinde bazen hiç
  çalışmıyor; bu yüzden güncel ve desteklenen Tasks API'si tercih edildi.
- **Tkinter**: Python ile birlikte gelir, Electron/Qt gibi ağır bir GUI
  framework'üne ihtiyaç yoktur.
- **Pillow kullanılmadı**: Görüntüyü Tkinter'a aktarmak için numpy
  dizisi doğrudan ham PPM byte formatına çevrilip veriliyor — ekstra bir
  bağımlılık eklemeden aynı sonucu veriyor.

## Performans optimizasyonları (uygulanan)

- Kamera 640x480 çözünürlükte, 30 FPS'te çalışır (daha yükseği kullanılmaz).
- El takibi her kamera frame'inde değil, 2 frame'de bir (~15 FPS) çalışır;
  aradaki frame'lerde son bilinen parmak konumu kullanılır, bu yüzden
  hareket akıcı görünür ama CPU yükü yarı yarıya azalır.
- Tek el takibi (`num_hands=1`), ikinci el aranmaz.
- Sadece işaret parmağı ucu (landmark 8) okunur, 21 landmark'ın tamamı
  işlenmez/çizilmez.
- Görüntü kopyalama/format dönüşümü minimumda tutulur (sadece BGR→RGB
  dönüşümü gerektiği için yapılır).
- Basit çarpışma kontrolü: `distance(parmakUcu, daireMerkezi) < yarıçap`
  — hiçbir physics/game engine yok.
- Kamera kapatıldığında `cap.release()` ve `detector.close()` ile tüm
  kaynaklar hemen serbest bırakılır.
- Thread kullanılmaz: bu ölçekte bir uygulama için thread eklemek
  gereksiz karmaşıklık katardı; kamera okuma + tracking gecikmesi bu
  frame hızında arayüzü fark edilir şekilde dondurmaz.

## RAM/CPU kullanımını test etme

Uygulamaya ekstra bir bağımlılık (ör. `psutil`) eklemek yerine işletim
sisteminizin kendi araçlarını kullanabilirsiniz:

- **Windows**: Görev Yöneticisi (Task Manager) → "python.exe" işlemini bulun,
  Bellek (RAM) ve CPU sütunlarına bakın.
- **macOS**: Activity Monitor → "Python" işlemini arayın.
- **Linux**: `htop` veya `top` çalıştırıp `python` işlemini bulun; ya da:
  ```bash
  ps -o pid,rss,%cpu,cmd -p $(pgrep -f main.py)
  ```
  (`RSS` sütunu kilobayt cinsinden gerçek RAM kullanımını gösterir.)

Beklenen değerler: kamera açıkken yaklaşık 150–400MB RAM, tek çekirdekte
%10–30 CPU civarı (donanıma göre değişir). 2GB sınırının oldukça altında
kalması beklenir.

## Bilinen sınırlamalar (kasıtlı olarak basit tutuldu)

- Sadece tek el takip edilir.
- Sadece işaret parmağı ucu takip edilir, gesture/pose tanıma yoktur.
- "Webcam bulunamadı" ve "izin verilmedi" ayrımı, OpenCV'nin platformlar
  arası sınırlı hata bilgisi nedeniyle kesin değildir; en yaygın iki
  senaryoyu (kamera açılamıyor / açılıyor ama frame okunamıyor) kapsar.
