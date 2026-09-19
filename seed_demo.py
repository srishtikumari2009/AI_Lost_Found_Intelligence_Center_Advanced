from database import Database, BASE_DIR
from pathlib import Path

db=Database()
if db.stats()["total"]>0:
    print("Database already contains records. No demo data inserted.")
else:
    lost=BASE_DIR/"images"/"lost"
    found=BASE_DIR/"images"/"found"
    lost_imgs=list(lost.glob("*"))
    found_imgs=list(found.glob("*"))
    if lost_imgs:
        db.add_item("Lost","Demo Lost Bag","Sample lost-item report for demonstration.",
                    "Lucknow","2026-08-31","demo@example.com",str(lost_imgs[0]))
    if found_imgs:
        db.add_item("Found","Demo Found Bag","Sample found-item report for demonstration.",
                    "Lucknow","2026-08-31","demo@example.com",str(found_imgs[0]))
    print("Demo data inserted. Start main.py and open AI Match.")
db.close()
