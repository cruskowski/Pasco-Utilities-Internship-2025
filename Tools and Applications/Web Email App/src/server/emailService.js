const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');

const transporter = nodemailer.createTransport({
    service: 'gmail', // Use your email service
    auth: {
        user: 'your-email@gmail.com', // Your email
        pass: 'your-email-password' // Your email password or app password
    }
});

const sendEmail = (to, subject, templateData) => {
    const templatePath = path.join(__dirname, '../templates/template1.html');
    
    fs.readFile(templatePath, 'utf8', (err, template) => {
        if (err) {
            console.error('Error reading template:', err);
            return;
        }

        // Fill the template with the provided data
        const filledTemplate = fillTemplate(template, templateData);

        const mailOptions = {
            from: 'your-email@gmail.com',
            to: to,
            subject: subject,
            html: filledTemplate
        };

        transporter.sendMail(mailOptions, (error, info) => {
            if (error) {
                return console.log('Error sending email:', error);
            }
            console.log('Email sent:', info.response);
        });
    });
};

const fillTemplate = (template, data) => {
    // Replace placeholders in the template with actual data
    return template.replace(/{{(\w+)}}/g, (match, key) => data[key] || '');
};

module.exports = {
    sendEmail
};