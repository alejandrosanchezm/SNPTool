from app import app

"""
Se encarga de ejecutar la aplicación de Flask.
"""

if __name__ == "__main__":
    app.run(host="192.168.1.67", debug=True)