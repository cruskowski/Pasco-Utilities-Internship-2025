document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('inputForm');
    const inputField = document.getElementById('userInput');
    
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        const userInput = inputField.value;
        
        try {
            const response = await fetch('/api/send-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: userInput }),
            });
            
            if (response.ok) {
                const result = await response.json();
                alert('Email sent successfully: ' + result.message);
            } else {
                alert('Error sending email: ' + response.statusText);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while sending the email.');
        }
    });
});