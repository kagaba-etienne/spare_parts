from app.db import Session
from app.db.models import Part, Accessory

session = Session()

parts = session.query(Part).all()
accessories = session.query(Accessory).all()

i = 0
for part in parts:
    fitments = part.fits
    sub_cat = part.subcategory

    for fitment in fitments:
        print(f'{i}-th fitment')
        fitment.parts_subcategories.append(sub_cat)
        session.commit()
        i += 1


j = 0
print('\n\n\n\n')
for accessory in accessories:
    fitments = accessory.fits
    sub_cat = accessory.subcategory
    for fitment in fitments:
        print(f'{j}-th fitment')
        fitment.acc_subcategories.append(sub_cat)
        session.commit()
        j += 1

session.close()
