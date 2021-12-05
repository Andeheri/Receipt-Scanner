
import pytesseract as pt
from difflib import SequenceMatcher

# Location of the program tesseract
pt.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
# Extracts text from image
receipt = pt.image_to_string(r'C:\Users\ahe02\OneDrive - NTNU\Bilder\Programmering\BUNNPRIS\2.jpg')
lines = receipt.split("\n")
# The threshold of how similar two products needs to be
threshold = 0.9
num = 1

def similar(a, b):
    # Checks how similar two strings are
    return SequenceMatcher(None, a, b).ratio()

unsure = []
products = {} # {nr, price, <Pant>}

for i, line in enumerate(lines):
    # The point where the receipt is of no interest (For BUNNPRIS)
    if "MVA" in line and len(products.keys()) > 0:
        break
    elif "#" in line or "*" in line[:5]:
        product = line[line.index("#" if "#" in line else "*") + 1:]
        
        # Seperates price from product-name
        price = product[len(product) - (product[::-1].index(" ")):]
        
        if price.isalpha():
            # Price was not found
            unsure.append(product[:-1] if product[-1] == " " else product)
        else:
            product = product[:product.index(price) - 1]
            try:
                products[product][0] += 1
            except KeyError:
                found = False
                for j in products.keys():
                    # Checks if two products are similar
                    if similar(j, product) > threshold:
                        products[min(j, product)] = products.pop(j)
                        products[min(j, product)][0] += 1
                        found = True
                        break
                if found:
                    continue
                j = 0
                while True:
                    j += 1
                    if len(lines[i + j]) > 0:
                        break
                # Pant
                if "&" in lines[i + j] or "PANT" in lines[i + j]:
                    pant = lines[i + j][len(lines[i + j]) - (lines[i + j][::-1].index(" ")):]
                    # If cashier has multiplied the product
                    if "*" in lines[i + j + 1][5:]:
                        # Might break
                        num = int(lines[i + j + 1][lines[i + j + 1].index("*") + 1:])
                        price = float(lines[i + j + 1][:lines[i + j + 1].index(".") + lines[i + j + 1][lines[i + j + 1].index(".")].index(" ")])
                    else:
                        num = 1
                    try:
                        products[product] = [num, float(price), float(pant)]
                    except ValueError:
                        try:
                            products[product] = [num, float(price), None]
                        except ValueError:
                            print(f"No valid price found for product: {product}")
                # Pant absent
                else:
                    # If cashier has multiplied the product
                    if "*" in lines[i + 1][5:]:
                        # Might break
                        try:
                            num = int(lines[i + 1][lines[i + 1].index("*") + 1:])
                            price = float(lines[i + 1][:lines[i + 1].index(" ")])
                        except ValueError:
                            unsure.append(product)
                            continue
                    else:
                        num = 1
                    try:
                        products[product] = [num, float(price)]
                    except ValueError:
                        print(f"No valid price found for product: {product}")
# Loops over products that the prices were absent from
for u_product in unsure:
    for product in products.keys():
        # Checks if two products are similar
        if similar(u_product, product) > threshold:
            products[product][0] += 1
            products[min(u_product, product)] = products.pop(product)
            unsure.pop(unsure.index(u_product))
            break

print(products)
total = 0
for val in products.values():
    if len(val) == 2:
        total += val[0] * val[1]
    else:
        total += val[0] * (val[1] + val[2])
print(f"The total was: {total} kr.")
print(f"\nValues weren't found for the following products: {unsure}\nYou might want to retake the picture." if len(unsure) > 0 else "")