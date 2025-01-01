# Globle Bot

Globle Bot is a Flask-based web application that allows users to play a geography-based game, guessing countries based on distance and direction clues.

## Features

- **Interactive Gameplay:** Users can input their guesses and receive suggestions based on geographical data.
- **Geospatial Calculations:** Utilizes GeoPandas and Shapely for accurate distance and direction computations.
- **Responsive Design:** Built with Bootstrap to ensure compatibility across devices.
- **Ready for Deployment:** Configured for easy deployment on platforms like Render.

## Project Structure

GlobleBot/ ├── app.py ├── requirements.txt ├── Procfile ├── .gitignore ├── README.md └── templates/ └── index.html


## Setup and Installation

### Prerequisites

- **Python 3.8+**
- **pip** (Python package installer)

### Installation Steps

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/GlobleBot.git
    cd GlobleBot
    ```

2. **Create a Virtual Environment:**

    ```bash
    python -m venv venv
    ```

3. **Activate the Virtual Environment:**

    - **Windows:**

        ```bash
        venv\Scripts\activate
        ```

    - **macOS/Linux:**

        ```bash
        source venv/bin/activate
        ```

4. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Set Environment Variables:**

    Create a `.env` file in the project root and add your secret key:

    ```env
    SECRET_KEY=your-secret-key
    ```

6. **Run the Application Locally:**

    ```bash
    python app.py
    ```

    The app will be accessible at `http://localhost:5000`.

## Deployment on Render

1. **Create a New Repository on GitHub:**

    - Go to [GitHub](https://github.com/) and create a new repository named `GlobleBot`.

2. **Initialize Git and Push to GitHub:**

    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    git remote add origin https://github.com/yourusername/GlobleBot.git
    git push -u origin main
    ```

3. **Deploy to Render:**

    - Log in to [Render](https://render.com/) and create a new Web Service.
    - Connect your GitHub repository (`GlobleBot`).
    - Set the environment variables in Render (e.g., `SECRET_KEY`).
    - Render will automatically detect the `Procfile` and deploy your application.

## Usage

1. **Access the Application:**

    Navigate to your Render-provided URL.

2. **Start Playing:**

    - Enter your first guess country.
    - Provide distance and direction clues based on the suggestions.
    - Continue until you reach your target country or need to reset the game.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [GeoPandas](https://geopandas.org/)
- [Shapely](https://shapely.readthedocs.io/)
- [Bootstrap](https://getbootstrap.com/)
