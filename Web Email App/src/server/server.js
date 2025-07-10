const express = require('express');
const bodyParser = require('body-parser');
const emailService = require('./emailService');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, '../..')));

// Routes
app.post('/submit', (req, res) => {
    const userInput = req.body.input;

    // Here you would fill out your template with the user input
    const filledTemplate = fillTemplate(userInput);

    // Send the filled template via email
    emailService.sendEmail(filledTemplate)
        .then(() => {
            res.status(200).send('Email sent successfully!');
        })
        .catch((error) => {
            console.error('Error sending email:', error);
            res.status(500).send('Error sending email.');
        });
});

// Function to fill the template with user input
function fillTemplate(input) {
    // Load your template and replace placeholders with user input
    // For simplicity, let's assume template1.html has a placeholder {{input}}
    const templatePath = path.join(__dirname, '../templates/template1.html');
    let template = fs.readFileSync(templatePath, 'utf8');
    return template.replace('{{input}}', input);
}

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});