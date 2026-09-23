import json
import google.generativeai as genai
from PIL import Image

SYSTEM_PROMPT = """
Sen savdo nakladnoylarini (Товарная накладная) tahlil qiluvchi AI tizimsan.
Rasmdan quyidagi barcha maydonlarni aniq ajratib ol va strictly JSON formatida qaytar.

Agar ma'lumot ko'rinmasa null qiymat ber.
Format:
{
  "invoice_number": "2533838383",
  "date": "11.08.2026",
  "supplier": {
    "name": "ZAMIN DRINKS OOO",
    "inn": "311215785",
    "address": "NAMANGAN POP T.ANXOR MFY MAYDON.K 26",
    "phone": null
  },
  "customer": {
    "name": "BARAKA-NURLI SAVDO MCHJ",
    "client_code": "1775100174",
    "inn": "00000305891771",
    "address": "TOSH.SHAYXONTOHUR, BUNYODKOR-"
  },
  "sales_agent": "BARDABAYEV ALEKSANDR",
  "expediter": "DALIBAYEV MIRJALOL",
  "items": [
    {
      "code": "641526",
      "name": "FUS MANGO CH-E PET 0,5L 1X12 SAM",
      "unit": "Case",
      "quantity": 2.0,
      "unit_price": 70308.0,
      "line_total": 140616.0
    }
  ],
  "total_qty": 10.0,
  "total_sum": 596293.60
}
Faqat va faqat valid JSON qaytar, qo'shimcha text yoki markdown tushuntirish yozma!
"""

class GeminiOCR:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def parse_invoice_image(self, image_bytes: bytes) -> dict:
        import io
        img = Image.open(io.BytesIO(image_bytes))
        
        response = self.model.generate_content([SYSTEM_PROMPT, img])
        text = response.text.strip()
        
        # JSON tozalash
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text.strip())