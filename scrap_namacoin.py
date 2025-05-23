from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# Setup webdriver otomatis
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Buka halaman target
driver.get('https://www.tradingview.com/')

# Tunggu halaman termuat
time.sleep(3)

# Klik tombol jika perlu
button_xpath = "/html/body/div[2]/div[3]/div[2]/div[2]/div/div/div/button[1]/span"
try:
    button = driver.find_element(By.XPATH, button_xpath)
    button.click()
except Exception as e:
    print(f"Gagal klik tombol: {e}")

# Tunggu halaman
time.sleep(2)

# Inisialisasi checker sekali di luar loop
class DuplicateChecker:
    def __init__(self, filename='kacau.txt'):
        self.filename = filename
        self.lines = set()
        self._load_lines()

    def _load_lines(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                for line in f:
                    self.lines.add(line.strip())

    def is_duplicate(self, text):
        return text in self.lines

    def add(self, text):
        if not self.is_duplicate(text):
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(text + '\n')
            self.lines.add(text)
            return True
        return False

checker = DuplicateChecker()

# Loop utama
for i in range(999999999):
    p = i + 1
    target_xpath = "/html/body/div[7]/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div/div[4]"

    try:
        # Cari elemen target dan scroll ke situ
        target_element = driver.find_element(By.XPATH, target_xpath)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_element)
    except Exception as e:
        print(f"Gagal scroll ke elemen di iterasi {i}: {e}")
        # Jika gagal scroll, bisa lanjut atau break
        # break
        continue

    try:
        # Ambil data dari halaman
        try:
            text_element = driver.find_element(By.XPATH, f'/html/body/div[7]/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div/div[4]/div/div/div[{p}]/div[1]/div[2]/div/span')
            coin = text_element.text
            print("Coin:", coin)
        except Exception as e:
            print(f"Gagal ambil coin di baris {p}: {e}")
            coin = ""

        try:
            text_element = driver.find_element(By.XPATH, f'/html/body/div[7]/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div/div[4]/div/div/div[{p}]/div[2]/div')
            pingping = text_element.text
            print("Pingping:", pingping)
        except Exception as e:
            print(f"Gagal ambil pingping di baris {p}: {e}")
            pingping = ""

        try:
            text_element = driver.find_element(By.XPATH, f'/html/body/div[7]/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div/div[4]/div/div/div[{p}]/div[3]/div[1]/div[1]')
            jenis = text_element.text
            print("Jenis:", jenis)
        except Exception as e:
            print(f"Gagal ambil jenis di baris {p}: {e}")
            jenis = ""

        try:
            text_element = driver.find_element(By.XPATH, f'/html/body/div[7]/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div/div[4]/div/div/div[{p}]/div[3]/div[1]/div[2]/div')
            broker = text_element.text
            print("Broker:", broker)
        except Exception as e:
            print(f"Gagal ambil broker di baris {p}: {e}")
            broker = ""

        # Buat string data yang akan disimpan
        coinku = f"{coin}:::{pingping}:::{jenis}:::{broker}"

        # Cek duplikasi dan simpan
        if not checker.is_duplicate(coinku):
            checker.add(coinku)
            print(f'[+] {p} get {coinku}')
        else:
            # Jika tidak ingin pesan, bisa dihapus
            pass

    except Exception as e:
        print(f"Terjadi error di iterasi {i}, baris {p}: {e}")

    # Optional: tambahkan delay agar tidak terlalu cepat

# Setelah loop selesai, tutup browser
driver.quit()