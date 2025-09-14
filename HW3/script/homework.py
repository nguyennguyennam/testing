import csv
import random
from datetime import datetime, timedelta
from faker import Faker
import hashlib
import sys

# Initialize Faker for generating realistic data with general locales.
fake = Faker(['en_US', 'en_GB', 'en_AU', 'de_DE'])

# Create separate Faker instances specifically for highly locale-specific methods
vietnam_fake = Faker('vi_VN')
canada_fake = Faker('en_CA') 


# --- Global lists to store generated IDs for foreign key relationships ---
user_ids = []
category_ids = []
product_ids = []
invoice_ids = []
brand_ids = []

# --- Predefined Vietnamese address components ---
vietnamese_wards = [
    "Ben Thanh Ward", "Pham Ngu Lao Ward", "Tan Dinh Ward", 
    "Ward 1", "Ward 2", "Ward 3", "Ward 4", "Ward 5", "Ward 6", 
    "Ward 7", "Ward 8", "Ward 9", "Ward 10", "Ward 11", "Ward 12",
    "Ward 13", "Ward 14", "Ward 15", "Ward 16", "Ward 17", "Ward 18",
    "Phu My Hung Ward", "Thao Dien Ward", "An Phu Ward" # Example additional wards
]

vietnamese_districts = [
    "District 1", "District 3", "District 4", "District 5", "District 6", 
    "District 7", "District 8", "District 10", "District 11", "District 12",
    "Go Vap District", "Binh Thanh District", "Tan Binh District", 
    "Phu Nhuan District", "Thu Duc City", "Binh Tan District", "Tan Phu District",
    "Nha Be District", "Binh Chanh District", "Cu Chi District" # Example additional districts
]


def generate_users(num_users):
    """Generates user data."""
    global user_ids
    headers = [
        'id', 'first_name', 'last_name', 'address', 'city', 'state', 'country',
        'postcode', 'phone', 'dob', 'email', 'password', 'role', 'enabled',
        'failed_login_attempts', 'created_at', 'updated_at'
    ]
    data = []
    for i in range(1, num_users + 1):
        user_id = i
        user_ids.append(user_id)
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        # Randomly choose a country for more varied addresses
        country = random.choice(['United States', 'United Kingdom', 'Canada', 'Australia', 'Vietnam', 'Germany'])
        
        address_info = {}
        if country == 'United States':
            address_info = {
                'address': fake.street_address(),
                'city': fake.city(),
                'state': fake.state_abbr(),
                'postcode': fake.postcode(),
                'phone': fake.phone_number()
            }
        elif country == 'United Kingdom':
            address_info = {
                'address': fake.street_address(),
                'city': fake.city(),
                'state': 'NULL',
                'postcode': fake.postcode(),
                'phone': fake.phone_number()
            }
        elif country == 'Canada':
            # Generate random Canadian-style postcode
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            numbers = "0123456789"
            canadian_postcode = (
                random.choice(letters) + 
                random.choice(numbers) + 
                random.choice(letters) + 
                " " + 
                random.choice(numbers) + 
                random.choice(letters) + 
                random.choice(numbers)
            )
            address_info = {
                'address': canada_fake.street_address(),
                'city': canada_fake.city(),
                'state': canada_fake.province_abbr(),
                'postcode': canadian_postcode,
                'phone': canada_fake.phone_number()
            }
        elif country == 'Australia':
            address_info = {
                'address': fake.street_address(),
                'city': fake.city(),
                'state': fake.state_abbr(),
                'postcode': fake.postcode(),
                'phone': fake.phone_number()
            }
        elif country == 'Vietnam':
            # Generate random 5-digit postcode for Vietnam
            vietnam_postcode = f"{random.randint(10000, 99999)}"
            # Use predefined wards and districts
            random_ward = random.choice(vietnamese_wards)
            random_district = random.choice(vietnamese_districts)
            address_info = {
                'address': f"{random.randint(1, 300)} {vietnam_fake.street_name()}, {random_ward}, {random_district}",
                'city': vietnam_fake.city(), # Still use vietnam_fake for city
                'state': 'NULL',
                'postcode': vietnam_postcode,
                'phone': f"84{random.randint(100000000, 999999999)}"
            }
        elif country == 'Germany':
            address_info = {
                'address': fake.street_address(),
                'city': fake.city(),
                'state': 'NULL',
                'postcode': fake.postcode(),
                'phone': fake.phone_number()
            }
            
        dob = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d')
        email = f"{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}"
        password = hashlib.sha256("password123".encode()).hexdigest()
        role = 'user'
        enabled = 1
        failed_login_attempts = 0
        created_at = 'NULL'
        updated_at = 'NULL'

        data.append([
            user_id, first_name, last_name, address_info['address'], address_info['city'], address_info['state'], country,
            address_info['postcode'], address_info['phone'], dob, email, password, role, enabled,
            failed_login_attempts, created_at, updated_at
        ])
    return headers, data


