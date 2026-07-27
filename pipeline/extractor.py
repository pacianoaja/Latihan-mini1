from playwright.sync_api import sync_playwright

class PlaywrightExtractor:
    
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _block_aggressively(self, route):
        """
        Memblokir request aset visual (.png, .jpg, .css, .font) demi efisiensi.
        """
        resource_type = route.request.resource_type
        if resource_type in ["image", "stylesheet", "font", "media"]:
            route.abort()
        else:
            route.continue_()

    def extract_products(self, limit: int = 20) -> list[dict]:
        """
        Menjalankan Playwright Headless dan mengambil data mentah dari web target.
        """
        raw_products = []
        
        with sync_playwright() as p:
            # 1. Buka browser Chromium dalam mode Headless
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 2. Terapkan Route Blocking
            page.route("**/*", self._block_aggressively)
            
            try:
                print(f"[INFO] Mengakses target: {self.base_url}")
                page.goto(self.base_url, timeout=30000)
                
                # Mengambil semua elemen kartu produk
                product_elements = page.query_selector_all("article.product_pod")
                
                for idx, element in enumerate(product_elements):
                    if idx >= limit:
                        break
                    
                    # 3. Safe Extraction: Isolasi error per elemen
                    try:
                        # Judul & Link Detail
                        title_el = element.query_selector("h3 a")
                        title = title_el.get_attribute("title") if title_el else ""
                        
                        # Generate SKU dari judul/link (sebagai pengganti SKU unik web)
                        relative_url = title_el.get_attribute("href") if title_el else f"prod-{idx}"
                        sku = relative_url.split("/")[-2].replace("_", "-") if "/" in relative_url else f"SKU-{idx+1:03d}"
                        
                        # Harga
                        price_el = element.query_selector("p.price_color")
                        price = price_el.inner_text() if price_el else ""
                        
                        # Status Stok
                        stock_el = element.query_selector("p.instock.availability")
                        stock_status = stock_el.inner_text() if stock_el else ""
                        
                        # Rating (Tersimpan di kelas CSS, contoh: 'star-rating Three')
                        rating_el = element.query_selector("p.star-rating")
                        rating_class = rating_el.get_attribute("class") if rating_el else ""
                        rating = rating_class.replace("star-rating", "").strip() if rating_class else ""
                        
                        raw_products.append({
                            "sku": sku,
                            "title": title,
                            "price": price,
                            "stock_status": stock_status,
                            "rating": rating
                        })
                        
                    except Exception as e:
                        print(f"[WARN] Gagal mengekstrak elemen ke-{idx}: {e}")
                        continue  # Melanjutkan ke produk berikutnya tanpa menghentikan loop
                        
            except Exception as e:
                print(f"[ERROR] Kegagalan navigasi halaman: {e}")
            finally:
                browser.close()
                
        return raw_products