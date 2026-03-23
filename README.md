# AmazonClone: Multi-Vendor E-Commerce Platform

A fully-featured, Amazon-like multi-vendor e-commerce platform built with Django, HTMX, and Bootstrap 5.

🌐 **Live Demo:** [https://small-clowns-marry.loca.lt](https://small-clowns-marry.loca.lt)
*(Note: If prompted by Localtunnel, click "Click to Continue" to view the site.)*

## 🚀 Features

### Frontend (Amazon-inspired UI)
- **Dynamic Homepage**: Featured products and category blocks.
- **Product Discovery**: Search and filter by category, price, and rating.
- **Shopping Cart**: Real-time quantity updates and subtotal calculation (HTMX).
- **Checkout Flow**: Secure multi-step checkout simulation.
- **Buyer Dashboard**: Order history with interactive tracking timelines.

### Seller Dashboard (Seller Central)
- **Store Management**: Register as a seller and manage business details.
- **Product Management**: CRUD operations for products with multi-image support.
- **Order Management**: Track and update status for orders received.
- **Analytics**: High-level overview of sales and active inventory.

### Core Infrastructure
- **Custom User Model**: Role-based access (Buyer, Seller, Admin).
- **Stripe Integration**: Backend support for Stripe Checkout and Stripe Connect (marketplace payouts).
- **Dummy Data**: Custom management command to seed the database with realistic products and images.

## 🛠️ Tech Stack
- **Backend**: Django 5.x, Django REST Framework
- **Frontend**: Django Templates, HTMX, Bootstrap 5, Vanilla CSS
- **Database**: SQLite (Development)
- **Tools**: WhiteNoise (static files), Decouple (env management), Pillow (images)

## 💻 Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AbhishekN578/E-commerce.git
   cd E-commerce
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**:
   ```bash
   python manage.py migrate
   python manage.py populate_dummy_data
   ```

4. **Run Server**:
   ```bash
   python manage.py runserver
   ```

Access the application at `http://localhost:8000`.

## 👤 Credentials
- **Admin/Seller**: `admin@ecommerce.com` / `admin123`

---
*Built as a high-performance, scaleable marketplace demonstration.*