def generate_categories(num_categories):
    """Generates category data."""
    global category_ids
    headers = [
        'id', 'parent_id', 'name', 'slug', 'created_at', 'updated_at'
    ]
    data = []
    
    base_categories_and_slugs = [
        ("Hand Tools", "hand-tools"), 
        ("Power Tools", "power-tools"), 
        ("Hammer", "hammer"),
        ("Hand Saw", "hand-saw"),
        ("Wrench", "wrench"),
        ("Screwdriver", "screwdriver"),
        ("Pliers", "pliers"),
        ("Grinder", "grinder"),
        ("Sander", "sander"),
        ("Saw", "saw"),
        ("Drill", "drill"),
        ("Other", "other")
    ]
    
    for i in range(1, num_categories + 1):
        category_id = i
        category_ids.append(category_id)
        
        if i <= len(base_categories_and_slugs):
            name, slug = base_categories_and_slugs[i-1]
        else:
            name = fake.unique.word().capitalize() + " Category"
            slug = name.lower().replace(' ', '-')
        
        parent_id = 'NULL'
        if name in ["Hammer", "Hand Saw", "Wrench", "Screwdriver", "Pliers"] and category_ids and 1 in category_ids:
            parent_id = 1
        elif name in ["Grinder", "Sander", "Saw", "Drill"] and category_ids and 2 in category_ids:
            parent_id = 2
        elif category_ids and random.random() < 0.2 and len(category_ids) > 1:
            parent_id = random.choice([cid for cid in category_ids if cid != category_id])
        
        created_at = 'NULL'
        updated_at = 'NULL'

        data.append([
            category_id, parent_id, name, slug, created_at, updated_at
        ])
    return headers, data

def generate_brands(num_brands):
    """Generates brand data."""
    global brand_ids
    headers = [
        'id', 'name', 'slug', 'created_at', 'updated_at'
    ]
    data = []
    
    base_brands = ["Brand name 1", "Brand name 2", "ToolMaster", "PowerCraft", "DIYPro"]
    
    for i in range(1, num_brands + 1):
        brand_id = i
        brand_ids.append(brand_id)
        
        if i <= len(base_brands):
            name = base_brands[i-1]
        else:
            name = fake.unique.company() + " Tools"
        
        slug = name.lower().replace(' ', '-')
        created_at = 'NULL'
        updated_at = 'NULL'

        data.append([
            brand_id, name, slug, created_at, updated_at
        ])
    return headers, data


def generate_products(num_products):
    """Generates product data."""
    global product_ids
    if not category_ids:
        print("Please generate categories first to create products.")
        return [], []
        
    headers = [
        'id', 'category_id', 'name', 'description', 'price', 'sku',
        'quantity', 'status', 'created_at', 'updated_at'
    ]
    
    if brand_ids:
        headers.insert(2, 'brand_id')
    
    data = []
    for i in range(1, num_products + 1):
        product_id = i
        product_ids.append(product_id)
        category_id = random.choice(category_ids)
        name = fake.catch_phrase() + " " + fake.word().capitalize()
        description = fake.paragraph(nb_sentences=3)
        price = round(random.uniform(5.00, 1000.00), 2)
        sku = f"PROD-{product_id:04d}-{random.randint(100,999)}"
        quantity = random.randint(0, 500)
        status = 1
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        row = [
            product_id, category_id, name, description, price, sku,
            quantity, status, created_at, updated_at
        ]
        
        if brand_ids:
            brand_id = random.choice(brand_ids) if random.random() < 0.7 else 'NULL'
            row.insert(2, brand_id)
            
        data.append(row)
    return headers, data


def generate_product_images(num_product_images):
    """Generates product image data."""
    if not product_ids:
        print("Please generate products first to create product images.")
        return [], []

    headers = [
        'id', 'product_id', 'image_url', 'sort_order', 'is_thumbnail', 'created_at', 'updated_at'
    ]
    data = []
    
    product_sort_order = {}

    for i in range(1, num_product_images + 1):
        product_image_id = i
        product_id = random.choice(product_ids)
        
        if product_id not in product_sort_order:
            product_sort_order[product_id] = 0
        product_sort_order[product_id] += 1
        
        image_url = f"https://example.com/images/products/{product_id}_{product_sort_order[product_id]}.jpg"
        sort_order = product_sort_order[product_id]
        
        is_thumbnail = 1 if sort_order == 1 else random.choice([0, 1])
        
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        data.append([
            product_image_id, product_id, image_url, sort_order, is_thumbnail, created_at, updated_at
        ])
    return headers, data


