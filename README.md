# Fourth-Wall
A compact, portable productivity companion inspired by ORV, featuring a touch OLED screen that displays animated characters and lets users set custom timers for study or workout sessions, log brief memos, and receive break reminders—all stored locally and packed into a stylish, Fourth Wall-themed case.

## 📦 Bill of Materials (BOM)

| Component                        | Description                                | Estimated Cost (USD)   | Notes | Link |
|----------------------------------|--------------------------------------------|------------------------|-------|------|
| Raspberry Pi Zero 2W             | Main processor board                       | Already owned          | Compact, low-power, runs Python | N/A |
| 2.8" TFT LCD with Touchscreen Breakout Board w/MicroSD Socket - ILI9341 | Touch display for UI| $26.99                 | Capacitive preferred for finger/stylus input | https://www.amazon.ca/dp/B0CD9NDSVN/ref=sspa_dk_detail_1?psc=1&pd_rd_i=B0CD9NDSVN&pd_rd_w=uZdOn&content-id=amzn1.sym.516c2169-755e-413a-a38a-68230f4ab66f&pf_rd_p=516c2169-755e-413a-a38a-68230f4ab66f&pf_rd_r=052SGRP9072K06PV0J9B&pd_rd_wg=BRKIS&pd_rd_r=b86eea06-6c8b-4f9e-af12-f157570f25c6&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWw |
| Digikey 1528-1119-ND             | Push button for power or action input      | $3.88                    | Used for turning on/start | https://www.digikey.ca/en/products/detail/adafruit-industries-llc/1119/7241449 |
| 3.7V 1200mAh flat LiPo cell      | Rechargeable power source                  | $11.75                   | Choose based on space and usage time | https://www.amazon.ca/063450-1200mAh-Polymer-Battery-Rechargeable/dp/B0BCJT5DGS?source=ps-sl-shoppingads-lpcontext&ref_=fplfs&psc=1&smid=A2SCFHO7ADYKAL&utm_source=chatgpt.com |
| TP4056 Charging Module           | Battery charger with protection            | $8.99                     | Enables USB recharging | https://www.amazon.ca/Battery-Charger-Charging-Protection-Functions/dp/B0CTG3W3VZ?source=ps-sl-shoppingads-lpcontext&ref_=fplfs&psc=1&smid=A15AU4KLTOGL5D&utm_source=chatgpt.com |
| MicroSD Card (16–32GB)           | Storage for OS + notes/memos               | Already owned          | Also boots RPi | N/A |
| Buzzer 12V – 12mm          | Audio output for timers                    | $0.12                   | PCB mountable | https://www.ktron.in/product/buzzer-12v-12mm-hydz-pcb-mountable/?utm_source=chatgpt.com&v=3e8d115eb4b3 |
| Stylus (optional)                          | Precision touch input                      | $2–5                   | Optional, so will not buy | N/A |
| 3D Printed Case                  | Custom case with Fourth Wall design        | Varies                 | Dual-design: paper stack chaos + clean UI | N/A |
| Misc. wires, headers, etc.       | For connecting components                  | <$3                    | Jumper wires, solder, etc. | N/A |

**Total Estimated Cost:** ~$45–60 (excluding 3D printing materials)
