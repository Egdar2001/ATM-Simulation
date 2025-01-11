from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "atm_secret_key"  # For session management and flash messages

# Simulated user data
account = {
    "pin": "1234",  # Default PIN
    "balance": 500.0
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
                flash(f"${amount:.2f} withdrawn successfully!", "success")
                return redirect(url_for("balance"))
        except ValueError:
            flash("Invalid input. Please enter a number.", "error")
    return render_template("withdraw.html")


if __name__ == "__main__":
    app.run(debug=True)