def generate_invoices(num_invoices):
    """Generates invoice data."""
    global invoice_ids
    if not user_ids:
        print("Please generate users first to create invoices.")
        return [], []

    headers = [
        'id', 'user_id', 'invoice_date', 'invoice_number', 'billing_address',
        'billing_city', 'billing_state', 'billing_country', 'billing_postcode',
        'payment_method', 'payment_account_name', 'payment_account_number',
        'status', 'status_message', 'created_at', 'updated_at'
    ]
    data = []
    
    user_address_map = {}
    for uid in user_ids:
        country_for_user = random.choice(['United States', 'United Kingdom', 'Canada', 'Australia', 'Vietnam', 'Germany'])
        
        user_address_info = {}
        if country_for_user == 'United States':
            user_address_info = {
                'address': fake.street_address(), 'city': fake.city(), 'state': fake.state_abbr(),
                'country': country_for_user, 'postcode': fake.postcode()
            }
        elif country_for_user == 'United Kingdom':
            user_address_info = {
                'address': fake.street_address(), 'city': fake.city(), 'state': 'NULL',
                'country': country_for_user, 'postcode': fake.postcode()
            }
        elif country_for_user == 'Canada':
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            numbers = "0123456789"
            canadian_postcode = (
                random.choice(letters) + 
                random.choice(numbers) + 
                random.choice(letters) + 
                " " + 
                random.choice(numbers) + 
                random.choice(letters) + 
                random.choice(numbers)
            )
            user_address_info = {
                'address': canada_fake.street_address(), 'city': canada_fake.city(), 'state': canada_fake.province_abbr(),
                'country': country_for_user, 'postcode': canadian_postcode
            }
        elif country_for_user == 'Australia':
            user_address_info = {
                'address': fake.street_address(), 'city': fake.city(), 'state': fake.state_abbr(),
                'country': country_for_user, 'postcode': fake.postcode()
            }
        elif country_for_user == 'Vietnam':
            vietnam_postcode = f"{random.randint(10000, 99999)}"
            random_ward = random.choice(vietnamese_wards)
            random_district = random.choice(vietnamese_districts)
            user_address_info = {
                'address': f"{random.randint(1, 300)} {vietnam_fake.street_name()}, {random_ward}, {random_district}",
                'city': vietnam_fake.city(), 'state': 'NULL',
                'country': country_for_user, 'postcode': vietnam_postcode
            }
        elif country_for_user == 'Germany':
            user_address_info = {
                'address': fake.street_address(), 'city': fake.city(), 'state': 'NULL',
                'country': country_for_user, 'postcode': fake.postcode()
            }
        
        user_address_map[uid] = user_address_info


    for i in range(1, num_invoices + 1):
        invoice_id = i
        invoice_ids.append(invoice_id)
        user_id = random.choice(user_ids)
        
        invoice_date_dt = datetime.now() - timedelta(days=random.randint(1, 365))
        invoice_date = invoice_date_dt.strftime('%Y-%m-%d %H:%M:%S')
        
        invoice_number = f"INV-{invoice_date_dt.strftime('%Y%m%d')}-{random.randint(1000000, 9999999)}"
        
        billing_info = user_address_map.get(user_id, {
            'address': fake.street_address(), 'city': fake.city(), 'state': 'NULL',
            'country': random.choice(['United States', 'The Netherlands', 'Belgium']), 'postcode': fake.postcode()
        })

        payment_method = random.choice(['Cash On Delivery', 'Bank Transfer', 'Credit Card'])
        payment_account_name = fake.name() if payment_method == 'Bank Transfer' else 'Tester'
        payment_account_number = fake.bban() if payment_method == 'Bank Transfer' else '09076540ABC'
        
        status = random.choice(['AWAITING_FULFILLMENT', 'ON HOLD', 'COMPLETED', 'CANCELLED'])
        status_message = 'NULL'

        created_at = invoice_date
        updated_at = 'NULL'

        data.append([
            invoice_id, user_id, invoice_date, invoice_number, billing_info['address'],
            billing_info['city'], billing_info['state'], billing_info['country'], billing_info['postcode'],
            payment_method, payment_account_name, payment_account_number,
            status, status_message, created_at, updated_at
        ])
    return headers, data


