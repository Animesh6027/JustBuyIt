JustBuyIt

An E-commerce Web Application — A dynamic online shopping platform built with Django, enabling seamless product browsing, cart management, and secure checkout experience.

Overview

JustBuyIt delivers a user-friendly interface for shopping that supports category-based navigation, session-driven cart management, and order placement—all wrapped in a responsive, Tailwind-powered design. It’s a great showcase of full-stack development using modern web practices.

Key Goals

Enable smooth product browsing with categorization and filtering.

Offer robust cart functionality—add, update, or remove items, all managed within user sessions.

Support secure user authentication for personalized experiences.

Provide a responsive UI, ensuring accessibility on mobile, tablet, and desktop devices.

Features

Category & Subcategory Navigation – Users can easily filter and explore products by categories.

Product Detail View – Displays comprehensive product information in a clean, structured layout.

Shopping Cart – Supports adding items, adjusting quantities, and removing products, all session-stored for consistency across visits.

User Authentication – Registration and login functionality to manage user sessions and secure access.

Checkout Flow – Streamlined process for placing orders (with potential for future payment integration).

Responsive UI – Tailwind CSS ensures the interface adapts fluidly across screen sizes.

Template-based Architecture – Django templates maintain modularity and readability.

CRUD Operations – Full create, read, update, and delete capabilities for products and cart items.

Session Management – Utilizes Django’s session framework to preserve cart state, even for non-logged-in users.

Tech Stack & Tools

Backend: Python, Django (ORM, Views, Templates, Authentication)

Database: SQLite (via Django ORM)

Frontend: Tailwind CSS, Django Templates

Environment: Python virtual environments, requirements.txt for dependencies

Deployment: Instructions provided in DEPLOYMENT_GUIDE.md, with environment setup via env_example.txt

Getting Started

Clone the Repository

git clone https://github.com/Animesh6027/justbuyit.git
cd justbuyit


Set Up the Environment

Copy env_example.txt to create your .env file and configure required environment variables.

Create a virtual environment and install dependencies:

python3 -m venv env
source env/bin/activate
pip install -r requirements.txt


Run the Application

python manage.py migrate
python manage.py runserver


Visit http://127.0.0.1:8000/ in your browser.

Feel free to let me know if you'd like a concise summary version formatted for your portfolio or CV—it can include around 2–3 lines highlighting the most impactful aspects of the project!
