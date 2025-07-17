🛍️ JustBuyIt — A Full-Stack E-Commerce Website
JustBuyIt is a modern and responsive e-commerce platform built with Django, PostgreSQL, and Tailwind CSS. It supports multi-role user management (Buyer & Supplier), product browsing, shopping cart, wishlist, product reviews, and more — all inspired by the UI/UX of platforms like Amazon and Flipkart.

📌 Features
👥 User Roles
Buyers: Browse, search, filter products, add to cart/wishlist, review products.

Suppliers: Add/edit/delete their own products.

Admins: Manage all data through Django admin.

🛒 Core Functionalities
🔎 Advanced Search with category/subcategory filters

📦 Product management by suppliers

❤️ Wishlist support

🛍️ Cart with quantity adjustment

🌟 Reviews and Ratings from buyers

🖼️ Image upload for products

📄 Bulk product upload via CSV

📱 Responsive and mobile-friendly

🌙 Dark mode toggle

🧑‍💻 Tech Stack
Layer	Technology
Backend	Django (Python)
Frontend	HTML, Tailwind CSS
Database	PostgreSQL
Admin Panel	Django Admin
Styling Tools	Tailwind, Gradient UI
Animation	AOS (Animate on Scroll)

📦 ER Diagram
plaintext
Copy
Edit
User (CustomUser)
│
├── id (PK)
├── username
├── email
├── password
└── role (buyer/supplier)

Category
├── id (PK)
└── name

Subcategory
├── id (PK)
├── name
└── category_id (FK)

Product
├── id (PK)
├── name
├── description
├── price
├── image
├── category_id (FK)
├── subcategory_id (FK)
└── supplier_id (FK → User)

CartItem
├── id (PK)
├── user_id (FK)
├── product_id (FK)
└── quantity

Wishlist
├── id (PK)
├── user_id (FK)
└── product_id (FK)

Review
├── id (PK)
├── product_id (FK)
├── user_id (FK)
├── rating
└── comment

Payment
├── id (PK)
├── user_id (FK)
├── product_id (FK)
├── amount
├── status
└── timestamp
📚 Future Enhancements
🧾 Razorpay/Stripe Payment Gateway Integration

📦 Order history & invoice download

🛠️ Supplier dashboard analytics

📬 Email notifications

🔒 2FA Authentication

🧑‍🎓 Project Developed By
Animesh Singh

A Django enthusiast building smart and user-friendly web apps.
