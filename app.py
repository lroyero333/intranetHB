from main.run import app
# Import the 'app' variable from the 'run' module of the 'main' package
if __name__ == '__main__':
    # Check if the file is being executed directly as a script
    app.run(port=443)
    # Run the Flask application on port 80