def generate_invoice_items(num_invoice_items):
    """Generates invoice item data."""
    if not invoice_ids:
        print("Please generate invoices first to create invoice items.")
        return [], []
    if not product_ids:
        print("Please generate products first to create invoice items.")
        return [], []

    headers = [
        'id', 'invoice_id', 'product_id', 'unit_price', 'quantity',
        'created_at', 'updated_at'
    ]
    data = []
    
    product_price_map = {pid: round(random.uniform(5.00, 500.00), 2) for pid in product_ids}

    for i in range(1, num_invoice_items + 1):
        invoice_item_id = i
        invoice_id = random.choice(invoice_ids)
        product_id = random.choice(product_ids)
        quantity = random.randint(1, 5)
        unit_price = product_price_map.get(product_id, 0.00)
        
        created_at = (datetime.now() - timedelta(minutes=random.randint(1, 60))).strftime('%Y-%m-%d %H:%M:%S')
        updated_at = 'NULL'

        data.append([
            invoice_item_id, invoice_id, product_id, unit_price, quantity,
            created_at, updated_at
        ])
    return headers, data

def generate_contact_replies(num_replies):
    """Generates contact reply data."""
    if not user_ids:
        print("Please generate users first to create contact replies.")
        return [], []

    headers = [
        'id', 'contact_id', 'user_id', 'reply_message', 'replied_at', 'created_at', 'updated_at'
    ]
    data = []

    # Danh sách 5 phản hồi mặc định
    default_replies = [
        "Cảm ơn bạn đã liên hệ! Chúng tôi đã nhận được yêu cầu của bạn và sẽ phản hồi sớm nhất.",
        "Xin lỗi vì sự chậm trễ. Vấn đề của bạn đang được xử lý bởi đội ngũ hỗ trợ kỹ thuật của chúng tôi.",
        "Chúng tôi đã cung cấp giải pháp cho vấn đề của bạn. Vui lòng kiểm tra email của bạn để biết chi tiết.",
        "Để hiểu rõ hơn về vấn đề, bạn có thể cung cấp thêm thông tin không?",
        "Chúng tôi đang điều tra vấn đề này và sẽ cập nhật cho bạn ngay khi có thông tin mới."
    ]

    dummy_contact_ids = list(range(1, 101)) # Giả định có 100 contact_id

    for i in range(1, num_replies + 1):
        reply_id = i
        contact_id = random.choice(dummy_contact_ids)
        user_id = random.choice(user_ids)
        
        # Chọn ngẫu nhiên một phản hồi từ danh sách mặc định
        reply_message = random.choice(default_replies)
        
        replied_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        created_at = replied_at
        updated_at = 'NULL'

        data.append([
            reply_id, contact_id, user_id, reply_message, replied_at, created_at, updated_at
        ])
    return headers, data


def print_csv(headers, data):
    """Prints data in CSV format to stdout."""
    writer = csv.writer(sys.stdout)
    writer.writerow(headers)
    writer.writerows(data)


def main():
    
    table_name = input("Enter table name (users, category, brand, product, product_image, invoice, invoice_item, contact_reply): ").lower()
    num_data = int(input("Enter number of records to generate: "))

    headers = []
    data = []

    if table_name == 'users':
        headers, data = generate_users(num_data)
    elif table_name == 'category':
        headers, data = generate_categories(num_data)
    elif table_name == 'brand':
        headers, data = generate_brands(num_data)
    elif table_name == 'product':
        if not category_ids:
            print("Generating 10 categories first to ensure product data can be created...")
            cat_headers, cat_data = generate_categories(10)
        if not brand_ids:
            print("Generating 5 brands first to allow products to link to brands...")
            brand_headers, brand_data = generate_brands(5)
        headers, data = generate_products(num_data)
    elif table_name == 'product_image':
        if not product_ids:
            print("Generating 10 products first to ensure product image data can be created...")
            prod_headers, prod_data = generate_products(10)
        headers, data = generate_product_images(num_data)
    elif table_name == 'invoice':
        if not user_ids:
            print("Generating 10 users first to ensure invoice data can be created...")
            user_headers, user_data = generate_users(10)
        headers, data = generate_invoices(num_data)
    elif table_name == 'invoice_item':
        if not invoice_ids:
            print("Generating 10 invoices first to ensure invoice item data can be created...")
            inv_headers, inv_data = generate_invoices(10)
        if not product_ids:
            print("Generating 10 products first to ensure invoice item data can be created...")
            prod_headers, prod_data = generate_products(10)
        headers, data = generate_invoice_items(num_data)
    elif table_name == 'contact_reply':
        if not user_ids:
            print("Generating 10 users first to ensure contact reply data can be created...")
            user_headers, user_data = generate_users(10)
        headers, data = generate_contact_replies(num_data)
    else:
        print("Invalid table name. Please choose from: users, category, brand, product, product_image, invoice, invoice_item, contact_reply.")
        return

    if headers and data:
        print_csv(headers, data)
        print(f"\nGenerated {len(data)} records for the '{table_name}' table.")

if __name__ == "__main__":
    main()