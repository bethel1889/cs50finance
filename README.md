Nexus Stock Trading App
This project is a stock trading application named Nexus, built using Flask, a lightweight Python web framework. It allows users to register, log in, buy and sell stocks, view their portfolio, and track their transaction history. The application integrates with a stock quote API to fetch real-time stock prices.

Features
User Authentication: Register and log in securely.
Buy Stocks: Purchase stocks by entering a stock symbol and the number of shares.
Sell Stocks: Sell previously purchased stocks.
Portfolio Overview: View the user's portfolio including stock symbols, shares owned, and the current market value.
Transaction History: Track all buying and selling activities.
Add Cash: Deposit additional cash into the user's account.
Real-time Stock Prices: Fetches the latest stock prices using an external API.
Custom Filters: Display prices in USD format.
Technologies Used
Backend: Flask, CS50 SQL Library, SQLite
Frontend: Jinja2 templating, HTML, CSS
Security: Werkzeug for password hashing
Session Management: Flask-Session
Installation
Prerequisites
Python 3.x
Flask
SQLite
CS50 Library for SQL
Setup
Clone the repository:

sh
Copy code
git clone https://github.com/yourusername/nexus-stock-trading-app.git
cd nexus-stock-trading-app
Install dependencies:

sh
Copy code
pip install -r requirements.txt
Set up the database:

sh
Copy code
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
Run the application:

sh
Copy code
flask run
Access the application:
Open your browser and navigate to http://127.0.0.1:5000

Usage
Register
Navigate to the /register route.
Enter a username and password.
Confirm the password and submit the form.
Login
Navigate to the /login route.
Enter your username and password.
Submit the form to log in.
Buy Stocks
Navigate to the /buy route.
Enter the stock symbol and the number of shares.
Submit the form to purchase the stock.
Sell Stocks
Navigate to the /sell route.
Select the stock symbol and enter the number of shares to sell.
Submit the form to sell the stock.
View Portfolio
Navigate to the / route.
View your portfolio including stock symbols, shares owned, and the current market value.
View Transaction History
Navigate to the /history route.
View all buying and selling activities.
Add Cash
Navigate to the /add_cash route.
Enter the amount of cash to add.
Submit the form to add cash to your account.
File Structure
arduino
Copy code
nexus-stock-trading-app/
├── static/
│   └── styles.css
├── templates/
│   ├── buy.html
│   ├── history.html
│   ├── index.html
│   ├── layout.html
│   ├── login.html
│   ├── quote.html
│   ├── quoted.html
│   ├── register.html
│   ├── sell.html
│   └── add_cash.html
├── .gitignore
├── app.py
├── helpers.py
├── finance.db
├── requirements.txt
└── README.md
Helper Functions
apology: Render an error message.
login_required: Decorator to ensure the user is logged in.
lookup: Fetch stock data using an external API.
usd: Format a value as USD.
check: Validate username and password during registration.
Contributing
Fork the repository.
Create a new branch (git checkout -b feature/your-feature-name).
Commit your changes (git commit -m 'Add some feature').
Push to the branch (git push origin feature/your-feature-name).
Open a pull request.
License
This project is licensed under the MIT License. See the LICENSE file for more details.

Acknowledgments
CS50's Introduction to Computer Science for the foundational project idea.
Flask and its community for the amazing framework.
The contributors and maintainers of the libraries and tools used in this project.