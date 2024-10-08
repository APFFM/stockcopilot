# AI-Powered Stock Analysis Dashboard

This is my first public project which is an AI-powered (Claude API) stock analysis dashboard that provides real-time stock data, technical analysis, and AI-generated insights.

## Features

- Real-time stock data visualization
- Technical analysis charts (price, returns, volume)
- AI-powered stock analysis
- Interactive chat for stock-related questions

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/APFFM/ai-stock-analysis.git
    cd ai-stock-analysis
    ```

2. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

3. Set up environment variables:
    Create a `.env` file in the root directory and add your Anthropic API key:

    ```sh
    echo "ANT=your_anthropic_api_key" > .env
    ```

4. Run the application:

    ```sh
    python app2.py
    ```

5. Open a web browser and navigate to `http://localhost:8050`

## Usage

1. Enter a stock ticker (e.g., AAPL for Apple Inc.) in the input field.
2. Select a time period from the dropdown menu.
3. Click "Fetch Data" to retrieve and display the stock analysis.
4. Use the chat feature to ask specific questions about the stock.

## Screenshots

Here are some screenshots of the AI-powered stock analysis dashboard:

![Screenshot 1](screenshots/Screen1.PNG)
![Screenshot 2](screenshots/Screen2.PNG)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)


## Created by Alex Proschkin
