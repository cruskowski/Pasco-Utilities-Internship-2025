# Web Template Email App

This project is a web application that allows users to input numbers and characters into a form, which then fills out predefined templates and sends them via email.

## Project Structure

```
web-template-email-app
├── src
│   ├── index.html          # HTML structure of the web page
│   ├── styles
│   │   └── main.css       # CSS styles for the web page
│   ├── scripts
│   │   └── main.js        # JavaScript code for handling user input and submission
│   ├── templates
│   │   └── template1.html  # HTML template to be filled and sent
│   └── server
│       ├── server.js      # Express server setup
│       └── emailService.js # Logic for sending emails
├── package.json            # npm configuration file
└── README.md               # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd web-template-email-app
   ```

2. **Install dependencies:**
   ```
   npm install
   ```

3. **Run the server:**
   ```
   node src/server/server.js
   ```

4. **Open your browser and navigate to:**
   ```
   http://localhost:3000
   ```

## Usage

- Enter the desired numbers and characters into the input box.
- Click the submit button to send the data.
- The application will fill out the template with the provided input and send it to the specified email address.

## Dependencies

- Express: A web framework for Node.js.
- Nodemailer: A module for sending emails from Node.js applications.

## License

This project is licensed under the MIT License.