from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import csv
from io import StringIO
from flask import Response

app = Flask(__name__)
app.secret_key = "atm_secret_key"  # For session management and flash messages

# Simulated user data
account = {
    "pin": "1234",  # Default PIN
    "balance": 500.0,
    "transactions": []  # To store transaction logs
}

@app.route("/", methods=["GET", "POST"])
def login():
    """Handle PIN authentication."""
    if request.method == "POST":
        pin = request.form.get("pin")
        if pin == account["pin"]:
            session["authenticated"] = True
            flash("Authentication successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid PIN. Please try again.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log out the user by clearing the session."""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/home")
def index():
    """ATM homepage."""
    if not session.get("authenticated"):
        flash("Please log in to access the ATM.", "error")
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route("/balance")
def balance():
    """Display the user's current balance."""
    if not session.get("authenticated"):
        flash("Please log in to access the ATM.", "error")
        return redirect(url_for("login"))
    return render_template("balance.html", balance=account["balance"])


@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    """Handle deposits."""
    if not session.get("authenticated"):
        flash("Please log in to access the ATM.", "error")
        return redirect(url_for("login"))
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
            if amount <= 0:
                flash("Amount must be greater than zero.", "error")
            else:
                account["balance"] += amount
                # Log the transaction
                account["transactions"].append({
                    "type": "Deposit",
                    "amount": amount,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                flash(f"${amount:.2f} deposited successfully!", "success")
                return redirect(url_for("balance"))
        except ValueError:
            flash("Invalid input. Please enter a number.", "error")
    return render_template("deposit.html")


@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    """Handle withdrawals."""
    if not session.get("authenticated"):
        flash("Please log in to access the ATM.", "error")
        return redirect(url_for("login"))
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
            if amount <= 0:
                flash("Amount must be greater than zero.", "error")
            elif amount > account["balance"]:
                flash("Insufficient funds.", "error")
            else:
                account["balance"] -= amount
                # Log the transaction
                account["transactions"].append({
                    "type": "Withdrawal",
                    "amount": amount,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                flash(f"${amount:.2f} withdrawn successfully!", "success")
                return redirect(url_for("balance"))
        except ValueError:
            flash("Invalid input. Please enter a number.", "error")
    return render_template("withdraw.html")


@app.route("/statement")
def statement():
    """Display the transaction statement."""
    if not session.get("authenticated"):
        flash("Please log in to access the ATM.", "error")
        return redirect(url_for("login"))
    return render_template("statement.html", transactions=account["transactions"])



@app.route("/download_statement")
def download_statement():
    """Generate and download the transaction statement as a CSV file."""
    if not session.get("authenticated"):
        flash("Please log in to access the ATM.", "error")
        return redirect(url_for("login"))
    
    # Prepare the CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Transaction Type", "Amount"])  # Header row
    
    for transaction in account["transactions"]:
        writer.writerow([transaction["date"], transaction["type"], transaction["amount"]])
    
    # Create a downloadable response
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=transaction_statement.csv"}
    )

    

if __name__ == "__main__":
    app.run(debug=True)
